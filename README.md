# comp9321
Data Services Engineering assignment 2

## Architecture

API consits of a  data pre processing and macine learning model that is trained in batches, i.e. once a day.
The API then loads this model and uses it to serve predictions.

The frontend is a static file that uses VUE to request data from the API

