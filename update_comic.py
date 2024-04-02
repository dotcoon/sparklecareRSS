import requests
from PIL import Image
from fpdf import FPDF
import os
import feedgenerator

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
    response = requests.get(comic_url.format(latest_page), headers=headers)
    if response.status_code == 200:
        print(f"Found comic page {latest_page}")
    else:
        # If main page doesn't exist, check for alternate pages with appended letters
        char = 'a'
        alternate_found = False
        while True:
            response = requests.get(comic_url.format(f"{latest_page}{char}"), headers=headers)
            if response.status_code == 200:
                print(f"Found comic page {latest_page}{char}")
                char = chr(ord(char) + 1)  # Move to the next letter
                alternate_found = True
            else:
                break

        # If no alternate pages found, check for the next page without letters
        if not alternate_found:
            response = requests.get(comic_url.format(f"{latest_page + 1}"), headers=headers)
            if response.status_code == 200:
                print(f"Found comic page {latest_page + 1}")
            else:
                # If the page doesn't exist, check for v2 pages
                v2_page = 0
                while True:
                    response = requests.get(comic_url.format(f"v2/{v2_page}"), headers=headers)
                    if response.status_code == 200:
                        print(f"Found comic page v2/{v2_page}")
                        v2_page += 1
                    else:
                        break
                latest_page += v2_page
                break

    latest_page += 1

# Output the total number of comic pages found
print(f"Total comic pages found: {latest_page - 1}")

# Create a directory to store downloaded images
output_dir = "output/images"
os.makedirs(output_dir, exist_ok=True)

# Download images
for page_number in range(latest_page):
    image_urls = [comic_url.format(page_number)]
    for char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
        response = requests.get(comic_url.format(f"{page_number}{char}"), headers=headers)
        if response.status_code == 200:
            image_urls.append(comic_url.format(f"{page_number}{char}"))

    for image_url in image_urls:
        image_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_url))[0]}.png")
        with open(image_path, 'wb') as f:
            f.write(requests.get(image_url, headers=headers).content)

# Generate PDF file
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

for page_number in range(latest_page):
    pdf.cell(200, 10, txt=f"Page {page_number}", ln=True, align="C")
    
    # Add numeric images
    numeric_image_path_png = os.path.join(output_dir, f"{page_number}.png")
    numeric_image_path_jpg = os.path.join(output_dir, f"{page_number}.jpg")
    if os.path.exists(numeric_image_path_png):
        img = Image.open(numeric_image_path_png)
        if img.mode == 'RGBA':
            # Convert the image to RGB format
            img = img.convert('RGB')
            # Save the image as JPEG
            img_path_jpg = os.path.join(output_dir, f"{page_number}.jpg")
            img.save(img_path_jpg)
            pdf.image(img_path_jpg, x=10, y=None, w=180)
        else:
            pdf.image(numeric_image_path_png, x=10, y=None, w=180)
    elif os.path.exists(numeric_image_path_jpg):
        pdf.image(numeric_image_path_jpg, x=10, y=None, w=180)
        
    for char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
        image_path_png = os.path.join(output_dir, f"{page_number}{char}.png")
        image_path_jpg = os.path.join(output_dir, f"{page_number}{char}.jpg")
        if os.path.exists(image_path_png):
            img = Image.open(image_path_png)
            if img.mode == 'RGBA':
                # Convert the image to RGB format
                img = img.convert('RGB')
                # Save the image as JPEG
                img_path_jpg = os.path.join(output_dir, f"{page_number}{char}.jpg")
                img.save(img_path_jpg)
                pdf.image(img_path_jpg, x=10, y=None, w=180)
            else:
                pdf.image(image_path_png, x=10, y=None, w=180)
        elif os.path.exists(image_path_jpg):
            pdf.image(image_path_jpg, x=10, y=None, w=180)
            
    pdf.add_page()
    
pdf.output("output/comic.pdf")

# Generate RSS feed
feed = feedgenerator.Rss201rev2Feed(
    title="Comic Updates",
    link="https://www.sparklecarehospital.com",
    description="Updates for the comic.",
)

for page_number in range(latest_page):  # Start from page 0
    feed.add_item(
        title=f"Page {page_number}",
        link=comic_url.format(page_number),
        description=f"Comic page {page_number}",
    )

    for char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
        alt_page = f"{page_number}{char}"
        alt_page_url = comic_url.format(alt_page)
        response = requests.get(alt_page_url, headers=headers)
        if response.status_code == 200:
            feed.add_item(
                title=f"Page {alt_page}",
                link=alt_page_url,
                description=f"Comic page {alt_page}",
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
for page_number in range(latest_page):  # Start from page 0
    html_content += f"<li><a href=\"{comic_url.format(page_number)}\">Page {page_number}</a></li>"

    for char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
        alt_page = f"{page_number}{char}"
        alt_page_url = comic_url.format(alt_page)
        response = requests.get(alt_page_url, headers=headers)
        if response.status_code == 200:
            html_content += f"<li><a href=\"{alt_page_url}\">Page {alt_page}</a></li>"

html_content += """
    </ul>
</body>
</html>
"""
with open("output/comic.html", "w") as f:
    f.write(html_content)