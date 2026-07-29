from paddleocr import PaddleOCR

# Initialize model
ocr_english = PaddleOCR(use_angle_cls=False, lang='en')

print("\n--- EXTRACTING LEGAL TEXT ---")
result = ocr_english.ocr('challan.jpg')

# The new PaddleX backend returns a list containing a dictionary. 
# We just need to grab the 'rec_texts' list out of it!
if result and len(result) > 0:
    extracted_sentences = result[0].get('rec_texts', [])
    
    for sentence in extracted_sentences:
        print(sentence)
else:
    print("No text found.")