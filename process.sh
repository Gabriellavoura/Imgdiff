#!/bin/bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Uso: $0 arquivo1.pdf arquivo2.pdf [diretorio_saida]"
  exit 1
fi

PDF1="$1"
PDF2="$2"
OUT="${3:-diff_out}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$OUT"

echo "[1/4] Rasterizando PDFs (300 DPI, grayscale)..."
convert -density 300 "$PDF1" -alpha off -colorspace Gray "$OUT/pageA_%03d.png"
convert -density 300 "$PDF2" -alpha off -colorspace Gray "$OUT/pageB_%03d.png"

echo "[2/4] Alinhando páginas com OpenCV (ECC)..."
python3 "$SCRIPT_DIR/pdf_diff_align.py" "$OUT"

echo "[3/4] Gerando diffs com ImageMagick..."
total_sim=0
count=0

for a in "$OUT"/a_*_bin.png; do
  idx=$(basename "$a" .png | cut -d'_' -f2)
  b="$OUT/b_${idx}_aligned.png"
  diff="$OUT/diff_${idx}_magick.png"
  if [ -f "$b" ]; then
    echo "   → Diferença página $idx"

    diff_pixels=$(compare -metric AE "$a" "$b" null: 2>&1 || echo "0")

    if [[ "$diff_pixels" =~ ^[0-9]+$ ]]; then
      total_pixels=$(identify -format "%[fx:w*h]" "$a" 2>/dev/null || echo "0")
      if [ "$total_pixels" -gt 0 ]; then
        similarity=$(awk -v d="$diff_pixels" -v t="$total_pixels" 'BEGIN { printf "%.2f", 100*(1 - d/t) }')
      else
        similarity="0.00"
      fi
    else
      similarity="0.00"
    fi

    echo "      Similaridade: $similarity%"

    total_sim=$(awk -v a="$total_sim" -v s="$similarity" 'BEGIN { printf "%.2f", a + s }')
    count=$((count + 1))

    compare -fuzz 30% -metric AE -highlight-color Red -lowlight-color White -compose src "$a" "$b" "$diff" 2>/dev/null || true

    filtered="$OUT/diff_${idx}_filtered.png"

    convert "$diff" \
      -colorspace RGB -channel R -separate +channel \
      -blur 0x2 \
      "$OUT/tmp_mask.png"

    convert "$OUT/tmp_mask.png" \
      -morphology Erode Diamond \
      -morphology Erode Square \
      -morphology Close Diamond \
      -morphology Open Diamond \
      -blur 0x2 \
      -despeckle \
      -threshold 15% \
      "$OUT/tmp_clean_mask.png"

    convert "$diff" "$OUT/tmp_clean_mask.png" \
      -compose Multiply -composite \
      -morphology Dilate Diamond \
      "$filtered"

    rm -f "$OUT/tmp_mask.png" "$OUT/tmp_clean_mask.png"

    echo "      → Diff filtrado salvo em: $filtered"
    echo
  fi
done

if [ "$count" -gt 0 ]; then
  avg_sim=$(awk -v t="$total_sim" -v c="$count" 'BEGIN { printf "%.2f", t / c }')
  echo "[4/4] Concluído!"
  echo "Média geral de similaridade: $avg_sim%"
else
  echo "[4/4] Nenhuma página processada!"
fi

echo "Resultados em: $OUT"
