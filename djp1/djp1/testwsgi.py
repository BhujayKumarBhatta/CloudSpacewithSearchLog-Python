#!/usr/bin/python
'''
Created on Jul 30, 2016

@author: cisco
'''
def application(environ, start_response):
    status = '200 OK'
    output = 'Hello Babu!'

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]