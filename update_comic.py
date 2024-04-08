import requests
import os
import feedgenerator

# URLs for each comic volume
comic_urls = {
    "vol1": "https://www.sparklecarehospital.com/media/page/{}{}.png",
    "vol2": "https://www.sparklecarehospital.com/media/page/v2/{}{}.png",
    "vol3": "https://www.sparklecarehospital.com/media/page/v3/{}{}.png",
    "vol4": "https://www.sparklecarehospital.com/media/page/v4/{}{}.png"
}

# Define headers to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Function to check if an image exists at a URL
def image_exists(url):
    response = requests.head(url, headers=headers)
    return response.status_code == 200

# Generate RSS feed
def generate_rss(feed_title, feed_link, feed_description):
    feed = feedgenerator.Rss201rev2Feed(
        title=feed_title,
        link=feed_link,
        description=feed_description
    )
    return feed

# Generate HTML content for a volume
def generate_html(volume, comic_url):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comic Volume {volume}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
            background-color: #f0f0f0;
        }}
        .image {{
            display: block;
            width: 200px;
            height: auto;
            margin: 10px;
        }}
    </style>
</head>
<body>
"""

    page_number = 0
    while True:
        image_found = False
        for char in ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']:
            url = comic_url.format(page_number, char)
            if image_exists(url):
                image_found = True
                html_content += f'<img class="image" src="{url}" alt="Comic Volume {volume}, Page {page_number}">'
                page_number += 1
            else:
                break
        
        if not image_found:
            break

    html_content += """
</body>
</html>
"""
    return html_content

# Loop through each volume
for volume, comic_url in comic_urls.items():
    # Generate HTML page for the volume
    html_content = generate_html(volume, comic_url)

    # Write HTML content to a file
    html_output_path = f"comic_{volume}.html"
    with open(html_output_path, "w") as f:
        f.write(html_content)

    # Generate RSS feed for the volume
    rss_feed = generate_rss(
        feed_title=f"Comic {volume} Updates",
        feed_link="https://www.sparklecarehospital.com",
        feed_description=f"Updates for Comic {volume}."
    )

    # Write RSS feed to a file
    rss_feed_output_path = f"comic_{volume}_feed.xml"
    rss_feed.write(open(rss_feed_output_path, 'w'))