import requests
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

# Generate RSS feed
feed = feedgenerator.Rss201rev2Feed(
    title="Comic Updates",
    link="https://www.sparklecarehospital.com",
    description="Updates for the comic.",
)

# Generate second RSS feed
second_feed = feedgenerator.Rss201rev2Feed(
    title="Comic Updates (Reversed)",
    link="https://www.sparklecarehospital.com",
    description="Updates for the comic in reverse order.",
)

# Generate first HTML page
html_content1 = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comic</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f0f0f0;
        }}
        .slideshow {{
            position: relative;
            max-width: 80%;
            max-height: 80vh;
            margin: auto;
        }}
        .image {{
            display: block;
            width: auto;
            max-height: 80vh;
            margin: auto;
        }}
        .button {{
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background-color: rgba(255, 255, 255, 0.5);
            border: none;
            padding: 10px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .button:hover {{
            background-color: rgba(255, 255, 255, 0.8);
        }}
        .button-back {{
            left: -100px;
        }}
        .button-next {{
            right: -100px;
        }}
    </style>
</head>
<body>
    <div class="slideshow">
        <img class="image" src="{comic_url.format(0)}" alt="Comic Image">
        <button class="button button-back" onclick="previousSlide()">Back</button>
        <button class="button button-next" onclick="nextSlide()">Next</button>
    </div>

    <script>
        var currentPage1 = 0;
        var totalPages1 = {latest_page};

        function previousSlide() {{
            currentPage1 = (currentPage1 - 1 + totalPages1) % totalPages1;
            updateSlide1();
        }}

        function nextSlide() {{
            currentPage1 = (currentPage1 + 1) % totalPages1;
            updateSlide1();
        }}

        function updateSlide1() {{
            var image = document.querySelector('.image');
            image.src = "{comic_url.format('')}";

            var pageNumber = currentPage1;
            for (var i = 0; i < 10; i++) {{
                var altPage = pageNumber + String.fromCharCode(97 + i);
                var altPageUrl = "{comic_url.format('')}";

                var http = new XMLHttpRequest();
                http.open('HEAD', altPageUrl, false);
                http.send();

                if (http.status != 404) {{
                    image.src = altPageUrl;
                    break;
                }}
            }}
        }}
    </script>
</body>
</html>
"""

# Generate second HTML page
html_content2 = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comic</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-color: #f0f0f0;
        }}
        .image {{
            display: block;
            max-width: 80%;
            max-height: 80vh;
            margin: 10px auto;
        }}
    </style>
</head>
<body>
"""

# Loop through pages to add to feeds and HTML pages
for page_number in range(latest_page):
    page_exists = False

    # Check if main page exists
    response = requests.get(comic_url.format(page_number), headers=headers)
    if response.status_code == 200:
        page_exists = True
        description = f"""<![CDATA[<p><a href="{comic_url.format(page_number)}" rel="bookmark" title="Comic Page {page_number}">
            <img src="{comic_url.format(page_number)}" alt="" loading="lazy" /></a></p>"""
        feed.add_item(
            title=f"Page {page_number}",
            link=comic_url.format(page_number),
            description=description,
        )
        second_feed.add_item(
            title=f"Page {page_number}",
            link=comic_url.format(page_number),
            description=description,
        )
        html_content2 += f'<img class="image" src="{comic_url.format(page_number)}" alt="Comic Page {page_number}">'
    
    # Check for alternate pages with appended letters
    for char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']:
        alt_page = f"{page_number}{char}"
        alt_page_url = comic_url.format(alt_page)
        response = requests.get(alt_page_url, headers=headers)
        if response.status_code == 200:
            page_exists = True
            description = f"""<![CDATA[<p><a href="{alt_page_url}" rel="bookmark" title="Comic Page {alt_page}">
                <img src="{alt_page_url}" alt="" loading="lazy" /></a></p>"""
            feed.add_item(
                title=f"Page {alt_page}",
                link=alt_page_url,
                description=description,
            )
            second_feed.add_item(
                title=f"Page {alt_page}",
                link=alt_page_url,
                description=description,
            )
            html_content2 += f'<img class="image" src="{alt_page_url}" alt="Comic Page {alt_page}">'

    # Add empty space if the page doesn't exist
    if not page_exists:
        html_content2 += '<div style="height: 100px;"></div>'

# Close the HTML content for the second page
html_content2 += """
</body>
</html>
"""

# Write RSS feeds to files
rss_feed = feed.writeString('utf-8')
rss_feed_bytes = rss_feed.encode('utf-8')
with open("output/comic_feed.xml", "wb") as f:
    f.write(rss_feed_bytes)

second_rss_feed = second_feed.writeString('utf-8')
second_rss_feed_bytes = second_rss_feed.encode('utf-8')
with open("output/comic_feed_reversed.xml", "wb") as f:
    f.write(second_rss_feed_bytes)

# Write HTML contents to files
with open("output/comic.html", "w") as f:
    f.write(html_content1)

with open("output/comic_all_pages.html", "w") as f:
    f.write(html_content2)