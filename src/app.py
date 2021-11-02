import requests
from bs4 import BeautifulSoup

FOD_URL = 'https://www.banxico.org.mx/tipcamb/tipCamMIAction.do'

def get_federation_official_diary_data():
    data = requests.get(FOD_URL).text
    soup = BeautifulSoup(data, 'html.parser')

    title_row = soup.find('tr', class_='renglonTituloColumnas')
    titles = [title.text.strip().split(' ', 1)[0].rstrip() for title in title_row.find_all('td')]
    
    pair_rows = soup.find_all('tr', class_='renglonPar')
    none_rows = soup.find_all('tr', class_='renglonNoN')

    data = []
    for td in title_row.find_all('td'):
        td.text.strip()

get_federation_official_diary_data()