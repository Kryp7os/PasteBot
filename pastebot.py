import requests
from bs4 import BeautifulSoup
import re
import os
import time

# Function to scrape all pastebin URLs with 8-character identifiers from a page
def scrape_pastebin_urls(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    pastebin_urls = []
    for link in soup.select('table.maintable tbody tr a[href^="/"]'):
        title = link.text.strip()
        href = link['href']
        if re.match(r'/\w{8}$', href):
            paste_key = href[1:]
            pastebin_urls.append((title, paste_key))
    return pastebin_urls

# Function to fetch raw content of a paste
def fetch_raw_content(paste_key):
    raw_url = f'https://pastebin.com/raw/{paste_key}'
    response = requests.get(raw_url)
    if response.status_code == 200:
        return response.text
    else:
        print(f'Failed to fetch raw content of paste with key: {paste_key}')
    return None

# Webhook URL for your Discord channel
WEBHOOK_URL = 'WEBHOOKGOESHERE'

def send_to_discord_webhook(title, paste_key, content):
    formatted_content = f'```plaintext\n{content}\n```'
    data = {
        'content': f'**{title}** (Key: {paste_key})\n{formatted_content}'
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 200:
        print('Failed to send message to Discord webhook.')

# Load previously processed URLs
processed_urls = set()
if os.path.exists('processed_urls.txt'):
    with open('processed_urls.txt', 'r') as file:
        processed_urls.update(file.read().splitlines())

# Continuous monitoring loop
while True:
    # Scrape pastebin URLs from the page
    print("Scraping Pastebin URLs...")
    all_pastebin_urls = scrape_pastebin_urls('https://pastebin.com/archive')
    new_urls = [(title, url) for title, url in all_pastebin_urls if url not in processed_urls]
    print(f"Found {len(new_urls)} new Pastebin URLs with 8-character identifiers.")

    # Fetch raw content of new pastes and send to Discord
    print("Fetching raw content of new pastes...")
    for title, paste_key in new_urls:
        raw_content = fetch_raw_content(paste_key)
        if raw_content:
            print(f"Fetched raw content for paste with key: {paste_key}")
            send_to_discord_webhook(title, paste_key, raw_content)
            processed_urls.add(paste_key)

    # Save updated processed URLs
    with open('processed_urls.txt', 'w') as file:
        file.write('\n'.join(processed_urls))

    # Delay before next iteration
    print("Waiting for 5 minutes before checking for new URLs again...")
    time.sleep(300)  # Wait for 5 minutes before checking again
