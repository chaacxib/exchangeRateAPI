import logging
import requests

from bs4 import BeautifulSoup
from datetime import datetime

FOD_URL = 'https://www.banxico.org.mx/tipcamb/tipCamMIAction.do'

def get_official_gazette_of_the_federation_data():
    """Scrape USD to MXN exchange price from Banxico Official Gazette Of The Federation
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

print(get_official_gazette_of_the_federation_data())