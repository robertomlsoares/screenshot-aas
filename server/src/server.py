#!/usr/bin/python
# coding: utf-8

"""
    server
    ~~~~~~

    This is a screenshot-as-a-service application used to take screenshots
    of URLs provided by the users.

    :copyright: (c) 2018 Roberto Soares
    :license: GPL-3.0
"""

import json
import os
import uuid

import pika
from flask import Flask, abort, request
from redis import Redis

from server_exceptions import MissingParameter

app = Flask(__name__)

redis_conn = Redis(os.environ.get('REDIS_IP'))


def _enqueue_urls(urls):
    """
    Receives a list of URLs and puts them in a job queue that workers will
    consume to take screenshots. This function returns a unique job id to be
    used on a GET request to /screenshot/<job_id> in order to retrieve the
    results of the job.

    :param urls (list): List of URLs.
    :return: A unique job id. Used to retrieve the job results.
    """

    job_id = uuid.uuid4().hex
    redis_conn.hmset('status_' + job_id,
                     {'status': 'Processing', 'amount': len(urls)})
    rabbit_conn = pika.BlockingConnection(
        pika.ConnectionParameters(os.environ.get('RABBIT_IP')))
    channel = rabbit_conn.channel()
    channel.queue_declare(queue='screenshot', durable=True)
    job_body = {'job_id': job_id}
    for url in urls:
        job_body['url'] = url
        channel.basic_publish(exchange='', routing_key='screenshot',
                              body=json.dumps(job_body),
                              properties=pika.BasicProperties(delivery_mode=2))
    rabbit_conn.close()
    return job_id


def _handle_post_screenshot(req_data):
    """
    Handler for a POST on /screenshot.

    :param req_data (dict): Request payload.
    :return: A unique id related to the request. It is used to retrieve the
    screenshots by sending a GET to /screenshot/<job_id>.
    """

    urls = req_data.get('urls')
    if not urls:
        raise MissingParameter(
            'Invalid request. Please provide at least one URL.')
    return _enqueue_urls(urls)


def _handle_get_screenshot(job_id):
    """
    Handler for a GET on /screenshot/<job_id>.

    :param job_id (str): The id of the job responsible for taking screenshots.
    :return: If the job has finished, it will return a dict where each key is
    the name of the URL that was requested and each value is the screenshot in
    base64 format. Otherwise, it will return a string corresponding to the job
    status.
    """

    job = redis_conn.hgetall('status_' + job_id)
    job_data = redis_conn.hgetall(job_id)
    if job['status'] == 'Ready':
        return json.dumps(job_data)
    if int(job['amount']) == len(job_data):
        redis_conn.hset('status_' + job_id, 'status', 'Ready')
        return json.dumps(job_data)
    if job['status'] == 'Processing':
        return 'We are still processing your request. Try again later.'
    return 'There was a problem when taking your screenshots.'


@app.route('/screenshot', methods=['POST'])
@app.route('/screenshot/<string:job_id>', methods=['GET'])
def post_screenshot(job_id=None):
    """
    Route used to request and retrieve screenshots.
    When requesting, use a POST request with the payload containing a key named
    'urls' where the value is a list of URLs.
    When retrieving, use a GET request with the job id at the end of the route
    (/screenshot/<job_id>).

    :param job_id (str): Id of the job when using a GET request.
    :return: For the POST request, it returns an id that is used to retrieve
    the screenshots with the GET request. For the GET request, it returns the
    screenshots (if they are ready) in base64 format or a string corresponding
    to the job status.
    """

    if request.method == 'POST':
        return _handle_post_screenshot(request.get_json())
    elif request.method == 'GET':
        return _handle_get_screenshot(job_id)
    else:
        abort(404)
