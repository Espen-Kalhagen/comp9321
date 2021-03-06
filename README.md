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

#### Authenticating

* Register a user by posting {"username": "username", "password": "password"} to /security/users.
* Log in by posting {"username": "username", "password": "password"} to /security/login.
* POST /security/login returns a bearer token for authentication.
* Generate an api key by posting to /security/keys with the header "Authorization: Bearer token".
* POST /security/keys will return your newly generated api key
* For accessing the api resources, send the header "X-API-KEY: key"

### Client
After starting the server visit http://127.0.0.1:5000/client/ to get the client file

