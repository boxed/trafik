from pathlib import Path

import requests
from bs4 import BeautifulSoup


def s(c):
    return BeautifulSoup(c, "html.parser")


base = 'https://www.transportstyrelsen.se'


def scrape_index():
    x = s(requests.get(base + '/sv/vagtrafik/vagmarken/').content)
    for a in (x.select('.list-group-item a')):
        href = a.attrs['href']
        if "vagmark" not in href:
            continue

        if '/om-' in href:
            continue
        print(href)


def scrape_images(url):
    x = s(requests.get(base + url).content)
    for roadsign in x.select('.roadsign'):
        #print(roadsign)
        image_url = base + roadsign.select('img')[0].attrs['src']
        name = roadsign.select('span')[0].text.partition('.')[-1].strip() + '.gif'

        r = requests.get(image_url, stream=True)
        with open(Path('.').parent / 'images' / name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)


scrape_images('/sv/vagtrafik/vagmarken/Anvisningsmarken/')


def create_deck():
    import genanki
    my_model = genanki.Model(
        2075990655,
        'Simple image model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ]
    )
    my_deck = genanki.Deck(48475447053, 'Trafikmärken')
    filenames = []
    for f in (Path('.').parent / 'images').iterdir():
        filenames.append(str(f.absolute()))
        my_note = genanki.Note(
            model=my_model,
            fields=[f'<img src="{f.name}">', str(f.name.partition('.')[0])],
        )
        my_deck.add_note(my_note)

    package = genanki.Package(my_deck)
    package.media_files = filenames
    package.write_to_file(Path('.').parent / 'trafik.apkg')


create_deck()
