import os
import flask
from flask import Flask, request, jsonify
from database_client import create_table, insert_data, populate_random_data, get_all_data, get_data_by_id, update_data, delete_data, delete_all_data
from redis_client import (
    get_data as redis_get_data, 
    get_all_data as redis_get_all_data, 
    set_data as redis_set_data, 
    delete_data as redis_delete_data, 
    update_data as redis_update_data, 
    insert_random_data as redis_insert_random_data
)
from dotenv import load_dotenv
load_dotenv()
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.getenv('DATABASE_URL')

@app.route('/', methods=['GET'])
def home():
    return flask.jsonify({'message': 'This is the second assignment of Week-2'}), 200

@app.route('/status', methods=['GET'])
def status():
    try:
        if request.method == 'GET':
            return flask.jsonify({'status': 'ok'}), 200
            logging.info('Status 200, OK')
        else:
            return flask.jsonify({'client error': 'Method not allowed'}), 405
            logging.error('Status 405, Method not allowed')
    except Exception as e:
        return flask.jsonify({'server error': str(e)}), 500
        logging.critical('Status 500, Internal Server Error')

@app.route('/data', methods=['GET', 'POST', 'PUT', 'DELETE'])
def data():
    if request.method == 'GET':
        data = get_all_data()
        return jsonify(data), 200
    elif request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        name = data.get('name')
        age = data.get('age') 
        department = data.get('department')
        academic_year = data.get('academic_year')
        sgpa = data.get('sgpa')

        if not all([name, age, department, academic_year, sgpa]):
            return jsonify({'error': 'name, age, department, academic_year, and sgpa are required'}), 400

        insert_data(name, age, department, academic_year, sgpa)
        return jsonify({'message': 'Data inserted successfully'}), 201
    elif request.method == 'PUT':
        data = request.get_json()
        update_data(data['id'], data['name'], data['age'], data['department'], data['academic_year'], data['sgpa'])
        return jsonify({'message': 'Data updated successfully'}), 200
    elif request.method == 'DELETE':
        data = request.get_json()
        delete_data(data['id'])
        return jsonify({'message': 'Data deleted successfully'}), 200

@app.route('/redis-data', methods=['GET', 'POST', 'PUT', 'DELETE'])
def redis_data():
    if request.method == 'GET':
        data=redis_get_all_data()
        return flask.jsonify(data), 200
    elif request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        key = data.get('key')
        value = data.get('value')
        if not all([key, value]):
            return jsonify({'error': 'key and value are required'}), 400
        redis_set_data(key, value)
        return jsonify({'message': 'Data inserted successfully'}), 201
    elif request.method == 'PUT':
        data = request.get_json()
        redis_update_data(data['key'], data['value'])
        return jsonify({'message': 'Data updated successfully'}), 200
    elif request.method == 'DELETE':
        data = request.get_json()
        redis_delete_data(data['key'])
        return jsonify({'message': 'Data deleted successfully'}), 200
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    app.run(debug=True, host='0.0.0.0', port=5000)
