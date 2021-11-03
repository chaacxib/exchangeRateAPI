# Exchange Rate API

Web service which exposes the current exchange rate of USD to MXN from three
different sources in the same endpoint.

The response format is presented as:
~~~[json]
{
  "rates":{
    "provider_1":{
      "last_updated":"2018-04-22T18:25:43.511Z",
      "value":20.4722
    },
    "provider_2_variant_1":{
      "last_updated":"2018-04-23T18:25:43.511Z",
      "value":20.5281
    }
  }
}
~~~

This project collects data from the following providers:

*  [Diario Oficial de la Federación](https://www.banxico.org.mx/tipcamb/tipCamMIAction.do)
* [Fixer](https://fixer.io/)
* [Banxico](https://www.banxico.org.mx/SieAPIRest/service/v1/doc/consultaDatosSerieRango)

## Main Points to cover
* API should be accessed with an Application Token
* API should have a rate limit per user
* The project should be Dockerized

## How is deployed
This application is deployed as a lambda Function inside AWS Services Cloud. It uses as main technologies:
* AWS Lambda
* AWS API Gateway
* AWS DynamoDB

## To Do
* Create deploy instructions
* Create CI/CD Pipeline

## How to create the lambda layer Zip
~~~
docker run --rm -v $(pwd):/foo -w /foo lambci/lambda:build-python3.8 pip install -r requirements.txt -t python

zip -r requirements.zip python

sudo rm -r python
~~~