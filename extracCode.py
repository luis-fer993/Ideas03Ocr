
import cv2
import pytesseract
import re
from PIL import Image


def preprocess_image(image_path):
    # Load the image using OpenCV
    image = cv2.imread(image_path)
    #image= cv2.resize(image, (800, 500))

    # Convert the image to grayscale
    #gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to enhance the text
    #_, threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return image#threshold_image


def perform_ocr(image):
    # Use pytesseract to extract text from the image
    extracted_text = pytesseract.image_to_string(image)

    return extracted_text

# Filter numbers that start with 1 using regular expressions
def filter(text):
    numbers = re.findall(r'\b3', text)
    return numbers

def show_result(image, extracted_text, delay:int):
    # Display the image with the extracted text
    #image= cv2.resize(image, (400, 200))
    cv2.imshow("Image", image)
    #filtered_numbers = filter(extracted_text)
    print("Extracted Code:\n", extracted_text)
    cv2.waitKey(delay)
    cv2.destroyAllWindows()


# Replace 'path_to_your_image' with the actual path to your image file
image_path = 'img/qrNumbersRotated.png'
    
    # Preprocess the image
preprocessed_image = preprocess_image(image_path)
    
    # Perform OCR
extracted_text = perform_ocr(preprocessed_image)
    
    # Show the result
show_result(preprocessed_image, extracted_text)

