#!/usr/bin/env bash
# Builds a standalone copy of the "A Thing About The Thing" site into web/dist/.
# web/index.html stays the source (it is also published as a claude.ai artifact, which adds
# its own document skeleton); this script adds the skeleton a normal web host needs.
#   BASE_URL=https://example.org/ ./build_site.sh   # absolute URLs for social previews (optional)
set -euo pipefail
cd "$(dirname "$0")"
BASE_URL=${BASE_URL:-}
rm -rf dist && mkdir -p dist/img
cp data.json events.json dist/
cp img/*.jpg dist/img/
cp favicon.svg og.jpg dist/

og_img=og.jpg; [[ -n $BASE_URL ]] && og_img="${BASE_URL%/}/og.jpg"
desc=$(sed -n 's/.*<meta name="description" content="\([^"]*\)".*/\1/p' index.html | head -1)
{
  cat <<EOF
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#04070c">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:title" content="A Thing About The Thing">
<meta property="og:description" content="${desc}">
<meta property="og:image" content="${og_img}">
<meta name="twitter:card" content="summary_large_image">
EOF
  [[ -n $BASE_URL ]] && printf '<meta property="og:url" content="%s">\n<link rel="canonical" href="%s">\n' "$BASE_URL" "$BASE_URL"
  grep -v 'name="claude:' index.html
  printf '</html>\n'
} > dist/index.html
echo "dist: $(du -sh dist | cut -f1), $(ls dist/img | wc -l) images"
