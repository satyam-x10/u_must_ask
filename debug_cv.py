import cv2
import sys
import os

print(f"OpenCV Version: {cv2.__version__}")
print(f"OpenCV File: {cv2.__file__}")
try:
    print(cv2.getBuildInformation())
except Exception as e:
    print(f"Could not get build info: {e}")

try:
    cv2.imshow("Test", cv2.imread(sys.argv[0])) # Try to show this file as image (will fail decode but window might open) or just dummy
    cv2.destroyAllWindows()
    print("imshow seems available (no error thrown instantly)")
except cv2.error as e:
    print(f"imshow failed: {e}")
except Exception as e:
    print(f"imshow failed with general error: {e}")
