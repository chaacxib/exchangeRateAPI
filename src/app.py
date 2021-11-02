import logging
import operator
import requests

from functools import reduce
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta

FOD_URL = 'https://www.banxico.org.mx/tipcamb/tipCamMIAction.do'

BANXICO_URL = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno'
BANXICO_TOKEN = ''

def get_official_gazette_of_the_federation_data():
    """Scrape USD to MXN exchange price from 
    Banxico Official Gazette Of The Federation
    --------------------
    Parameters:
        None
    --------------------
    Returns:
        value: dict(str)
            Dictionary with structure { 'value': LAST_UPDATED_EXCHANGE_RATE}
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
    return({"value": data[0].get('Para pagos', 'N/A')})


def get_banxico_data():
    """Collect USD to MXN exchange price from 
    Banxico Economic Information System API
    --------------------
    Parameters:
        None
    --------------------
    Returns:
        value: dict(str)
            Dictionary with structure { 'value': LAST_UPDATED_EXCHANGE_RATE}
    """
    # Collect the last updated data from Banxico API in JSON format
    data = requests.get(BANXICO_URL, headers={'Bmx-Token': BANXICO_TOKEN}).json()

    # Extract exchange rate value and return it
    value = reduce(operator.getitem, ['bmx', 'series', 0, 'datos', 0, 'dato'], data)
    return({"value": value if value else 'N/A'})
