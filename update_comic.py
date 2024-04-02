import requests
from PIL import Image
from fpdf import FPDF
import os

comic_url = "https://www.sparklecarehospital.com/media/page/{}.png"
latest_page = 0

# Define headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Check if the first page exists
response = requests.get(comic_url.format(0), headers=headers)
if response.status_code != 200:
    print("Comic page 0 does not exist.")
    exit()

print(f"Found comic page 0. Checking for additional pages...")

# Find the newest page
while True:
    # Check for the main page
    response = requests.get(comic_url.format(latest_page + 1), headers=headers)
    if response.status_code != 200:
        # If main page doesn't exist, check for alternate pages
        found_alternate = False
        for char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
            response = requests.get(comic_url.format(f"{latest_page}{char}"), headers=headers)
            if response.status_code == 200:
                latest_page += 1
                found_alternate = True
            else:
                break
        if not found_alternate:
            break
    else:
        latest_page += 1
        print(f"Found comic page {latest_page}")

print(f"Total comic pages found: {latest_page}")

# Create a directory to store downloaded images
output_dir = "output/images"
os.makedirs(output_dir, exist_ok=True)

# Download images
for page_number in range(latest_page + 1):
    image_urls = [comic_url.format(page_number)]
    for char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
        response = requests.get(comic_url.format(f"{page_number}{char}"), headers=headers)
        if response.status_code == 200:
            image_urls.append(comic_url.format(f"{page_number}{char}"))
        else:
            break
    
    for image_url in image_urls:
        image_path = os.path.join(output_dir, f"{page_number}{image_url[-5]}.png")
        with open(image_path, 'wb') as f:
            f.write(requests.get(image_url, headers=headers).content)

# Generate PDF file
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

for page_number in range(latest_page + 1):
    pdf.cell(200, 10, txt=f"Page {page_number}", ln=True, align="C")
    for char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
        image_path = os.path.join(output_dir, f"{page_number}{char}.png")
        if os.path.exists(image_path):
            # Open the image
            img = Image.open(image_path)
            
            # Check if the image has an alpha channel
            if img.mode == 'RGBA':
                # Convert the image to RGB format
                img = img.convert('RGB')
                # Save the image as JPEG
                img_path_jpg = os.path.join(output_dir, f"{page_number}{char}.jpg")
                img.save(img_path_jpg)
                image_path = img_path_jpg

            # Add the image to the PDF
            pdf.image(image_path, x=10, y=None, w=180)
        else:
            print(f"Image {image_path} not found.")

    pdf.add_page()

pdf.output("output/comic.pdf")