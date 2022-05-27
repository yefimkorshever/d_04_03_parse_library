import requests


url = "https://tululu.org/txt.php?id=32168"

response = requests.get(url)
response.raise_for_status()

filename = 'tmp/sands_of_mars.txt'
with open(filename, 'w', encoding='utf-8') as file:
    file.write(response.text)
