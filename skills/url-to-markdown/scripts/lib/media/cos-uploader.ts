import { createReadStream } from "node:fs";
import { readdir, rm, rmdir, stat } from "node:fs/promises";
import path from "node:path";
import COS from "cos-nodejs-sdk-v5";
import type { Logger } from "../utils/logger";
import { sanitizeFileSegment } from "./media-utils";
import type { MediaReplacement } from "./types";

export type CosObjectAcl = "default" | "private" | "public-read" | "public-read-write";

export interface CosConfig {
  secretId: string;
  secretKey: string;
  bucket: string;
  region: string;
  prefix: string;
  acl: CosObjectAcl;
  baseUrl?: string;
}

const EXT_CONTENT_TYPE: Record<string, string> = {
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  png: "image/png",
  webp: "image/webp",
  gif: "image/gif",
  bmp: "image/bmp",
  avif: "image/avif",
  svg: "image/svg+xml",
  heic: "image/heic",
  heif: "image/heif",
  mp4: "video/mp4",
  webm: "video/webm",
  mov: "video/quicktime",
  m4v: "video/x-m4v",
  mkv: "video/x-matroska",
};

/**
 * Read Tencent Cloud COS configuration from environment variables.
 * Returns null when any required variable is missing.
 *
 * Required: COS_SECRET_ID, COS_SECRET_KEY, COS_BUCKET, COS_REGION
 * Optional: COS_PREFIX (key prefix, default "url-to-markdown"),
 *           COS_ACL (object ACL, default "public-read"),
 *           COS_BASE_URL (custom CDN domain; otherwise the default COS domain is used)
 */
export function readCosConfigFromEnv(env: NodeJS.ProcessEnv = process.env): CosConfig | null {
  const secretId = env.COS_SECRET_ID?.trim();
  const secretKey = env.COS_SECRET_KEY?.trim();
  const bucket = env.COS_BUCKET?.trim();
  const region = env.COS_REGION?.trim();
  if (!secretId || !secretKey || !bucket || !region) {
    return null;
  }

  const prefix = env.COS_PREFIX?.trim().replace(/^\/+|\/+$/g, "") || "url-to-markdown";
  const acl = readCosObjectAcl(env.COS_ACL);
  const baseUrl = env.COS_BASE_URL?.trim().replace(/\/+$/, "");

  return { secretId, secretKey, bucket, region, prefix, acl, baseUrl: baseUrl || undefined };
}

function readCosObjectAcl(raw: string | undefined): CosObjectAcl {
  const value = raw?.trim();
  if (!value) {
    return "public-read";
  }
  if (value === "default" || value === "private" || value === "public-read" || value === "public-read-write") {
    return value;
  }
  throw new Error("COS_ACL must be one of: default, private, public-read, public-read-write");
}

function contentTypeForFile(filePath: string): string | undefined {
  const ext = path.extname(filePath).replace(/^\./, "").toLowerCase();
  return EXT_CONTENT_TYPE[ext];
}

function buildObjectUrl(config: CosConfig, key: string): string {
  const encodedKey = key.split("/").map(encodeURIComponent).join("/");
  if (config.baseUrl) {
    return `${config.baseUrl}/${encodedKey}`;
  }
  return `https://${config.bucket}.cos.${config.region}.myqcloud.com/${encodedKey}`;
}

function outputNamespace(outputPath: string): string {
  const absoluteOutputPath = path.resolve(outputPath);
  const fileStem = sanitizeFileSegment(path.parse(absoluteOutputPath).name);
  const parentStem = sanitizeFileSegment(path.basename(path.dirname(absoluteOutputPath)));
  if (parentStem && parentStem === fileStem) {
    return parentStem;
  }
  return fileStem || parentStem || "article";
}

function deriveObjectKey(prefix: string, outputPath: string, replacement: MediaReplacement): string {
  const filename = path.basename(replacement.absolutePath);
  const kindDir = replacement.kind === "video" ? "videos" : "imgs";
  return [prefix, outputNamespace(outputPath), kindDir, filename]
    .filter((segment) => Boolean(segment) && segment !== "." && segment !== path.sep)
    .join("/");
}

async function removeLocalFiles(files: string[], log: Logger): Promise<void> {
  const dirs = new Set<string>();
  for (const file of files) {
    try {
      await rm(file, { force: true });
      dirs.add(path.dirname(file));
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      log.debug(`Could not remove local file ${file}: ${message}`);
    }
  }
  for (const dir of dirs) {
    try {
      const entries = await readdir(dir);
      if (entries.length === 0) {
        await rmdir(dir);
      }
    } catch {
      // Directory still has files or is already gone; leave it alone.
    }
  }
}

/**
 * Upload already-downloaded media files to Tencent Cloud COS.
 * Returns replacements whose `localPath` points at the COS URL so the
 * markdown rewriter swaps original URLs for COS URLs.
 *
 * Successfully uploaded local files are deleted. Failed uploads keep their
 * local file and fall back to the original local replacement.
 */
export async function uploadReplacementsToCos(
  replacements: MediaReplacement[],
  config: CosConfig,
  outputPath: string,
  log: Logger,
): Promise<MediaReplacement[]> {
  if (replacements.length === 0) {
    return replacements;
  }

  const cos = new COS({ SecretId: config.secretId, SecretKey: config.secretKey });
  const result: MediaReplacement[] = [];
  const uploadedFiles: string[] = [];

  for (const item of replacements) {
    try {
      const fileStat = await stat(item.absolutePath);
      const key = deriveObjectKey(config.prefix, outputPath, item);
      await new Promise<void>((resolve, reject) => {
        const body = createReadStream(item.absolutePath);
        cos.putObject(
          {
            Bucket: config.bucket,
            Region: config.region,
            Key: key,
            Body: body,
            ContentLength: fileStat.size,
            ContentType: contentTypeForFile(item.absolutePath),
            ...(config.acl === "default" ? {} : { ACL: config.acl }),
          },
          (error) => (error ? reject(error) : resolve()),
        );
      });
      const cosUrl = buildObjectUrl(config, key);
      result.push({ ...item, localPath: cosUrl });
      uploadedFiles.push(item.absolutePath);
      log.info(`Uploaded to COS: ${key}`);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      log.warn(`Failed to upload ${item.absolutePath} to COS: ${message}`);
      result.push(item);
    }
  }

  await removeLocalFiles(uploadedFiles, log);
  return result;
}
