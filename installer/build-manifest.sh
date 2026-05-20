#!/usr/bin/env bash
# Generate installer/manifest.xml with the production host URL.
# Usage: ./build-manifest.sh <host>      # host without protocol, e.g.
#        ./build-manifest.sh elom-max.github.io/augustine-citator
set -euo pipefail

HOST="${1:-}"
if [ -z "$HOST" ]; then
  echo "Usage: $0 <host>" >&2
  echo "Example: $0 elom-max.github.io/augustine-citator" >&2
  exit 1
fi

cd "$(dirname "$0")"
sed "s|YOUR-DOMAIN.example|${HOST}|g" ../manifest.xml > manifest.xml
echo "Wrote installer/manifest.xml with host: https://${HOST}"
