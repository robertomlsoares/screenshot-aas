# coding: utf-8

"""
    config
    ~~~~~~

    Configuration file for gunicorn.

    :copyright: (c) 2018 Roberto Soares
    :license: GPL-3.0
"""

import os

bind = '0.0.0.0:' + os.environ.get('SERVER_PORT', '5000')
