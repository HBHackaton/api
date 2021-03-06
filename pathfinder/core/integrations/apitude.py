from datetime import date, datetime
from json import dumps
from hashlib import sha256
from requests import post, HTTPError
from time import time
from os import environ
import logging as log

from .availability import get_destination_rq, get_geolocation_rq
from .checkrates import get_checkrate_rq
from .confirm import get_confirm_rq

apikey = environ['HOTELAPI_KEY']
secret = environ['HOTELAPI_SECRET']
base_uri = 'https://api.test.hotelbeds.com/hotel-api/1.0/'
hotels = 'hotels'
checkrates = 'checkrates'
confirmation = 'bookings'
headers = {
            'Api-Key': apikey,
            'Accept': 'application/json',
            'Content-Type': 'application/json; encoding=utf-8'
}


def __send_post(path, data):
    raw_sig = "{}{}{}".format(apikey, secret, int(time()))
    signature = sha256(raw_sig.encode('utf-8')).hexdigest()
    head = {**headers}
    head['X-Signature'] = signature

    response = post("/".join([base_uri, path]), headers=head, data=dumps(data))

    if response.status_code != 200:
        raise HTTPError("Apitude response code: [{}] {}".format(response.status_code, response.text))

    parsed_rs = response.json()
    if 'errors' in parsed_rs:
        raise HTTPError("Apitude response with errors: {}".format(parsed_rs['errors'][0]['text']))

    return parsed_rs


# availability
# All operations must return apitude whole response
# get by radio
# Performs an hotel search by giata code (destination)
def get_hotels_by_radio(longitude, latitude, radio, unit, checkin: date, checkout: date, age=900, name='Diego', surname='Farras', daily_rate=True):
    request = get_geolocation_rq(longitude, latitude, radio, unit, checkin, checkout, age, name, surname, daily_rate)
    log.info("get hotel by id RQ: {}".format(request))
    response = __send_post(hotels, request)
    log.info("gte hotel by id RS: {}".format(response))

    return response


# get by giata
# Performs an hotel search by giata code (destination)
def get_hotels_by_destination(destination, checkin: date, checkout: date, age=900, name='Diego', surname='Farras', daily_rate=True):
    request = get_destination_rq(destination, checkin, checkout, age, name, surname, daily_rate)
    response = __send_post(hotels, request)
    return response


# checkrates
# Receives a ratekey from any availability response, and returns checkrates response. It does not warranty ratekey usability!!!
def rate_check(ratekey):
    request = get_checkrate_rq(ratekey)
    response = __send_post(checkrates, request)
    return response


# confirm
def rate_confirm(ratekey, age, name, surname):
    request = get_confirm_rq(ratekey, age, name, surname)
    response = __send_post(confirmation, request)
    return response
