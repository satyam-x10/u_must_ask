import sys
import os
import rembg
import cv2
import numpy as np

print(f"Python: {sys.executable}")
print(f"rembg: {rembg.__file__}")
print(f"OpenCV Version: {cv2.__version__}")
print(f"OpenCV File: {cv2.__file__}")

try:
    print("Attempting to open window...")
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imshow("Test Window", img)
    cv2.waitKey(100)
    cv2.destroyAllWindows()
    print("SUCCESS: cv2.imshow passed!")
except Exception as e:
    print(f"FAILURE: cv2.imshow failed: {e}")
