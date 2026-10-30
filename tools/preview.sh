#!/bin/zsh
# Renders figures to PNG with headless Chrome (close to how GitHub shows them).
#   tools/preview.sh OUTDIR figures/NN-*.svg ...
set -euo pipefail
out=$1; shift
mkdir -p $out
chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for f in "$@"; do
  read w h < <(python3 -c "import re,sys;s=open(sys.argv[1]).read(500);m=re.search(r'viewBox=\"0 0 (\d+) (\d+)\"',s);print(m[1],m[2])" $f)
  "$chrome" --headless=new --disable-gpu --hide-scrollbars --screenshot=$out/${f:t:r}.png --window-size=$w,$h "file://${f:A}" >/dev/null 2>&1
  sips -Z 1300 $out/${f:t:r}.png >/dev/null
done
