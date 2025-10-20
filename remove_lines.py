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

contours, _ = cv2.findContours(lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
mask_lines = np.zeros_like(lines)
for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    aspect = max(w, h) / float(min(w, h) + 1)
    area = cv2.contourArea(c)
    if aspect > 12 and 30 < area < 0.02 * binary.size:
        cv2.drawContours(mask_lines, [c], -1, 255, -1)

mask_inv = cv2.bitwise_not(mask_lines)
clean = cv2.bitwise_and(binary, mask_inv)