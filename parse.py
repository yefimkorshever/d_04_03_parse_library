from pathlib import Path

import requests


def download_books():
    catalog_name = 'books'
    Path(f'./{catalog_name}').mkdir(exist_ok=True)
    for counter in range(1, 11):
        url = f"https://tululu.org/txt.php?id={counter}"
        response = requests.get(url)
        response.raise_for_status()

        filename = f'{catalog_name}/id{counter}.txt'
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)


def main():
    download_books()


if __name__ == '__main__':
    main()
