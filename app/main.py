import requests

from typing import List

from fastapi import FastAPI, Path
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware

cors_origins = [
    'https://www.govdirectory.org',
    'https://www.wikidata.org',
]

user_agent_external = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0 Govdirectory.org account existence checker'
user_agent_wikimedia = 'Wikidata:WikiProject Govdirectory (health check service)'

url_properties = [
    {
        'name': 'official website',
        'prop': 'P856',
    },
    {
        'name': 'URL for citizen\'s initiatives',
        'prop': 'P9732',
    },
]

platform_properties = [
    {
        'name': 'Twitter username',
        'prop': 'P2002',
        'formatter_url': 'https://twitter.com/$1',
    },
    {
        'name': 'YouTube channel ID',
        'prop': 'P2397',
        'formatter_url': 'https://www.youtube.com/channel/$1',
    },
    {
        'name': 'Facebook ID',
        'prop': 'P2013',
        'formatter_url': 'https://www.facebook.com/$1',
    },
    {
        'name': 'Instagram username',
        'prop': 'P2003',
        'formatter_url': 'https://www.instagram.com/$1/',
    },
    {
        'name': 'GitHub username',
        'prop': 'P2037',
        'formatter_url': 'https://github.com/$1',
    },
    {
        'name': 'Vimeo identifier',
        'prop': 'P4015',
        'formatter_url': 'https://vimeo.com/$1',
    },
    {
        'name': 'Flickr user ID',
        'prop': 'P3267',
        'formatter_url': 'https://www.flickr.com/people/$1',
    },
    {
        'name': 'Pinterest username',
        'prop': 'P3836',
        'formatter_url': 'https://www.pinterest.com/$1/',
    },
    {
        'name': 'Dailymotion channel ID',
        'prop': 'P2942',
        'formatter_url': 'https://www.dailymotion.com/$1',
    },
    {
        'name': 'TikTok username',
        'prop': 'P7085',
        'formatter_url': 'https://www.tiktok.com/@$1',
    },
    {
        'name': 'SlideShare username',
        'prop': 'P4016',
        'formatter_url': 'https://www.slideshare.net/$1',
    },
]

def check_url(url: HttpUrl):
    r = requests.head(url, headers={ 'User-Agent': user_agent_external, 'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br' })
    if r.status_code >= 400:
        return r.status_code
    return None

app = FastAPI(
    title='Govdirectory Health Check Service',
    description='Microservice that validates various external identifiers and URLs associated with a given Wikidata identifier.',
    version='0.1.0',
    docs_url='/',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=['GET'],
    allow_headers=['*'],
)

class Error(BaseModel):
    prop: str
    prop_name: str
    url: HttpUrl
    status_code: int

@app.get('/{qid}', response_model=List[Error])
async def read_item(qid: str = Path(..., title='Wikidata identfier', min_length=2, regex='^Q\d+$')):
    r = requests.get('https://www.wikidata.org/w/api.php?action=wbgetentities&props=claims&utf8=1&format=json&ids=' + qid, headers={ 'User-Agent': user_agent_wikimedia })
    item_statements = list(r.json()['entities'][qid]['claims'].items())

    errors = []

    for p in url_properties:
        for claim in item_statements:
            if not claim[0] == p['prop']:
                continue

            for statement in claim[1]: # needed in case a prop has several values
                url = statement['mainsnak']['datavalue']['value']
                negative_status = check_url(url)
                if negative_status:
                    error = {
                        'prop': p['prop'],
                        'prop_name': p['name'],
                        'url': url,
                        'status_code': negative_status,
                    }
                    errors.append(error)

    for p in platform_properties:
        for claim in item_statements:
            if not claim[0] == p['prop']:
                continue

            for statement in claim[1]: # needed in case a prop has several values
                identifier = statement['mainsnak']['datavalue']['value']
                url = p['formatter_url'].replace('$1', identifier, 1)
                negative_status = check_url(url)
                if negative_status:
                    error = {
                        'prop': p['prop'],
                        'prop_name': p['name'],
                        'url': url,
                        'status_code': negative_status,
                    }
                    errors.append(error)

    return errors
