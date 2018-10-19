# coding: utf-8

"""
    missing_parameter
    ~~~~~~~~~~~~~~~~~

    Exception class to be raised when an endpoint is hit with missing
    parameters.

    :copyright: (c) 2018 Roberto Soares
    :license: GPL-3.0
"""


class MissingParameter(Exception):

    def __init__(self, message):
        self.status_code = 400
        self.message = message

    def to_dict(self):
        return {'message': self.message}
