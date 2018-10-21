#!/usr/bin/python
# coding: utf-8

"""
    client
    ~~~~~~

    Testing client that will use the screenshot-aas API.

    :copyright: (c) 2018 Roberto Soares
    :license: GPL-3.0
"""

import base64
import hashlib
import json
import os
import time

import requests


def main():
    with open('payload.json', 'rb') as payload:
        headers = {'Content-Type': 'application/json'}
        r_post = requests.post(
            'http://127.0.0.1:5000/screenshot', data=payload, headers=headers)
    job_id = r_post.text

    r_get = requests.get('http://127.0.0.1:5000/screenshot/%s' % job_id)
    get_result = r_get.text

    while get_result == 'We are still processing your request. Try again later.':
        print get_result
        print 'Trying again in 3 seconds...'
        time.sleep(3)
        r_get = requests.get('http://127.0.0.1:5000/screenshot/%s' % job_id)
        get_result = r_get.text

    if get_result == 'There was a problem when taking your screenshots.':
        print get_result
        return

    print 'Job has finished. Saving screenshots...'
    get_result = json.loads(get_result)

    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    for url in get_result:
        file_data = get_result.get(url)
        file_name = hashlib.md5(url).hexdigest()
        with open('screenshots/' + file_name + '.png', 'wb') as img_f:
            img_data = base64.decodestring(file_data)
            img_f.write(img_data)


if __name__ == '__main__':
    main()
