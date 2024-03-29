import requests
from bs4 import BeautifulSoup
import re
import os

# Fetch HTML content and parse it for 24-7-tv
url = 'https://mrgamingstreams.com/24-7-tv/'
response = requests.get(url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')

# Extract names and create .m3u8 links for 24-7-tv
names_links = {}
channel_divs = soup.find_all('div', class_='wp-block-button')

for channel_div in channel_divs:
    channel_name = channel_div.a.text.strip()
    href = channel_div.a['href']

    # Fetch each channel's page
    channel_page_response = requests.get(href)
    if channel_page_response.status_code == 200:
        channel_page = channel_page_response.text                                                                                                              # Search for .m3u8 URL in the response text
        m3u8_urls = re.findall(r'(https://[^\s]+\.m3u8)', channel_page)

        if m3u8_urls:
            # Store multiple unique .m3u8 URLs if found
            links = set()  # Using a set to avoid duplicates
            for m3u8_url in m3u8_urls:
                links.add(m3u8_url)

            # Store the channel name with unique links
            names_links[channel_name] = {
                "links": list(links),
                "tag": "24-7-tv"  # Adding tag for source page
            }
        else:
            print(f"No .m3u8 URL found for {channel_name}")
    else:
        print(f"Failed to fetch {channel_name} page")

# Fetch HTML content and parse the new page for event links
fighting_url = 'https://mrgamingstreams.com/fighting/'
fighting_response = requests.get(fighting_url)
fighting_html_content = fighting_response.content
fighting_soup = BeautifulSoup(fighting_html_content, 'html.parser')

schedule_table = fighting_soup.find('table', id='scheduleTable')
if schedule_table:
    event_rows = schedule_table.find_all('tr')[1:]  # Skipping the header row

    for row in event_rows:
        columns = row.find_all('td')
        if len(columns) == 3:
            event_name = columns[1].text.strip()
            link = columns[2].a['href']

            # Fetch each event's page
            event_page_response = requests.get(link)
            if event_page_response.status_code == 200:
                event_page = event_page_response.text
                # Search for .m3u8 URL in the response text
                m3u8_urls = re.findall(r'(https://[^\s]+\.m3u8)', event_page)

                if m3u8_urls:
                    # Store multiple unique .m3u8 URLs if found
                    links = set()  # Using a set to avoid duplicates
                    for m3u8_url in m3u8_urls:
                        links.add(m3u8_url)

                    # Store the event name with unique links
                    names_links[event_name] = {
                        "links": list(links),
                        "tag": "fighting"  # Adding tag for source page
                    }
                else:
                    print(f"No .m3u8 URL found for {event_name}")
            else:
                print(f"Failed to fetch {event_name} page")
# File path
file_path = 'updated_file.m3u8'

# Read existing content from the file
existing_content = ""
if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        existing_content = file.read()

# Find the index of '#PLAYLIST:Mrgaming' if it exists
playlist_index = existing_content.find("#PLAYLIST:Mrgaming")

if playlist_index != -1:
    # Find the end index of the playlist section to remove old links
    end_playlist_index = existing_content.find("#EXTINF:-1", playlist_index + len("#PLAYLIST:Mrgaming\n"))
    if end_playlist_index != -1:
        end_playlist_index = existing_content.rfind("\n", playlist_index, end_playlist_index)

    # Write the content before the playlist section
    with open(file_path, 'w') as file:
        file.write(existing_content[:playlist_index + len("#PLAYLIST:Mrgaming\n")])

        # Append modified content for Mrgaming playlist only
        for name, link in names_links.items():
            file.write(f"#EXTINF:-1 , {name} {link['tag']}\n")
            # Write all unique links associated with the name
            for l in link['links']:
                file.write(f"{l}\n")

else:
    # If the marker doesn't exist, append it and the new links to the end of the file
    with open(file_path, 'a') as file:
        file.write("#PLAYLIST:Mrgaming\n")

        for name, link in names_links.items():
            file.write(f"#EXTINF:-1 , {name} {link['tag']}\n")
            # Write all unique links associated with the name
            for l in link['links']:
                file.write(f"{l}\n")