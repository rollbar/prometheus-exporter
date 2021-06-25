
from __future__ import print_function

import json
import sys
import time
import requests
import rollbar
from occurrence import Occurrence

URL_PATH = 'https://api.rollbar.com/api/1/instances'


VERSIONS_URL_PATH = \
    'https://api.rollbar.com/api/1/versions/{}' 

# only look at occurrences less than 10 minutes old
MAX_LOOK_BACK_SECONDS = 600


def stream_occurrences(read_token, project_slug, last_id=None):
    """
    read_token: Rollbar project_access_token with read_scope
    project_slug: The name of the project that this token is for
    last_id: The lowest occurence_id we are interested in

    returns: 
            Occurrence list 
            Highest occurrence_id in the returned list (None if list empty)
    """

    now_epoch_seconds = int(time.time())

    occ_list = []
    occ_list, highest_id, lowest_id = get_occurrence_batch(read_token, 
                                                           project_slug)

    if last_id == None:
        print('last_id was None')
        last_id = lowest_id

    while lowest_id > last_id:
        batch_list, highest_id, lowest_id = \
            get_occurrence_batch(read_token, project_slug, lowest_id)
        occ_list = occ_list + batch_list

        if not continue_getting_occs(occ_list, now_epoch_seconds):
            break

    occ_list = [x for x in occ_list if x.id > last_id]
    occ_list.sort(key=lambda x: x.id, reverse=True)

    max_id = None
    if len(occ_list) > 0:
        max_id = occ_list[0].id
    else:
        max_id = last_id

    return occ_list, max_id


def get_occurrence_batch(project_read_token, project_slug, last_id=None):
    """
    returns: list of 'Occurrence' objects
             highest_id in the batch (None if list is empty)
             lowest_id in the batch (None if list is empty)
    """

    headers = {'X-Rollbar-Access-Token': project_read_token}
    params = {}
    if last_id != None:
        params = {'lastId': str(last_id)}
    
    resp = requests.get(URL_PATH, headers=headers, params=params)
    log_api_call('get_occurrences', resp.status_code)
    
    if resp.status_code == 403:
        print('##')
        print('## HTTP 403 Error. Are the Project and Access Token Correct')
        print('## project_slug=', project_slug)
        print('##')

        msg = '403 Error project_slug={}'.format(project_slug)
        dct = {}
        dct['response_text'] = resp.text
        rollbar.report_message(msg, level='error', extra_data=dct)  
        return [], None, None
    
    if resp.status_code != 200:
        msg = 'HTTP ERROR={} project_slug={}'.format(resp.status_code, project_slug)
        msg = msg

        dct = {}
        dct['response_text'] = resp.text
        rollbar.report_message(msg, level='error', extra_data=dct)  
        return [], None, None     

    result = resp.json()
    
    print('##')
    print('## request.status_code=', resp.status_code)
    print('##')

    occ_list = []
    if result['err'] == 0:
        for elem in result['result']['instances']:
            occ = create_occurrence(elem)
            occ_list.append(occ)

    lowest_id = None
    highest_id = None
    if len(occ_list) > 0:
        lowest_id = min([x.id for x in occ_list])
        highest_id = max([x.id for x in occ_list])
    
    return occ_list, highest_id, lowest_id


def continue_getting_occs(occ_list, start_epoch_time):
    """
    If the oldest occurrence in the list less than
    MAX_LOOK_BACK_SECONDS ago, continue getting occurences

    We dont want old occurrence data. 
    """

    do_continue = False

    if len(occ_list) > 0:
        lowest_id = min([x.id for x in occ_list])
        lowest_occ = [x for x in occ_list if x.id == lowest_id][0]
        lowest_time_stamp = lowest_occ.timestamp
        max_look_back_time = start_epoch_time - MAX_LOOK_BACK_SECONDS

        if lowest_time_stamp > max_look_back_time:
            do_continue = True
        else:
            msg = 'Enough occurrences. We have looked back {} seconds'
            msg = msg.format(MAX_LOOK_BACK_SECONDS)
            print(msg)

    return do_continue


def create_occurrence(elem):
    """
    elem: A dictionary of dictionaries that contains 
          the data about a single occurrence returned 
          from the Rollbar API
 
    returns: An Occurrence object from the contents of elem
    """

    environment = 'none'
    if 'environment' in elem['data']:
        environment = elem['data']['environment']

    code_version = 'not_defined'
    if 'code_version' in elem['data']:
        code_version = elem['data']['code_version']

    level = elem['data']['level']
    occ_obj = Occurrence(elem['id'], elem['item_id'], elem['timestamp'],
                         level, environment, code_version)
    
    return occ_obj

def get_version_aggregate_stats(proj_name, code_version,
                                access_token, environment):

    url = VERSIONS_URL_PATH.format(code_version)

    resp = None
    try:
        params = {'environment': environment}
        headers = {'X-Rollbar-Access-Token': access_token}

        resp = requests.get(url, params=params, headers=headers)

        if resp.status_code == 403:
            print('##')
            print('## HTTP 403 Error. Are the Project and Access Token Correct')
            print('##')

            msg = '403 Error project_slug={}'.format(proj_name)
            dct = {}
            dct['response_text'] = resp.text
            rollbar.report_message(msg, level='error', extra_data=dct)  
            return None
    
        if resp.status_code != 200:
            msg = 'HTTP ERROR={} project_slug={}'.format(resp.status_code, proj_name)
            
            dct = {}
            dct['response_text'] = resp.text
            rollbar.report_message(msg, level='error', extra_data=dct)  
            return None


    except Exception as ex:
        print('Error making request to Rollbar Versions API', ex)


    log_api_call('versions', resp.status_code)
    print('##')
    print('## Rollbar Versions API status_code=', resp.status_code)
    print('##')

    json_stats = json.loads(resp.text)
    json_result = json_stats['result']

    return json_result

def log_api_call(api, status_code):
    msg = 'API Call={} status_code={}'.format(api, status_code)
    rollbar.report_message(msg, level='info')
