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

    formatted_open_numbers = ['8' + number[1:] for number in formatted_open_numbers]

    return formatted_hidden_numbers + formatted_open_numbers


def extract_internal_links(base_url, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    internal_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(base_url, href)
        internal_links.append(absolute_url)
    return internal_links


def process_url(url, base_domain):
    if url.startswith('tel:'):
        return []
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        phone_numbers = extract_phone_numbers(html_content)
        return phone_numbers
    except (requests.RequestException, ValueError) as e:
        print(f"Error processing {url}: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def crawl_website(start_url):
    base_domain = urlparse(start_url).netloc
    response = requests.get(start_url)
    response.raise_for_status()
    html_content = response.text

    all_internal_links = set(extract_internal_links(start_url, html_content))
    all_phone_numbers = set()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for url in all_internal_links:
            parsed_url = urlparse(url)
            if parsed_url.netloc == base_domain:
                futures.append(executor.submit(process_url, url, base_domain))
        for future in as_completed(futures):
            all_phone_numbers.update(future.result())

    print("Найденные телефонные номера:")
    for phone_number in all_phone_numbers:
        print(phone_number)


if __name__ == "__main__":
    start_url = input("Введите URL сайта: ")
    crawl_website(start_url)
