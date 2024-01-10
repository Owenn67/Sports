import requests
from bs4 import BeautifulSoup
import os

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

# File path
file_path = 'updated_file.m3u8'

# Read existing content from the file
existing_content = ""
if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        existing_content = file.read()

# Locate the position of #PLAYLIST:Mrgaming
mrgaming_index = existing_content.find("#PLAYLIST:Mrgaming")

# Append content after #PLAYLIST:Mrgaming if found, or append at the end if not found
if mrgaming_index != -1:
    before_mrgaming = existing_content[:mrgaming_index]
    after_mrgaming = existing_content[mrgaming_index:]

    with open(file_path, 'w') as file:
        file.write(before_mrgaming)  # Write content before #PLAYLIST:Mrgaming

        # Write the StreamB playlist title
        file.write("#PLAYLIST:StreamB\n")

        # Write content for StreamB playlist only
        for category, channels in names_links.items():
            for name, link in channels.items():
                file.write(f"#EXTINF:-1 , {name}\n")
                file.write(f"{link}\n")

        file.write(after_mrgaming)  # Write content after #PLAYLIST:Mrgaming
else:
    with open(file_path, 'a') as file:
        file.write("#PLAYLIST:StreamB\n")

        for category, channels in names_links.items():
            for name, link in channels.items():
                file.write(f"#EXTINF:-1 , {name}\n")
                file.write(f"{link}\n")
