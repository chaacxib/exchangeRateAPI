from fastapi import FastAPI
from utils import get_official_gazette_of_the_federation_data, get_banxico_data, get_fixer_data

app = FastAPI()


@app.get("/")
async def root():
    result = {'rates':{}}

    result['rates']['diario de la fedearcion'] = get_official_gazette_of_the_federation_data()
    result['rates']['fixer'] = get_fixer_data()
    result['rates']['banxico'] = get_banxico_data()

    return result
