import requests
from PIL import Image
from fpdf import FPDF
import os
import feedgenerator

comic_url = "https://www.sparklecarehospital.com/media/page/{}"
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
    found_alternate = False
    for char in [''] + list('abcdefghijklmnopqrstuvwxyz'):
        response = requests.get(comic_url.format(f"{latest_page}{char}"), headers=headers)
        if response.status_code == 200:
            latest_page += 1
            print(f"Found comic page {latest_page}")
            found_alternate = True
        else:
            break
    if not found_alternate:
        break

print(f"Total comic pages found: {latest_page}")

# Create a directory to store downloaded images
output_dir = "output/images"
os.makedirs(output_dir, exist_ok=True)

# Download images
for page_number in range(latest_page + 1):
    image_url = comic_url.format(page_number)
    image_path = os.path.join(output_dir, f"{page_number}.png")
    with open(image_path, 'wb') as f:
        f.write(requests.get(image_url, headers=headers).content)

# Generate PDF file
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

for page_number in range(latest_page):
    pdf.cell(200, 10, txt=f"Page {page_number}", ln=True, align="C")
    image_path = os.path.join(output_dir, f"{page_number}.png")
    if os.path.exists(image_path):
        # Open the image
        img = Image.open(image_path)

        # Check if the image has an alpha channel
        if img.mode == 'RGBA':
            # Convert the image to RGB format
            img = img.convert('RGB')
            # Save the image as JPEG
            img_path_jpg = os.path.join(output_dir, f"{page_number}.jpg")
            img.save(img_path_jpg)
            image_path = img_path_jpg

        # Add the image to the PDF
        pdf.image(image_path, x=10, y=None, w=180)
    else:
        print(f"Image {image_path} not found.")

    pdf.add_page()

# Save PDF file
pdf_file_path = "output/comic.pdf"
pdf.output(pdf_file_path)

# Generate RSS feed
feed = feedgenerator.Rss201rev2Feed(
    title="Comic Updates",
    link="https://www.sparklecarehospital.com",
    description="Updates for the comic.",
)

for page_number in range(latest_page):
    feed.add_item(
        title=f"Page {page_number}",
        link=comic_url.format(page_number),
        description=f"Comic page {page_number}",
    )

rss_feed = feed.writeString('utf-8')
rss_feed_bytes = rss_feed.encode('utf-8')  # Encode the string to bytes
with open("output/comic_feed.xml", "wb") as f:  # Open file in binary mode
    f.write(rss_feed_bytes)

# Generate HTML page
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comic</title>
</head>
<body>
    <h1>Comic</h1>
    <ul>
"""
for page_number in range(latest_page):
    html_content += f"<li><a href=\"{comic_url.format(page_number)}\">Page {page_number}</a></li>"

html_content += """
    </ul>
</body>
</html>
"""
with open("output/comic.html", "w") as f:
    f.write(html_content)