#!/bin/bash
#
# TDL Download Helper Script
# Simplifies common tdl download operations
#

set -e

# Default values
DOWNLOAD_DIR="${TDL_DOWNLOAD_DIR:-$HOME/Downloads/telegram}"
FILE_TYPES="jpg,jpeg,png,gif,webp,mp4,mov,mkv,avi,webm"
NAMESPACE="default"

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] <telegram-message-url>

Download media files from Telegram using tdl

Options:
    -d DIR      Download directory (default: $DOWNLOAD_DIR)
    -t TYPES    File types to download (default: $FILE_TYPES)
    -n NS       Namespace for session (default: $NAMESPACE)
    -i          Interactive mode - choose file types interactively
    -h          Show this help

Examples:
    $(basename "$0") https://t.me/c/xxxxx/123
    $(basename "$0") -d ~/Desktop/photos -t jpg,png <url>
    $(basename "$0") -n work <url>

EOF
}

# Parse arguments
INTERACTIVE=false
while getopts "d:t:n:ih" opt; do
    case $opt in
        d) DOWNLOAD_DIR="$OPTARG" ;;
        t) FILE_TYPES="$OPTARG" ;;
        n) NAMESPACE="$OPTARG" ;;
        i) INTERACTIVE=true ;;
        h) usage; exit 0 ;;
        *) usage; exit 1 ;;
    esac
done

shift $((OPTIND-1))

# Check for URL argument
if [ $# -eq 0 ]; then
    echo "Error: Telegram message URL required"
    usage
    exit 1
fi

URL="$1"

# Check if tdl is installed
if ! command -v tdl &> /dev/null; then
    echo "Error: tdl not found. Please install tdl first."
    echo "Visit: https://github.com/iyear/tdl"
    exit 1
fi

# Interactive mode
if [ "$INTERACTIVE" = true ]; then
    echo "Select file types to download:"
    echo "1) Images only (jpg,jpeg,png,gif,webp)"
    echo "2) Videos only (mp4,mov,mkv,avi,webm)"
    echo "3) Images + Videos"
    echo "4) Custom"
    read -rp "Choice [1-4]: " choice
    
    case $choice in
        1) FILE_TYPES="jpg,jpeg,png,gif,webp" ;;
        2) FILE_TYPES="mp4,mov,mkv,avi,webm" ;;
        3) FILE_TYPES="jpg,jpeg,png,gif,webp,mp4,mov,mkv,avi,webm" ;;
        4) read -rp "Enter file types (comma-separated): " FILE_TYPES ;;
        *) echo "Invalid choice"; exit 1 ;;
    esac
fi

# Create download directory if it doesn't exist
mkdir -p "$DOWNLOAD_DIR"

echo "=== TDL Download ==="
echo "URL: $URL"
echo "Directory: $DOWNLOAD_DIR"
echo "File types: $FILE_TYPES"
echo "Namespace: $NAMESPACE"
echo ""

# Run tdl download
tdl download \
    -u "$URL" \
    -d "$DOWNLOAD_DIR" \
    -i "$FILE_TYPES" \
    -n "$NAMESPACE"

echo ""
echo "Download complete. Files saved to: $DOWNLOAD_DIR"
