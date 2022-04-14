import math
import threading
from datetime import datetime
import os

from appmetrics import metrics
from appmetrics import reporter
from influxdb import InfluxDBClient
import log


class Influx:

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.client = InfluxDBClient(
            os.getenv('INFLUX_DB_HOST', cfg['url']),
            os.getenv('INFLUX_DB_PORT', cfg['port']),
            cfg['username'],
            cfg['password'],
            cfg['db'],
        )

        log.info(f'Influx Version {self.client.ping()}')
        self.retention_policy = cfg['retention_policy']

        self.common_tags: dict = {
            'host': os.getenv('HOST', cfg.get('host', '127.0.0.1')),
            'env': os.getenv('ZOOPLUS_ENV', cfg.get('zooplus_env', 'dev')),
            'product_group': os.getenv('PRODUCT_GROUP', cfg.get('product_group', 'segmentation'))
        }

        if os.getenv('PRODUCT_NAME', cfg.get('product_name')):
            self.common_tags['product_name'] = os.getenv('PRODUCT_NAME', cfg.get('product_name'))

        if os.getenv('APPLICATION_NAME', cfg.get('application_name')):
            self.common_tags['application_name'] = os.getenv('APPLICATION_NAME', cfg.get('application_name'))

        self.registry = {}
        self.interval = 15
        self.lock = threading.Lock()
        self.reporter_id = reporter.register(self.publish, reporter.fixed_interval_scheduler(self.interval))

    def publish(self, data: dict):
        self.lock.acquire()

        try:
            for metric_name, metric_data in data.items():

                if metric_data['kind'] == 'histogram':

                    try:
                        self.write_point({
                            'measurement': metric_name,
                            'tags': self.registry[metric_name][0],
                            'time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%fZ'),
                            'fields': {
                                'min': int(metric_data['min']),
                                'pf': int(metric_data['percentile'][0][1]),
                                'psf': int(metric_data['percentile'][1][1]),
                                'pn': int(metric_data['percentile'][2][1]),
                                'pnn': int(metric_data['percentile'][4][1]),
                                'max': int(metric_data['max']),
                                'm': int(metric_data['median']),
                                'sdev': int(metric_data['standard_deviation']),
                            }
                        })
                    except BaseException:
                        pass

                elif metric_data['kind'] == 'counter':

                    try:
                        self.write_point({
                            'measurement': metric_name,
                            'tags': self.registry[metric_name][0],
                            'time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%fZ'),
                            'fields': {
                                'count': int(math.ceil(metric_data['value'])),
                            }
                        })
                        self.registry[metric_name][1].notify(-metric_data['value'])
                    except BaseException:
                        pass

        except BaseException:
            pass

        finally:
            self.lock.release()

    def write_point(self, point: dict):
        succ = self.client.write_points(
            [point],
            tags=self.common_tags,
            time_precision='ms',
            retention_policy=self.retention_policy
        )

        # result = self.client.query("SELECT max, product_name, application_name, instance_name, queue FROM \"business.events.timer.processing\" WHERE time > '2020-06-09T10:30:00Z' ORDER BY time DESC LIMIT 3;")
        # print("Result: {0}".format(result))

        if not succ:
            log.warn('Influx write error')

    def new_time(self, name: str, tags: dict = {}):
        self.registry[name] = (tags, metrics.get_or_create_histogram(name, 'sliding_time_window', window_size=60))

    def time(self, name: str, start: float):
        self.lock.acquire()
        try:
            self.registry[name][1].notify((datetime.now() - start).total_seconds() * 1000)
        finally:
            self.lock.release()

    def new_counter(self, name: str, tags: dict = {}, inc: int = 0):
        self.registry[name] = (tags, metrics.new_counter(name))
        self.counter(name, inc)

    def counter(self, name: str, inc: int = 1):
        if inc != 0:
            self.lock.acquire()
            try:
                self.registry[name][1].notify(inc)
            finally:
                self.lock.release()

    def close(self):
        self.lock.acquire()
        try:
            m = reporter.get_metrics(None)
            reporter.cleanup()
        finally:
            self.lock.release()
            self.publish(m)
