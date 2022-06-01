import os
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

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


def parse_comments(soup):
    comments = []
    comments_tags = soup.find_all('div', class_='texts')
    for comment_tag in comments_tags:
        comments.append(comment_tag.find('span').text)

    return comments


def pars_genres(soup):
    genres = []
    genres_links = soup.find('span', class_='d_book').find_all('a')
    for genre_link in genres_links:
        genres.append(genre_link.text)

    return genres


def parse_book_page(response):

    soup = BeautifulSoup(response.text, 'lxml')
    div_content = soup.find('div', id='content')
    title_text = div_content.find('h1').text
    book_name = title_text.split(sep='::')
    img_src = div_content.find('img')['src']

    return {
        'title': book_name[0].strip(),
        'author': book_name[1].strip(),
        'image': urljoin(response.url, img_src),
        'comments': parse_comments(soup),
        'genres': pars_genres(soup),
    }


def download_image(url, folder):
    response = get_response(url)
    try:
        check_for_redirect(response)
    except requests.RequestException:
        return

    filename = urlsplit(url).path.split(sep='/')[-1]
    valid_filename = unquote(filename)
    file_path = os.path.join(folder, valid_filename)
    with open(file_path, 'wb') as file:
        file.write(response.content)


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
    image_folder = 'images'
    txt_folder = 'books'
    Path(f'./{image_folder}').mkdir(exist_ok=True)
    Path(f'./{txt_folder}').mkdir(exist_ok=True)

    for book_id in range(1, 11):
        head_url = 'https://tululu.org/'
        book_page_response = get_response(f'{head_url}b{book_id}')
        try:
            check_for_redirect(book_page_response)
        except requests.RequestException:
            continue

        book_card = parse_book_page(book_page_response)
        print(book_card['title'])
        print(book_card['genres'], '\n')
        continue
        download_image(book_card['image'], image_folder)

        title = book_card['title']
        download_txt(
            f'{head_url}txt.php?id={book_id}',
            f'{book_id}.{title}',
            txt_folder,
        )


def main():
    download_books()


if __name__ == '__main__':
    main()
