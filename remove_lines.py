import cv2
import numpy as np
import sys, os


if len(sys.argv) < 3:
    print("Uso: remove_lines.py <input> <output>")
    sys.exit(1)

inp, out = sys.argv[1], sys.argv[2]
img = cv2.imread(inp, cv2.IMREAD_GRAYSCALE)
if img is None:
    print(f"Erro: não foi possível ler {inp}")
    sys.exit(1)

img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
_, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (80, 2))
v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 80))

detect_h = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel)
detect_v = cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_kernel)
lines = cv2.bitwise_or(detect_h, detect_v)
