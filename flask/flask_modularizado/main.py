import unittest

from flask import Flask, request, jsonify
from app import create_app
from app.services.email_service import *


initialization = create_app() # Creating the app
app = initialization['app'] # Getting app information
#connection = initialization['connection'] # Getting connection to database information
init_email_service(app) # Intializing email service
app.extensions['mail'].debug = 0 # This silence the Flask_Mail logs

## Testing database connection
#print("PostgreSQL server information")
#print(connection.get_dsn_parameters(), "\n")

## Tests declaration
## Run flask test to test
@app.cli.command()
def test():
    tests = unittest.TestLoader().discover('tests') ## Looks for the directory tests
    unittest.TextTestRunner().run(tests) ## Run all the tests that have been found on the directory


## Routing declaration
@app.route('/', methods=['GET'])
def Main():
    try:
        print('ok in main route ')
        return jsonify({'success': True}), 200
    except Exception as e:
        print('error in main route', e)
        return jsonify({'success': False}), 500


# If uses flask run, run using the command: flask run --host=0.0.0.0 --port=4000
# If not just use python main.py
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)

