import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.url == 'https://tululu.org/' and response.history:
        raise requests.HTTPError()


def download_books():
    catalog_name = 'books'
    Path(f'./{catalog_name}').mkdir(exist_ok=True)

    for book_id in range(1, 11):
        url = f"https://tululu.org/txt.php?id={book_id}"
        response = requests.get(url)
        response.raise_for_status()

        try:
            check_for_redirect(response)
        except requests.RequestException:
            continue

        filename = f'{catalog_name}/id{book_id}.txt'
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)


def get_name_and_author():
    url = 'https://tululu.org/b1/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('table').find('h1')
    title_text = title_tag.text
    book_card = title_text.split(sep='::')
    title = book_card[0].strip()
    author = book_card[1].strip()

    print(f'Title: {title}', f'Author: {author}', sep='\n')


def download_txt(url, filename, folder='books'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    valid_filename = f'{sanitize_filename(filename)}.txt'
    return os.path.join(folder, valid_filename)


def main():
    url = 'http://tululu.org/txt.php?id=1'
    filepath = download_txt(url, 'Алиби')
    print(filepath)  # Выведется books/Алиби.txt
    filepath = download_txt(url, 'Али/би', folder='books')
    print(filepath)  # Выведется books/Алиби.txt

    filepath = download_txt(url, 'Али\\би', folder='txt')
    print(filepath)  # Выведется txt/Алиби.txt

    return
    get_name_and_author()
    download_books()


if __name__ == '__main__':
    main()
