from openai import OpenAI
import os
import pytesseract
from PIL import Image
import pandas as pd

# Set your OpenAI API key
API_KEY = os.environ['apiKey']
client = OpenAI(api_key=API_KEY)

grade = 3
# Directory containing images
levelName = f'G{grade}-sample'
image_dir = f'images/{levelName}'
output_csv_dir = f'csv/{levelName}'

# Ensure the output directory exists
os.makedirs(output_csv_dir, exist_ok=True)

# Function to extract text from an image using OCR
def ocr_image(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)


# 24.11.05 추출도 sequence 필요.

# Function to use OpenAI API to format text into structured data
# TEXT 형태로 먼저 추출 후 전달하는 함수
def extract_data_with_openai(text):
  
    prompt = f"""Extract the following details from the provided text:
    
    - typeOfTestAndNumber: Located at the top of the page and will be either "Level Test N" or "Cumulative Test N." N stands for the number stated at the image. not literally "N".
    - pageNum: Numeric value located at the bottom of the page near the text "Wordly Wise 3000 Test Booklet {grade}" indicating the page of the image
    - sequence : Number value of the numbered sentences.
    - questionText: This refers to the numbered sentences in the test.
    - options: The 3-4 phrases listed under each question, marked with circled letters. Each option should be separeted with ||. Leave out the circled letters.
    
    Text:
    {text}
    
    Format the output as a CSV with the following columns: typeOfTestAndNumber, pageNum, sequence, questionText, options.
    Leave out the triple backticks in the beginning and the end of the answer and csv prefix.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
          {
            "role": "user",
            "content": [
               {
                  "type":"text",
                  "text": prompt
               }
            ]
          }
        ],
        # max_tokens = 4096 # gpt-4o model's max  
      )

    return response.choices[0].message.content.strip()

def extract_data_from_image_with_openai(image_path):
  
    prompt = f"""Extract the following details from the provided image:
    
    - typeOfTestAndNumber: Located at the top of the page and will be either "Level Test N" or "Cumulative Test N." N stands for the number stated at the image. not literally "N".
    - pageNum: Numeric value located at the bottom of the page near the text "Wordly Wise 3000 Test Booklet {grade}" indicating the page of the image
    - sequence : Number value of the numbered sentences.
    - questionText: This refers to the numbered sentences in the test.
    - options: The 3-4 phrases listed under each question, marked with circled letters. Each option should be separeted with ||. Leave out the circled letters.
    
    Format the output as a CSV with the following columns: typeOfTestAndNumber, pageNum, sequence, questionText, options.
    Leave out the triple backticks in the beginning and the end of the answer and csv prefix.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
          {
            "role": "user",
            "content": [
               {
                  "type":"text",
                  "text": prompt
               },
               {
                  "type":"image_url",
                  "image_url":{"url":image_path}
               }
            ]
          }
        ],
        # max_tokens = 4096 # gpt-4o model's max  
      )

    return response.choices[0].message.content.strip()

# Process all images in the specified directory
all_data = []
for filename in sorted(os.listdir(image_dir)):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):

      image_path = os.path.join(image_dir, filename)
      # Get the filename without the extension
      file_name_without_ext = os.path.splitext(filename)[0]
      
      # Step 1: Use OCR to extract text from the image
      # extracted_text = ocr_image(image_path)

      # print(f'extracted_text {extracted_text}')
      
      # Step 2: Use OpenAI API to structure the extracted text
      # structured_data = extract_data_with_openai(extracted_text)

      structured_data = extract_data_from_image_with_openai(image_path)

      print(f'structured_data {structured_data}')
      
      # Step 3: Parse the structured data into rows for CSV
      # Since OpenAI is instructed to format as CSV, split by lines and commas
      for row in structured_data.splitlines():
          row_data = row.split(',')
          # if len(row_data) == 3: # ,,, comma 만 있는 경우 제외.
          #   pass
          # else:
          print(f'row_data {row_data}')
          try:
            appendedData = {
                "typeOfTestAndNumber": row_data[0].strip(),
                "pageNum" : row_data[1],
                "sequence" : row_data[1].strip(),
                "questionText": row_data[2].strip(),
                "options": ','.join(row_data[3].split('||'))
            }
            all_data.append(appendedData)
          except:
            print(f'[ERROR] faild for sentence {row_data}')
          
          output_csv = f'{output_csv_dir}/{file_name_without_ext}.csv'

          # Convert all data to a DataFrame and save it to CSV
          df = pd.DataFrame(appendedData)
          df.to_csv(output_csv, index=False)

          print(f"Data extracted and saved to {output_csv}")      

total_output_csv = f'{output_csv_dir}/{levelName}_total.csv'

# Convert all data to a DataFrame and save it to CSV
df = pd.DataFrame(all_data)
df.to_csv(output_csv, index=False)

print(f"Data extracted and saved to {total_output_csv}")
