import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_phone_numbers(text):
    hidden_numbers = re.findall(r'<div class="phone-number__placeholder">(.*?)</div>', text)
    formatted_hidden_numbers = ['8' + re.sub(r'[^\d]', '', number) for number in hidden_numbers]
    open_numbers = re.findall(r'\b(?:\+?7|8)[\s(-]?\d{3}[)\s-]?\d{3}[-\s]?\d{2}[-\s]?\d{2}\b', text)
    formatted_open_numbers = [re.sub(r'\D', '', number) for number in open_numbers]
    formatted_open_numbers = ['8' + number[1:] if number.startswith('+7') or number.startswith('7') else number for number in formatted_open_numbers]
    return formatted_hidden_numbers + formatted_open_numbers

def extract_internal_links(base_url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    internal_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(base_url, href)
        parsed_url = urlparse(absolute_url)
        main_domain = re.sub(r'^.*?\.hands\.ru', 'hands.ru', parsed_url.netloc)
        if main_domain == parsed_base_url.netloc:
            internal_links.append(absolute_url)
    return internal_links

start_url = input("Введите URL:")
response = requests.get(start_url)
html_content = response.text
parsed_base_url = urlparse(start_url)
all_internal_links = set([start_url])
all_phone_numbers = set()

internal_links = extract_internal_links(start_url, html_content)
all_internal_links.update(internal_links)

def process_url(url):
    response = requests.get(url)
    html_content = response.text
    phone_numbers = extract_phone_numbers(html_content)
    return phone_numbers

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = []
    for url in all_internal_links:
        futures.append(executor.submit(process_url, url))
    for future in as_completed(futures):
        all_phone_numbers.update(future.result())

print("Найденные телефонные номера:")
for phone_number in all_phone_numbers:
    print(phone_number)
