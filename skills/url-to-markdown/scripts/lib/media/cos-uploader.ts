import { readFile, readdir, rm, rmdir } from "node:fs/promises";
import path from "node:path";
import COS from "cos-nodejs-sdk-v5";
import type { Logger } from "../utils/logger";
import type { MediaReplacement } from "./types";

export interface CosConfig {
  secretId: string;
  secretKey: string;
  bucket: string;
  region: string;
  prefix: string;
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

  const prefix = (env.COS_PREFIX ?? "url-to-markdown").trim().replace(/^\/+|\/+$/g, "");
  const baseUrl = env.COS_BASE_URL?.trim().replace(/\/+$/, "");

  return { secretId, secretKey, bucket, region, prefix, baseUrl: baseUrl || undefined };
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

/**
 * Derive a COS object key from a downloaded file's absolute path.
 * Downloaded media lives at `{base}/{slug}/{imgs|videos}/{filename}`,
 * so the key keeps the slug + kind directory as a namespace to avoid collisions.
 */
function deriveObjectKey(prefix: string, absolutePath: string): string {
  const filename = path.basename(absolutePath);
  const kindDir = path.basename(path.dirname(absolutePath));
  const slugDir = path.basename(path.dirname(path.dirname(absolutePath)));
  return [prefix, slugDir, kindDir, filename]
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
      const body = await readFile(item.absolutePath);
      const key = deriveObjectKey(config.prefix, item.absolutePath);
      await new Promise<void>((resolve, reject) => {
        cos.putObject(
          {
            Bucket: config.bucket,
            Region: config.region,
            Key: key,
            Body: body,
            ContentType: contentTypeForFile(item.absolutePath),
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
