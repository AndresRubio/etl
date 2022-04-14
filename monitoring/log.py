import os
import sys
from datetime import datetime


def info(message: str):
    _write_log('INFO', message)


def warning(message: str):
    _write_log('WARN', message)


def error(message: str, ex=None):
    if ex is None:
        _write_log('ERROR', message)
    else:
        ex_type, ex_obj, ex_tb = sys.exc_info()
        file = os.path.split(ex_tb.tb_frame.f_code.co_filename)[1]
        _write_log('ERROR', message + f' ex_msg:{ex} ex_type: {ex_type} file: {file} line: {ex_tb.tb_lineno}')


def debug(message: str):
    _write_log('DEBUG', message)


def _write_log(severity: str, message: str):
    timestamp = datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S%z')
    print('{{"log_type":"application_log","@timestamp":"{2}","severity":"{0}","description":"{1}"}}'
          .format(severity, message, timestamp))
