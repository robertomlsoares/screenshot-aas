#!/usr/bin/python
# coding: utf-8

"""
    worker
    ~~~~~~

    Worker class used to consume jobs from a RabbitMQ queue. The queue has URLs
    that this worker will screenshot and save on Redis.

    :copyright: (c) 2018 Roberto Soares
    :license: GPL-3.0
"""

import json
import logging
import os

import pika
from redis import Redis

from photographer import Photographer

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(name)s - %(message)s', level=logging.INFO)

redis_conn = Redis(os.environ.get('REDIS_IP'))

rabbit_conn = pika.BlockingConnection(
    pika.ConnectionParameters(os.environ.get('RABBIT_IP')))
channel = rabbit_conn.channel()
channel.queue_declare(queue='screenshot', durable=True)


def take_screenshot(ch, method, properties, body):
    """
    This is the job's main function: taking a screenshot of a website and
    returning the base64 data of the image. It will receive the URL from
    RabbitMQ and save the data of the image on Redis.

    :param ch (dict): RabbitMQ channel.
    :param method (dict): Method from RabbitMQ. Used to send ACK messages.
    :param properties (dict): Dict of properties of the RabbitMQ channel.
    :param body (str): Body of the message. String in a JSON format.
    """

    logging.info('Received job %r' % body)
    work_photographer = Photographer()
    job_body = json.loads(body)
    job_id = job_body.get('job_id')
    job_url = job_body.get('url')
    try:
        img_base64 = work_photographer.take_screenshot(job_url)
        redis_conn.hset(job_id, job_url, img_base64)
    except Exception as e:
        redis_conn.hset('status_' + job_id, 'status', 'Error')
        redis_conn.hset(job_id, job_url, 'Could not take screenshot.')
        logging.warn(e)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_jobs():
    """
    Main loop of the worker. It will bind to a RabbitMQ channel and work on its
    messages.
    """

    logging.info('Waiting for screenshot jobs.')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(take_screenshot, queue='screenshot')

    channel.start_consuming()


if __name__ == '__main__':
    consume_jobs()
