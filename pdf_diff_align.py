import cv2
import numpy as np
import os
import sys

    
if len(sys.argv) < 2:
    print("Uso: pdf_diff_align.py <diretorio_com_paginas>")
    sys.exit(1)

OUTDIR = os.path.abspath(sys.argv[1])
print(f"Diretório de trabalho: {OUTDIR}")

def preprocess(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Falha ao ler imagem: {path}")
    blur = cv2.GaussianBlur(img, (3, 3), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th

def align_ecc(a, b):
    warp = np.eye(2, 3, dtype=np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 1000, 1e-6)
    try:
        cc, warp = cv2.findTransformECC(a, b, warp, cv2.MOTION_AFFINE, criteria)
        print(f"Correlação ECC: {cc:.5f}")
        return warp
    except cv2.error as e:
        print(f"Falha ECC: {e}")
        return None
    
pagesA = sorted(f for f in os.listdir(OUTDIR) if f.startswith("pageA_"))
pagesB = sorted(f for f in os.listdir(OUTDIR) if f.startswith("pageB_"))

if not pagesA or not pagesB:
    print("Nenhuma imagem encontrada")
    sys.exit(1)

for fA, fB in zip(pagesA, pagesB):
    idx = fA.split("_")[1].split(".")[0]
    pA = os.path.join(OUTDIR, fA)
    pB = os.path.join(OUTDIR, fB)

    print(f"Processando página {idx}")
    a = preprocess(pA)
    b = preprocess(pB)

    warp = align_ecc(a, b)
    if warp is not None:
        b_aligned = cv2.warpAffine(
            b, warp, (a.shape[1], a.shape[0]),
            flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
            borderMode=cv2.BORDER_CONSTANT, borderValue=255,
        )
else:
    b_aligned = b.copy()

cv2.imwrite(os.path.join(OUTDIR, f"a_{idx}_bin.png"), a)
cv2.imwrite(os.path.join(OUTDIR, f"b_{idx}_aligned.png"), b_aligned)

print("Alinhamento concluído. Pronto para diff com ImageMagick.")

