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
    if response.status_code == 200:
        print(f"Found existing image at URL: {url}")
        return True
    return False

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
            flex-direction: column;
            align-items: center;
            background-color: #f0f0f0;
        }}
        .toolbar {{
            width: 100%;
            padding: 10px;
            background-color: #333;
            color: white;
            display: flex;
            justify-content: center; /* Center the toolbar horizontally */
            align-items: center;
        }}
        .toolbar button, .toolbar input[type='text'] {{
            background-color: #555;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
        }}
        .toolbar input[type='text'] {{
            width: 100px;
        }}
        .toolbar button:hover, .toolbar input[type='text']:hover {{
            background-color: #777;
        }}
        .toolbar button:active, .toolbar input[type='text']:active {{
            background-color: #444;
        }}
        .image-container {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: center;
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
<div class="toolbar">
    <div>
        <button onclick="resizeImages('small')">Small</button>
        <button onclick="resizeImages('medium')">Medium</button>
        <button onclick="resizeImages('large')">Large</button>
        <input type="text" id="customSize" placeholder="Custom Size">
        <button onclick="resizeImages('custom')">Apply</button>
    </div>
    <button onclick="openRSSFeed()">Open RSS Feed</button>
</div>
<div class="image-container">
"""

    page_number = 0
    while True:
        if (volume == "vol1" and page_number == 77) or (volume == "vol2" and page_number == 4):
            page_number += 1
            continue

        image_found = False
        for char in ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'] + [f"-{i}" for i in range(10)] + ['_colors_kitty']:
            url = comic_url.format(page_number, char)
            if image_exists(url):
                image_found = True
                html_content += f'<img class="image" src="{url}" alt="Comic Volume {volume}, Page {page_number}{char}">'
                page_number += 1
                break
        
        if not image_found:
            break

    html_content += f"""
</div>
<script>
    function resizeImages(size) {{
        const images = document.querySelectorAll('.image');
        images.forEach(image => {{
            if (size === 'small') {{
                image.style.width = '100px';
            }} else if (size === 'medium') {{
                image.style.width = '200px';
            }} else if (size === 'large') {{
                image.style.width = '300px';
            }} else if (size === 'custom') {{
                const customSize = document.getElementById('customSize').value;
                if (customSize) {{
                    image.style.width = customSize + 'px';
                }}
            }}
        }});
    }}

    function openRSSFeed() {{
        window.open('comic_{volume}_feed.xml', '_blank');
    }}
</script>
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

    # Add items to the RSS feed
    page_number = 0
    while True:
        image_found = False
        for char in ['', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'] + [f"-{i}" for i in range(10)] + ['_colors_kitty']:
            if (volume == "vol1" and page_number == 77) or (volume == "vol2" and page_number == 4):
                page_number += 1
                continue

            url = comic_url.format(page_number, char)
            if image_exists(url):
                rss_feed.add_item(
                    title=f"Page {page_number}{char}",
                    link=url,
                    description=f"Comic volume {volume}, Page {page_number}{char}"
                )
                image_found = True
                page_number += 1
                break
        
        if not image_found:
            break

    # Write RSS feed to a file
    rss_feed_output_path = f"comic_{volume}_feed.xml"
    with open(rss_feed_output_path, 'w', encoding='utf-8') as f:
        rss_feed.write(f, encoding='utf-8')