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
After installing flask and other dependensies, run the main file in the server

### Client
Open the index.html file in client in any web browser
