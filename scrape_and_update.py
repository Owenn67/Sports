import requests
from bs4 import BeautifulSoup

# Fetch HTML content
url = 'https://soccer.freesportstime.com/'
response = requests.get(url)
html_content = response.content

# Parse HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Extract names and links
names_links = {}
sections = soup.find_all('ul', class_='list-group')
for section in sections:
    section_name = section.find('center').text.strip()
    links = section.find_all('li', class_='list-group-item')
    names_links[section_name] = {}
    for link in links:
        name = link.text.strip()
        iframe_url = link.a['href']  # Assuming this is the iframe URL

        # Extract the number from the URL
        channel_number = ''.join(filter(str.isdigit, iframe_url))

        # Check URL format and create the .m3u8 link accordingly
        if 'box' in iframe_url:
            m3u8_link = f'https://hls.streambtw.com/live/stream_box{channel_number}.m3u8'
        else:
            m3u8_link = f'https://hls.streambtw.com/live/stream_{channel_number}.m3u8'

        # Map the channel name to its .m3u8 link
        names_links[section_name][name] = m3u8_link

# Write the content to a new .m3u8 file
with open('updated_file.m3u8', 'w') as file:
    for category, channels in names_links.items():
        for name, link in channels.items():
            file.write(f"#EXTINF:-1 , {name}\n")
            file.write(f"{link}\n")
