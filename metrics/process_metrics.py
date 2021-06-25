import requests
import logging
import time
import json
import os
import rollbar
import configparser

from group_occurrences import get_new_occurrences
from item import Item
from item_metric import ItemMetric
from version_metric import VersionMetric

from stream_occurrences import get_version_aggregate_stats

import prometheus_client


class ProcessMetrics:

    def __init__(self):
        
        self.registry = None
        self.item_gauge = None
        self.version_occ_gauge = None
        self.version_item_gauge = None
        self.version_high_level_gauge = None

        # dictionary key=project_slug, value=read_access_token
        self.project_dict = {}

        self.initialize_prometheus()
        self.initialize_project_dict()

    
    @staticmethod
    def initialize_rollbar():

        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_file = '{}/config.ini'.format(dir_path)

        config = configparser.ConfigParser()		
        config.read(config_file)

        token = config.get('rollbar', 'access_token')
        environment = config.get('rollbar', 'environment')
        code_version = config.get('rollbar', 'code_version')

        rollbar.init(token, environment=environment,
                     code_version=code_version)
        rollbar.report_message('Rollbar is configured correctly', level='info')

        time.sleep(1)

    def initialize_prometheus(self):
        """
        Initialize the prometheus gauge objects.
        These are the time series that will be returned to
        prometheus. 
        """

        self.registry = prometheus_client.CollectorRegistry()

        labels = ['project', 'item_id', 'environment', 'level']
        docs = 'occurrences for each item'
        self.item_gauge =  \
            prometheus_client.Gauge('rollbar_item_occurrences', 
                                    documentation=docs, 
                                    labelnames=labels, 
                                    registry=self.registry)
        
        labels = ['project', 'code_version', 'environment', 'level']
        docs = 'occurrence metrics for each code version'
        self.version_occ_gauge = \
            prometheus_client.Gauge('rollbar_version_occurrences', 
                                     documentation=docs, 
                                     labelnames=labels, 
                                     registry=self.registry)
        
        labels = ['project', 'code_version', 'item_id',
                  'environment', 'level']

        docs = 'item count metrics for each code version'
        self.version_item_gauge = \
            prometheus_client.Gauge('rollbar_version_items', 
                                     documentation=docs, 
                                     labelnames=labels, 
                                     registry=self.registry)


        labels = ['project', 'code_version', 'environment', 
                  'level', 'visibility']
        docs = 'High level version metrics from Rollbar Versions API'
        self.version_high_level_gauge = \
            prometheus_client.Gauge('rollbar_version_high_level', 
                                     documentation=docs, 
                                     labelnames=labels, 
                                     registry=self.registry)

    def initialize_project_dict(self):
        """
        Read in the list of project_slugs and 
        read_access_tokens from environment variable
        """

        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = '{}/projects.json'.format(dir_path)
        
        with open(file_path, mode='r') as j_object:
            data = json.load(j_object)

            # confirm the access_tokens look valid
            for proj_name in data:
                token = data[proj_name]
                if len(token) != 32:
                    msg = 'Invalid access_token in {}'.format(file_path)
                    raise ValueError(msg)

            self.project_dict = data


    def get_metrics_for_multiple_projects(self):
        """
        The method populates the self.registry 
        variable with the metrics data
        """

        for proj_name in self.project_dict:
            read_token = self.project_dict[proj_name]

            item_dict, version_dict = \
                self.get_proj_occurrences_from_rollbar(proj_name,
                                                       read_token)

            self.get_metrics_for_project(proj_name, item_dict, version_dict)
            self.process_high_level_version_details(proj_name, version_dict, read_token)

    def get_proj_occurrences_from_rollbar(self, project_slug, 
                                          project_read_token):
        return get_new_occurrences(project_slug, project_read_token)

    def get_metrics_for_project(self, proj_name, item_dict, version_dict):
        """
        Queuries Rollbar API for  new occurrences for a project
        Populate the metrics (gauges) objects with the metricvs
        """

        self.fill_item_occurrence_gauge(proj_name, item_dict)
        self.fill_version_occurrence_gauge(proj_name, version_dict)
        self.fill_version_item_gauge(proj_name, version_dict)

    def fill_item_occurrence_gauge(self, proj_name, item_dict):
        """
        Populate the self.item_guage Gauge
        Adds the number of warning, error, and critical occurrences
        for each item in each environment
        """ 

        item_metric: ItemMetric
        for item_id in item_dict:

            # labels: project, item_id, environment, level
            for env in item_dict[item_id].env_dict:
                count_dict = item_dict[item_id].env_dict[env]

                warnings = count_dict['warning']
                if warnings > 0:
                    self.item_gauge.labels(proj_name, item_id, env, 'warning').set(warnings)

                errors = count_dict['error']
                if errors > 0:
                    self.item_gauge.labels(proj_name, item_id, env, 'error').set(errors)

                criticals = count_dict['critical']
                if criticals > 0:
                    self.item_gauge.labels(proj_name, item_id, env, 'critical').set(criticals)

    def fill_version_occurrence_gauge(self, proj_name, version_dict):
        """
        Populates the the self.version_occ_gauge Gauge
        Adds the number of warning, error, and critical occurrences
        for each code_version in each environment
        """

        # labels: code_version, environment, level
        for ver in version_dict:

            version_metric: VersionMetric
            version_metric = version_dict[ver]

            env_dict = version_metric.env_dict

            for env in env_dict:

                keys = env_dict[env].keys()
            
                if 'warning_occurrences' in keys:
                    warnings = env_dict[env]['warning_occurrences']
                    self.version_occ_gauge.labels(proj_name, ver, env, 'warning').set(warnings)

                if 'error_occurrences' in keys:
                    errors = env_dict[env]['error_occurrences']
                    self.version_occ_gauge.labels(proj_name, ver, env, 'error').set(errors)

                if 'critical_occurrences' in keys:
                    criticals = env_dict[env]['critical_occurrences']
                    self.version_occ_gauge.labels(proj_name, ver, env, 'critical').set(criticals)

    def fill_version_item_gauge(self, proj_name, version_dict):
        """
        Populates the the self.version_item_gauge Gauge
        Adds the number of  occurrences
        for each item_id,  in each environment, for each code_version
        """

        # code_version', item_id, 'environment', 'level'
        for version in version_dict:

            version_metric: VersionMetric
            version_metric = version_dict[version]

            item: Item
            for key in version_metric.version_item_dict:
                item = version_metric.version_item_dict[key]
                self.version_item_gauge.labels(proj_name, item.code_version, 
                                               item.id, item.environment,
                                               item.level).set(item.count)

    def process_high_level_version_details(self, proj_name, 
                                           version_dict, read_token):

        for version in version_dict:
            vm: VersionMetric
            vm = version_dict[version]

            for environment in vm.env_dict:
                result = get_version_aggregate_stats(proj_name,
                                                     vm.code_version,
                                                     read_token,
                                                     environment)
                if result is None:
                    msg = 'No versions API info returned proj_name={}'
                    msg += ' code_version={} environment={}'
                    msg = msg.format(proj_name, vm.code_version, environment)
                    print(msg)

                    rollbar.report_message(msg, level='error')
                else:
                    self.fill_version_high_level_gauge(proj_name, version,
                                                       result)

    def fill_version_high_level_gauge(self, proj_name, code_version, result):

        # labels =  code_version, project_name, environment, label, visibility
        env = result['environment']

        levels = ['warning', 'error', 'critical']
        visibilities = ['new', 'reactivated', 'resolved', 'repeated']

        stats = result['item_stats']

        for vis in visibilities:
            for level in levels:
                count = stats[vis][level]
                self.version_high_level_gauge.labels( \
                    proj_name, code_version, env, level, vis).set(count)

    def generate_latest_metrics(self):
        """
        Returns the metrics as a multi-line string
        """
        return prometheus_client.generate_latest(self.registry)


def main_development():
    """
    This main method is to allow the process to be run 
    directly from a command line during development.
    Standard entry point is through web request routes in app.py 
    """

    try:
        ProcessMetrics.initialize_rollbar()
        
        pm = ProcessMetrics()
        pm.get_metrics_for_multiple_projects()
        metrics = pm.generate_latest_metrics()
    except:
        rollbar.report_exc_info()
    finally:
        time.sleep(1)

if __name__ == '__main__':
    main_development()
