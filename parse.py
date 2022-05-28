from pathlib import Path

import requests


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


def main():
    download_books()


if __name__ == '__main__':
    main()
