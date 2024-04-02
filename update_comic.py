import requests
import feedparser
from fpdf import FPDF

comic_url = "https://www.sparklecarehospital.com/media/page/{}.png"
latest_page = 0

# Find the newest page
while True:
	response = requests.head(comic_url.format(latest_page + 1))
	if response.status_code == 404:
		break
	latest_page += 1
	
# Generate RSS feed
feed = feedparser.FeedGenerator()
feed.title("Comic Updates")
feed.link(href="https://www.sparklecarehospital.com")
for page_number in range(latest_page + 1):
	feed.add_entry(title=f"Page {page_number}", link=comic_url.format(page_number))
	
rss_feed = feed.writeString('utf-8')
with open("output/comic_feed.xml", "wb") as f:
	f.write(rss_feed)
	
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
for page_number in range(latest_page + 1):
	html_content += f"<li><a href=\"{comic_url.format(page_number)}\">Page {page_number}</a></li>"
	
html_content += """
	</ul>
</body>
</html>
"""
with open("output/comic.html", "w") as f:
	f.write(html_content)
	
# Generate PDF file
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)
for page_number in range(latest_page + 1):
	pdf.cell(200, 10, txt=f"Page {page_number}", ln=True, align="C")
	pdf.image(comic_url.format(page_number), x=10, y=None, w=180)
	pdf.add_page()
	
pdf.output("output/comic.pdf")