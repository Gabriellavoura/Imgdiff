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