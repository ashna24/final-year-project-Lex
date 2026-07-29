import cv2
import easyocr

img = cv2.imread('contract_clean.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
cv2.imwrite('processed.jpg', thresh)

reader = easyocr.Reader(['en', 'ur'])
result = reader.readtext('processed.jpg', detail=0)

print("=== OCR OUTPUT ===")
for line in result:
    print(line)