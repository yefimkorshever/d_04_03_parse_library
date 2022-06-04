import argparse
import os
import sys
from pathlib import Path
from time import sleep
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def create_arg_parser():
    description = 'The program parses tululu.org library'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('start_id',
                        help='start book id, by default: 1',
                        default=1,
                        nargs='?',
                        type=int,
                        )

    parser.add_argument('end_id',
                        help='end book id, by default: 10',
                        default=10,
                        nargs='?',
                        type=int,
                        )
    return parser


def check_for_redirect(response):
    if response.url == 'https://tululu.org/' and response.history:
        raise requests.HTTPError('redirected')


def parse_book_page(response):

    soup = BeautifulSoup(response.text, 'lxml')
    div_content = soup.find('div', id='content')
    title_text = div_content.find('h1').text
    title, author = title_text.split(sep='::')
    img_src = div_content.find('img')['src']
    comments_tags = soup.find_all('div', class_='texts')
    genres_links = soup.find('span', class_='d_book').find_all('a')

    return {
        'title': title.strip(),
        'author': author.strip(),
        'image': urljoin(response.url, img_src),
        'comments': [x.find('span').text for x in comments_tags],
        'genres': [x.text for x in genres_links],
    }


def download_image(url, folder):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    filename = urlsplit(url).path.split(sep='/')[-1]
    valid_filename = unquote(filename)
    file_path = os.path.join(folder, valid_filename)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_txt(url, filename, folder):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    valid_filename = f'{sanitize_filename(filename)}.txt'
    file_path = os.path.join(folder, valid_filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(response.text)


def main():
    arg_parser = create_arg_parser()
    namespace = arg_parser.parse_args()

    image_folder = 'images'
    txt_folder = 'books'
    Path(f'./{image_folder}').mkdir(exist_ok=True)
    Path(f'./{txt_folder}').mkdir(exist_ok=True)

    for book_id in range(namespace.start_id, namespace.end_id + 1):
        print('\n')
        head_url = 'https://tululu.org/'
        url = f'{head_url}b{book_id}'

        try:
            book_page_response = requests.get(url)
            book_page_response.raise_for_status()
            check_for_redirect(book_page_response)
        except requests.exceptions.HTTPError as http_fail:
            print(
                f'failed to download book{book_id} page; {http_fail}',
                file=sys.stderr
            )
            continue
        except requests.exceptions.ConnectionError as connect_fail:
            print(
                f'failed to download book{book_id} page (connection error);',
                connect_fail,
                file=sys.stderr
            )
            sleep(2)
            continue

        book_card = parse_book_page(book_page_response)
        print(book_card['title'])
        print(book_card['genres'])

        try:
            download_image(book_card['image'], image_folder)
        except requests.exceptions.HTTPError as http_fail:
            print(
                f'failed to download book{book_id} image;',
                http_fail,
                file=sys.stderr
            )
        except requests.exceptions.ConnectionError as connect_fail:
            print(
                f'failed to download book{book_id} image (connection error);',
                connect_fail,
                file=sys.stderr
            )
            sleep(2)

        title = book_card['title']

        try:
            download_txt(
                f'{head_url}txt.php?id={book_id}',
                f'{book_id}.{title}',
                txt_folder,
            )
        except requests.exceptions.HTTPError as http_fail:
            print(
                f'failed to download book{book_id} text;',
                http_fail,
                file=sys.stderr
            )
        except requests.exceptions.ConnectionError as connect_fail:
            print(
                f'failed to download book{book_id} text (connection error);',
                connect_fail,
                file=sys.stderr
            )
            sleep(2)


if __name__ == '__main__':
    main()
