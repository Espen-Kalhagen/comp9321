# comp9321
Data Services Engineering assignment 2

## Architecture

API consits of a data pre processing and macine learning model that is trained in batches, i.e. once a day.
The API then loads this model and uses it to serve predictions.
The API also uses the data sources to provide various functionality to the user
The API is secured using username password with json web tokens for the administrative functions,
and API keys administrated using the admin functions for the general features.

The frontend is a static file that uses VUE to request data from the API

## How to run

### Server
* Install the dependencies described in requirements.txt
* run the main file in the server

The API is available at http://127.0.0.1:5000/
and the API swagger documentation is available at http://127.0.0.1:5000/

### Client
After starting the server visit http://127.0.0.1:5000/client/ to get the client file

