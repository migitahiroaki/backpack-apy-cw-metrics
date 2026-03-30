#!/usr/bin/env bash
set -euo pipefail

# このスクリプトはプロジェクトルートで実行します
ZIP_FILE="lambda-deployment.zip"
SOURCE_DIR="src"
EXCLUDE_PATTERN="*/__pycache__/*"

if [[ -f "$ZIP_FILE" ]]; then
  echo "既存の $ZIP_FILE を削除します。"
  rm -f "$ZIP_FILE"
fi

echo "$SOURCE_DIR を $ZIP_FILE に圧縮しています（$EXCLUDE_PATTERN を除外）..."
zip -r "$ZIP_FILE" "$SOURCE_DIR" -x "$EXCLUDE_PATTERN"

echo "完了: $ZIP_FILE"
