from PIL import Image
import pytesseract

im = Image.open("Irregularis_sampletext.png")

text = pytesseract.image_to_string(im, lang = 'eng')

print(text)
print("test")
