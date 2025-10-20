import cv2
import numpy as np
import os
import sys

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
    
def main():
    if len(sys.argv) < 2:
        print("Uso: pdf_diff_align.py <diretorio_com_paginas>")
        sys.exit(1)

    OUTDIR = os.path.abspath(sys.argv[1])
    print(f"[INFO] Diretório de trabalho: {OUTDIR}")

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
            print(f"   ↳ Correlação ECC: {cc:.5f}")
            return warp
        except cv2.error as e:
            print(f"   ⚠️ Falha ECC: {e}")
            return None


if __name__ == "__main__":
    preprocess(sys.argv[1])

