from openai import OpenAI
import os
import pytesseract
from PIL import Image
import pandas as pd

# Set your OpenAI API key
API_KEY = os.environ['apiKey']
client = OpenAI(api_key=API_KEY)

# Set the grade level
grade = 3
levelName = f'G{grade}'
image_url_dir = f'https://cdn.topialive.co.kr/prep-daily-test/returnee/images/{levelName}'
output_csv_dir = f'csv/{levelName}'

# Grade-based file number ranges
fileNumberRange = {
   3: [2, 63],
   4: [2, 105],
   5: [3, 107],
   6: [3, 97],
   7: [3, 101]
}

# Ensure the output directory exists
os.makedirs(output_csv_dir, exist_ok=True)

# Function to extract data from an image with OpenAI API
def extract_data_from_image_with_openai(image_path, grade):
    prompt = f"""Extract the following details from the provided image:
    
    - typeOfTestAndNumber: Located at the top of the page and will be either "Level Test N" or "Cumulative Test N." N stands for the number stated at the image. not literally "N".
    - pageNum: Numeric value located at the bottom of the page near the text "Wordly Wise 3000 Test Booklet {grade}" indicating the page of the image
    - sequence: Number value of the numbered sentences.
    - questionText: This refers to the numbered sentences in the test.
    - options: The 3-4 phrases listed under each question, marked with circled letters. Each option should be separated with ||. Leave out the circled letters.
    
    Format the output as a CSV with the following columns: typeOfTestAndNumber, pageNum, sequence, questionText, options.
    Leave out the triple backticks in the beginning and the end of the answer and csv prefix.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user",
             "content": [                
                {
                    "type":"text",
                    "text": prompt
                },
                {
                  "type": "image_url",
                  "image_url": {"url": image_path}
                }
              ]
            },
        ]
    )

    # return response['choices'][0]['message']['content'].strip()
    return response.choices[0].message.content.strip()

# Process all images in the specified range for the grade level
all_data = []
range_start, range_end = fileNumberRange.get(grade, [0, 0])
print(f'range_start {range_start} / range_end {range_end}')

for i in range(range_start, range_end + 1):
    image_url = f"{image_url_dir}/{i}.jpg"
    print(f"Processing image: {image_url}")

    # Extract text using OCR (if needed as fallback)
    # ocr_text = pytesseract.image_to_string(image)

    # Extract structured data from GPT-4 API
    structured_data = extract_data_from_image_with_openai(image_url, grade)

    print(f'structured_data {structured_data}')

    # Step 3: Parse the structured data into rows for CSV
    for row in structured_data.splitlines():
        row_data = row.split(',')
        
        # Filter out rows with missing data
        if len(row_data) < 5:
            print(f'[ERROR] Incomplete data for sentence: {row_data}')
            continue

        # Prepare the data entry
        try:
          appendedData = {
              "typeOfTestAndNumber": row_data[0].strip(),
              "pageNum": row_data[1].strip(),
              "sequence": row_data[2].strip(),
              "questionText": row_data[3].strip(),
              "options": f"{','.join(row_data[4].split('||'))}"
          }

          all_data.append(appendedData)
        except:
          print(f'[ERROR] faild for sentence {row_data}')

        output_csv = f'{output_csv_dir}/{grade}.csv'

        # Convert all data to a DataFrame and save it to CSV
        df = pd.DataFrame([appendedData])
        df.to_csv(output_csv, index=False)

    print(f"Data extracted and saved to {output_csv}")      


# Convert all data to a DataFrame and save it to a total CSV
total_output_csv = f'{output_csv_dir}/{levelName}_total.csv'
df = pd.DataFrame(all_data)
df.to_csv(total_output_csv, index=False)

print(f"Data extracted and saved to {total_output_csv}")