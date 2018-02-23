from flask import Flask, jsonify, request
from datetime import datetime
from core.ancillaries import get_integration_ancillaries
import os
import logging
from core import activities


def init_logger():
    level = logging.INFO
    if 'LOG_LEVEL' in os.environ:
        if os.environ['LOG_LEVEL'] == 'DEBUG':
            level = logging.DEBUG
        elif os.environ['LOG_LEVEL'] == 'INFO':
            level = logging.INFO
        elif os.environ['LOG_LEVEL'] == 'WARNING':
            level = logging.WARNING

    logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s', level=level)

init_logger()
start_time = datetime.now()
app = Flask(__name__)


@app.route('/health', methods=['GET'])
def info():
    global start_time
    response = {
        'error': "",
        'msg': "Hello World",
        'started_at': str(start_time)
    }

    return jsonify(response)


@app.route('/activities', methods=['POST'])
def get_acivities():
    logging.info("recieved activities request")
    data = request.get_json()

    ori = (data['origin']['lon'], data['origin']['lat'])
    dst = (data['destination']['lon'], data['destination']['lat'])
    checkin = datetime.strptime(data['checkin'], '%d-%m-%Y')
    checkout = datetime.strptime(data['checkout'], '%d-%m-%Y')

    acts = activities.get_activities_path(ori, dst, checkin, checkout)

    return jsonify({'activities': acts})


@app.route('/ancillaries', methods=['POST'])
def get_ancillaries():
    logging.info("recieved ancillaries request")
    data = request.get_json()
    inDate = datetime.strptime(data['checkin'], '%d-%m-%Y')
    outDate = datetime.strptime(data['checkout'], '%d-%m-%Y')
    response = get_integration_ancillaries(data['lon'], data['lat'], inDate, outDate)
    return jsonify(response)


@app.route('/agenda', methods=['POST'])
def make_agenda():
    logging.info("recieved agenda request")
    data = request.get_json()
    agenda_id = 'A1234'
    if 'id' in data and data['id']:
        agenda_id = data['id']
    response = { 'id': agenda_id }

    return jsonify(response)


@app.errorhandler(500)
def error_handler(ex):
    logging.error(str(ex))
    return jsonify({'error': str(ex)}), 500
