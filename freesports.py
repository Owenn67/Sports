import requests
from bs4 import BeautifulSoup
import re
import os

# Function to fetch and update .m3u8 file
def update_m3u8_file(file_path):
    # Fetch HTML content
    url = 'https://streambtw.com'
    response = requests.get(url)
    html_content = response.content

    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract names and create .m3u8 links
    names_links = {}
    ul_lists = soup.find_all('ul', class_='list-group')

    for ul_list in ul_lists:
        category = ul_list.find('center').text.strip()

        # Find all <a> tags within the list
        channel_links = ul_list.find_all('a')
        for channel_link in channel_links:
            channel_name = channel_link.text.strip()
            href = channel_link['href']

            # Fetch each channel's page
            channel_page_response = requests.get(href)
            if channel_page_response.status_code == 200:
                channel_page = channel_page_response.text
                # Search for .m3u8 URL in the response text
                m3u8_url = re.search(r'(https://[^\s]+\.m3u8)', channel_page)

                if m3u8_url:
                    # Extracted .m3u8 URL
                    extracted_m3u8 = m3u8_url.group()

                    # Parse :authority: and :path: from the URL
                    authority = extracted_m3u8.split('/')[2]
                    path = '/'.join(extracted_m3u8.split('/')[3:])

                    # Store the channel name, :authority:, and :path:
                    names_links[channel_name] = {
                        "category": category,
                        "authority": authority,
                        "path": path
                    }
                else:
                    print(f"No .m3u8 URL found for {channel_name} in {category}")
            else:
                print(f"Failed to fetch {channel_name} page in {category}")

    # Read existing content from the file
    existing_content = ""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            existing_content = file.read()

    # Find the start and end index of '#PLAYLIST:StreamB' if it exists
    playlist_start_index = existing_content.find("#PLAYLIST:StreamB")
    playlist_end_index = existing_content.find("#PLAYLIST:", playlist_start_index + 1) if playlist_start_index != -1 else -1

    if playlist_start_index != -1:
        # Remove the content under StreamB playlist
        updated_content = existing_content[:playlist_start_index + len("#PLAYLIST:StreamB\n")]

        # Append modified content for StreamB playlist only
        for name, link in names_links.items():
            new_link = f"https://{link['authority']}/{link['path']}\n"

            if new_link not in existing_content:
                updated_content += f"#EXTINF:-1 , {name} - {link['category']}\n"
                updated_content += new_link

                # Optionally, add more custom tags here for each channel

        # Append existing content after StreamB playlist if there's content after it
        if playlist_end_index != -1:
            updated_content += existing_content[playlist_end_index:]
        else:
            updated_content += "\n"  # Add a newline at the end if StreamB playlist was at the end of the file

        # Write the updated content back to the file
        with open(file_path, 'w') as file:
            file.write(updated_content)

    else:
        print("StreamB playlist doesn't exist. Creating...")
        # If the marker doesn't exist, append it and the new links to the end of the file
        with open(file_path, 'a') as file:
            file.write("#PLAYLIST:StreamB\n")

            for name, link in names_links.items():
                file.write(f"#EXTINF:-1 , {name} - {link['category']}\n")
                file.write(f"https://{link['authority']}/{link['path']}\n")

                # Optionally, add more custom tags here for each channel

# Call the function to update the .m3u8 file
update_m3u8_file('updated_file.m3u8')
