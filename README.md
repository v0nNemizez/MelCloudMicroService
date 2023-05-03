# Melcloud Microservice

App for communication with the MelCloud API. A part of Simens SmartHome setup.


### Features

* Flask-app with endpoints to control Air-to-Air heating pump connected to the Melcloud Cloud Service
* Data from the api is served as Prometheus metrics for monitoring (Temprature, Fanspeed etc.)


### Setup
* Create a config.json in app folder with the following format:

```json
{
  "username": "",
  "password": ""
}

```

* Build and deploy dockerimage locally by running app/build_and_deploy.sh


### Limitations
* This app is as of now ment for local deployment. If you want to deploy this to a cloud service, implementation of 
additional security and authentication is needed (this is a work in progress).

* You can only control one device pr class instance.

* As of now, not all ATA-heater functions are implimented. 


# PULL REQUESTS ARE WELCOME!






