import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.url == 'https://tululu.org/' and response.history:
        raise requests.HTTPError()


def get_response(url):
    response = requests.get(url)
    response.raise_for_status()
    return response


def parse_book_page(text):
    soup = BeautifulSoup(text, 'lxml')
    title_tag = soup.find('table').find('h1')
    title_text = title_tag.text
    book_name = title_text.split(sep='::')

    return {
        'title': book_name[0].strip(),
        'author': book_name[1].strip(),
    }


def download_txt(url, filename, folder):
    response = get_response(url)
    try:
        check_for_redirect(response)
    except requests.RequestException:
        return

    valid_filename = f'{sanitize_filename(filename)}.txt'
    file_path = os.path.join(folder, valid_filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response.text)


def download_books():
    folder = 'books'
    Path(f'./{folder}').mkdir(exist_ok=True)

    for book_id in range(1, 11):
        head_url = 'https://tululu.org/'
        book_page_response = get_response(f'{head_url}b{book_id}')
        try:
            check_for_redirect(book_page_response)
        except requests.RequestException:
            continue

        book_card = parse_book_page(book_page_response.text)
        title = book_card['title']
        download_txt(
            f'{head_url}txt.php?id={book_id}',
            f'{book_id}.{title}',
            folder)


def main():
    download_books()


if __name__ == '__main__':
    main()
