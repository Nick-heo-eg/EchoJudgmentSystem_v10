#!/usr/bin/env bash
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "Usage: $0 ARTIFACTS_DIR [S3_URI]" >&2
  exit 2
fi
ART_DIR="$1"
S3_URI="${2:-$S3_URI:-}"
if [ -z "${S3_URI}" ]; then
  echo "S3_URI not provided; set arg2 or env S3_URI" >&2
  exit 3
fi
aws s3 cp --recursive "$ART_DIR" "$S3_URI"
