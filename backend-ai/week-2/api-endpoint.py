import flask
import csv
from flask import request
import logging
app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return flask.jsonify({'message': 'This is the first assignment of Week-1'}), 200
@app.route('/status', methods=['GET'])
def status():
    try:
        if request.method == 'GET':
            return flask.jsonify({'status': 'ok'}), 200
            logger.info('Status 200, OK')
        else:
            return flask.jsonify({'client error': 'Method not allowed'}), 405
            logger.error('Status 405, Method not allowed')
    except Exception as e:
        return flask.jsonify({'server error': str(e)}), 500
        logger.critical('Status 500, Internal Server Error')
          
@app.route('/data', methods=['GET'])
def data():
    try:
        if request.method == 'GET':
            with open('sample_data.csv', 'r') as file:
                reader = csv.DictReader(file)
                data = [row for row in reader]
            return flask.jsonify(data), 200
            logger.info('Status 200, Data retrieved successfully')
        else:
            return flask.jsonify({'client error': 'Method not allowed'}), 405
            logger.error('Status 405, Method not allowed')
    except FileNotFoundError:
        return flask.jsonify({'server error': 'Data file not found'}), 500
        logger.critical('Status 500, Data file not found')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    app.run(debug=True)
                

