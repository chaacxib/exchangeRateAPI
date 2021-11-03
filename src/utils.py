import os
import logging
import operator
import requests

from functools import reduce
from database import Request
from bs4 import BeautifulSoup

from datetime import datetime, timedelta

MAX_REQUESTS = 5

FOD_URL = 'https://www.banxico.org.mx/tipcamb/tipCamMIAction.do'

BANXICO_TOKEN = os.environ['BANXICO_TOKEN']
BANXICO_URL = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno'

FIXER_API_KEY = os.environ['FIXER_API_KEY']
FIXER_URL = 'https://data.fixer.io/api/latest?access_key={api_key}&base=USD&symbols=MXN'


def get_official_gazette_of_the_federation_data():
    """Scrape USD to MXN exchange price from 
    Banxico Official Gazette Of The Federation
    --------------------
    Parameters:
        None
    --------------------
    Returns:
        value: dict(str)
            Dictionary with structure { 'last_updated': LAST_UPDATED_DATE,'value': LAST_UPDATED_EXCHANGE_RATE}
    """
    try:
        # Parse banxico data in beautiful soup
        data = requests.get(FOD_URL).text
        soup = BeautifulSoup(data, 'html.parser')

        # Extract title row
        title_row = soup.find('tr', class_='renglonTituloColumnas')
        titles = [title.text.strip().rsplit(' ', 1)[0].rstrip() for title in title_row.find_all('td')]

        # Find data rows
        pair_rows = soup.find_all('tr', class_='renglonPar')
        none_rows = soup.find_all('tr', class_='renglonNon')

        # Extract rows data and generate dictionary for each row
        data = []
        for row in none_rows + pair_rows:
            row_data = [td.text.strip() for td in row.find_all('td')]
            data.append(dict(zip(titles, row_data)))

        # Sort data bydate to return last value
        data.sort(key=lambda item:datetime.strptime(item['Fecha'], '%d/%m/%Y'), reverse=True)
    except Exception as e:
        logging.error(str(e))

    # Return last updated value if no error was found, if not returns N/A
    result = {
        "last_updated": data[0].get('Fecha', 'N/A'),
        "value": data[0].get('Para pagos', 'N/A')
    }
    return result


def get_banxico_data():
    """Collect USD to MXN exchange price from 
    Banxico Economic Information System API
    --------------------
    Parameters:
        None
    --------------------
    Returns:
        value: dict(str)
            Dictionary with structure { 'last_updated': LAST_UPDATED_DATE,'value': LAST_UPDATED_EXCHANGE_RATE}
    """
    rate = {}
    try:
        # Collect the last updated data from Banxico API in JSON format
        data = requests.get(BANXICO_URL, headers={'Bmx-Token': BANXICO_TOKEN}).json()

        # Extract exchange rate value
        rate = reduce(operator.getitem, ['bmx', 'series', 0, 'datos', 0], data)
    except Exception as e:
        logging.error(str(e))

    result = {
        "last_updated": rate['fecha'] if rate else 'N/A',
        "value": rate['dato'] if rate else 'N/A'
    }

    return result


def get_fixer_data():
    """Collect USD to MXN exchange price from Fixer API
    --------------------
    Parameters:
        None
    --------------------
    Returns:
        value: dict(str)
            Dictionary with structure { 'last_updated': LAST_UPDATED_DATE,'value': LAST_UPDATED_EXCHANGE_RATE}
    """
    data = None

    try:
        # Collect the last updated data from Fixer API in JSON format
        data = requests.get(FIXER_URL.format(api_key=FIXER_API_KEY)).json()
    except Exception as e:
        logging.error(str(e))

    # Validate request result and assign values to response message
    if data is not None and data['success']:
        result = {
            "last_updated": data['date'],
            "value": data['rates']['MXN']
        }
    else:
        result = {
            "last_updated": 'N/A',
            "value": 'N/A'
        }
    
    return result


def max_requests(username):
    requests = Request.count(username, Request.datetime >= datetime.utcnow() - timedelta(minutes=30))

    if requests >= MAX_REQUESTS:
        return True
    return False