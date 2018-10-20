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

work_photographer = Photographer()


def take_screenshot(ch, method, properties, body):
    logging.info('Received job %r' % body)
    job_body = json.loads(body)
    job_id = job_body.get('job_id')
    job_url = job_body.get('url')
    try:
        img_base64 = work_photographer.take_screenshot(job_url)
        redis_conn.hset(job_id, job_url, img_base64)
    except:
        redis_conn.hset('status_' + job_id, 'status', 'Error')
        redis_conn.hset(job_id, job_url, 'Could not take screenshot.')
    ch.basic_ack(delivery_tag=method.delivery_tag)


def consume_jobs():
    logging.info('Waiting for screenshot jobs.')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(take_screenshot, queue='screenshot')

    channel.start_consuming()


if __name__ == '__main__':
    consume_jobs()
