import logging

import prometheus_client
from flask import Flask
from flask import Response
from flask import request

import signal
import sys
import time

import requests
import threading
import os

import rollbar

from process_metrics import ProcessMetrics
from waitress import serve

do_continue = True
app = Flask(__name__)

#
#
# RUN INSTRUCTIONS:
# cd to the directory comtaining these files
# type the command below in a terminal window
#
# python3 app.py
#
#

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
ProcessMetrics.initialize_rollbar()

@app.route('/metrics', methods=['GET'])
def get_occurrence_metrics():
    """
    Return the metrics in a form that prometheus can consume
    """

    print('Starting to get occurrence metrics')

    global do_continue
    if do_continue == False:
        rollbar.report_message('do_continue is False. Not processing request')

    try:
        pm = ProcessMetrics()

        pm.get_metrics_for_multiple_projects()
        metrics = pm.generate_latest_metrics()

        resp = Response(metrics, status=200, mimetype='text/plain')
        print(resp)
        return resp

    except:
        rollbar.report_exc_info()
        msg = 'An error occurred processing the request for prometheus metrics'
        return Response(msg, status=500, mimetype='text/plain')
    finally:
        time.sleep(1)

    


def ctrlc_handler(sig, frame):
    print('You pressed Ctrl+C!. Exitting in 3 seconds.')
    do_continue = False

    time.sleep(3)
    print('Exitting')
    sys.exit(0)


def run_web_server():
    print('Starting this web application')
    rollbar.report_message('Starting the web server', level='info')

    port = os.environ.get('EXPORTER_PORT', '8083')

    url = 'http://localhost:{}/metrics'.format(port)
    print('Check this URL to confirm metrics are being processed')
    print(url)
    print('...')

    serve(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, ctrlc_handler)
    run_web_server()
    
