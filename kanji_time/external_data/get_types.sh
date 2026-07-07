#!/usr/bin/env bash
set -euo pipefail

zipfile="${1:?usage: $0 path/to/archive.zip}"

# Enumerate *all* XML files at any depth in the ZIP,
# stream their contents, and extract distinct type= attributes.
unzip -Z1 "$zipfile" \
  | awk 'tolower($0) ~ /\.svg$/ {print}' \
  | while IFS= read -r member; do
      unzip -p "$zipfile" "$member" || true
      printf '\n'
    done \
  | perl -ne '
      # Match type="..." or type='\''...'\'', anywhere
      while (/\btype\s*=\s*(["'\''])(.*?)\1/g) {
        print "$2\n";
      }
    ' \
  | awk 'NF' \
  | LC_ALL=C sort -u

