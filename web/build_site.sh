#!/usr/bin/env bash
# Builds a standalone copy of the "A Thing About The Thing" site into web/dist/.
# web/index.html stays the source (it is also published as a claude.ai artifact, which adds
# its own document skeleton); this script adds the skeleton a normal web host needs, in two
# entry points that differ only in language and link preview:
#   index.html  English card (og-en.jpg), language from the browser
#   sk.html     Slovak card (og-sk.jpg), opens in Slovak — share https://<host>/sk
#   BASE_URL=https://example.org/ ./build_site.sh   # absolute URLs for link previews
# The preview cards come from make_og.py.
set -euo pipefail
cd "$(dirname "$0")"
BASE_URL=${BASE_URL:-}
rm -rf dist && mkdir -p dist/img
cp data.json events.json favicon.svg og-en.jpg og-sk.jpg dist/
cp img/*.jpg dist/img/

desc_en="MacReady, or Childs? A frame-by-frame investigation of John Carpenter's film: the rules, who was where, the clues and the verdict. In English and Slovak."
desc_sk="MacReady, alebo Childs? Rozbor Carpenterovho filmu snímku po snímke: pravidlá, kto bol kde, stopy a verdikt. Po slovensky aj po anglicky."
base=${BASE_URL%/}

page() {  # lang path title description locale alt_locale image_alt
  local lang=$1 path=$2 title=$3 desc=$4 locale=$5 alt=$6 img_alt=$7
  local url="${base:+$base/}${path}" img="${base:+$base/}og-${lang}.jpg"
  local force=""; [[ $lang == sk ]] && force=' data-force-lang="sk"'
  cat <<EOF
<!doctype html>
<html lang="${lang}"${force}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#04070c">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="A Thing About The Thing">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${desc}">
<meta property="og:image" content="${img}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${img_alt}">
<meta property="og:locale" content="${locale}">
<meta property="og:locale:alternate" content="${alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${title}">
<meta name="twitter:description" content="${desc}">
<meta name="twitter:image" content="${img}">
EOF
  if [[ -n $base ]]; then
    printf '<meta property="og:url" content="%s">\n<link rel="canonical" href="%s">\n' "$url" "$url"
    printf '<link rel="alternate" hreflang="en" href="%s/">\n<link rel="alternate" hreflang="sk" href="%s/sk">\n' "$base" "$base"
  fi
  # the fragment's own description is English; the Slovak page gets its own
  grep -v 'name="claude:' index.html | sed "s|<meta name=\"description\" content=\"[^\"]*\">|<meta name=\"description\" content=\"${desc//&/\\&}\">|"
  printf '</html>\n'
}

page en "" "The Thing (1982): who is human at the end?" "$desc_en" en_US sk_SK \
  "MacReady and Childs, the two survivors of The Thing, on either side of the title" > dist/index.html
page sk "sk" "Vec (1982): kto je na konci človek?" "$desc_sk" sk_SK en_US \
  "MacReady a Childs, dvaja preživší z filmu Vec, po stranách názvu" > dist/sk.html
echo "dist: $(du -sh dist | cut -f1), $(ls dist/img | wc -l) images, pages: $(cd dist && ls *.html | tr '\n' ' ')"
