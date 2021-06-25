import requests
import logging
import os.path
import rollbar

from occurrence import Occurrence
from stream_occurrences import stream_occurrences

from item_metric import ItemMetric
from version_metric import VersionMetric


"""
Miscellaneous methods to help groups occurrences so
they can be converted into Prometheus metrics easily
"""

def read_starting_occ_from_file(project_slug):
    """
    OCCURRENCE_FILE contains the occurrence ID
    that we will start processing next
    """

    occ_id = None
    file_path = get_project_file(project_slug)
    if os.path.isfile(file_path):
        with open(file_path) as f:
            first_line = f.readline()
            occ_id = int(first_line.strip())

    return occ_id


def write_starting_occ_to_file(project_slug, occ_id):
    """
    update OCCURRENCE_FILE with the latest occ_id we next want to process
    """

    file_path = get_project_file(project_slug)
    with open(file_path, mode='w') as f:
        f.write(str(occ_id))


def get_project_file(project_slug):
    """
    For each project there is a small file that contains the
    newest occurrence ID that we want to get data for

    returns: The path of ths project file
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = '{}/{}.txt'.format(dir_path, project_slug)

    return file_path


def get_new_occurrences(project_slug, proj_read_token):
    """
    project_slug: The name of the Rollbar project
    poj_read_token: A Rollbar project access token with read scope

    returns: 2 dictionaries
             Dictionary Items data
             Dictionary of metrics for each code_version
    """
    curr_max_occ_id = read_starting_occ_from_file(project_slug)

    occ_list, max_id = stream_occurrences(proj_read_token, project_slug,
                                          last_id=curr_max_occ_id)
    msg = 'project_slug={} occurrence_count={} max_occurrence_id={}'
    msg = msg.format(project_slug, len(occ_list), max_id)
    rollbar.report_message(msg, level='info')

    item_dict = group_occurrences_into_items(occ_list)
    versions_dict = group_occurrences_into_versions(occ_list)

    num_occs = len(occ_list)
    
    print('##')
    print('###################################')
    print('##')
    print('##', project_slug)
    print('##')
    print('## Number of Code Versions', len(versions_dict))
    print('## Number of Items', len(item_dict))
    print('## Number of Occurrences', len(occ_list))
    print('##')
    print('###################################')
    print('##')

    write_starting_occ_to_file(project_slug, max_id)

    return item_dict, versions_dict


def group_occurrences_into_items(occ_list):
    """
    returns: A dictionary of items 
             key=item_id 
             value=occurrence list for that item_id
    """

    item_dict = {}
    if len(occ_list) > 0:
        max_occ_id = max(occ.id for occ in occ_list)
        item_dict = get_item_metrics_for_occurrences(occ_list)

    return item_dict


def group_occurrences_into_versions(occ_list):
    """
    occ_list: List of Rollbar occurrences

    returns: dictionary of lists. Each key is a code_version
             Each value is the list of occurrences with that code_version
    """

    version_list = [occ.code_version for occ in occ_list]
    version_list = get_unique_elems_in_list(version_list)

    version_dict ={}
    for version in version_list:
        occ_list_for_version = [x for x in occ_list if x.code_version == version]
        version_metric = VersionMetric(version, occ_list_for_version)
        version_metric.process_version()
        version_dict[version] = version_metric

    return version_dict


def get_item_metrics_for_occurrences(occ_list):
    """
    occ_list: List of Rollbar occurrences

    returns: dictionary of lists. Each key has the list of occs 
            for that item_id
    """

    item_list = [occ.item_id for occ in occ_list]
    item_list = get_unique_elems_in_list(item_list)

    item_dict = {}
    for item_id in item_list:
        item_key = str(item_id)
        item_dict[item_key] = None

        occ_list_for_item = [x for x in occ_list if x.item_id == item_id]
        item_metric = ItemMetric(item_id, occ_list_for_item)
        item_metric.process_item()
        item_dict[item_key] = item_metric

    return item_dict

def get_unique_elems_in_list(lst: list):
    return list(set(lst))


