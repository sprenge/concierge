from bs4 import BeautifulSoup

with open('utc.html', 'r') as f:
    contents = f.read()
    soup = BeautifulSoup(contents, 'lxml')
    rows = soup.findAll('tr')
    for row in rows:
        print('---')
        print(row)
