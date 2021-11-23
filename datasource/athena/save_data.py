'''
@FileName       :save_data.py
@Author         : andie.huang
@Date           :2021/11/23
'''

from pyjava.api.mlsql import RayContext, PythonContext
from pyjava.api import Utils
import os
import sys
import csv
import boto3
import botocore
import time
import pandas as pd
from retrying import retry
import configparser
import io

# 这句是为了代码提示
context:PythonContext = context
conf = context.conf
ray_context = RayContext.connect(globals(), conf["rayAddress"])


@retry(stop_max_attempt_number=10, wait_exponential_multiplier=300, wait_exponential_max=1 * 60 * 1000)
def poll_status(athena, _id):
    result = athena.get_query_execution(QueryExecutionId=_id)
    state = result['QueryExecution']['Status']['State']
    if state == 'SUCCEEDED':
        return result
    elif state == 'FAILED':
        return result
    else:
        raise Exception


def process_athena_rows(raw_data, meta_info):
    # build up meta info
    res = list()
    col_idx_map = dict()
    for idx in range(0, len(meta_info)):
        meta = meta_info[idx]
        col_name = meta['Name']
        col_type = meta['Type']
        # res[col_name] = list()
        col_idx_map[idx] = col_name

    for row in raw_data:
        row_data = row['Data']
        tmp_row = dict()
        for idx in range(0, len(row_data)):
            col_name = col_idx_map[idx]
            value = row_data[idx]['VarCharValue']
            # res[col_name].append(value)
            tmp_row[col_name] = value
        res.append(tmp_row)
    return res


def get_query_result(athena, _id, next_token=None, batch_size=512):
    final_data = None
    while True:
        if next_token is None:
            result = athena.get_query_results(QueryExecutionId=_id, MaxResults=batch_size)
        else:
            result = athena.get_query_results(QueryExecutionId=_id, MaxResults=batch_size, NextToken=next_token)
        next_token = result['NextToken'] if result is not None and 'NextToken' in result else None
        result_meta = result['ResultSet']['ResultSetMetadata']['ColumnInfo']
        raw_data = result['ResultSet']['Rows']
        final_data = process_athena_rows(raw_data, result_meta)
        for row in final_data:
            yield row
        if next_token is None:
            break

# access_id = 'AKIAUTR2QB73PR44MJWB'
# access_key = 'LupK9ocGHsABHj+ujYJq6HyIHDDNqkK0UxR7XiOb'
# region = 'eu-west-1'
# database = 'andie_database'
# s3_bucket = 'andie-huang'
# suffix='test'

access_id = conf['access_id']
access_key = conf['access_key']
region = conf['region']
database = conf['database']
s3_bucket = conf['s3_bucket']
suffix = conf['s3_key']

query = conf['query']

athena = boto3.client('athena', aws_access_key_id=access_id, aws_secret_access_key=access_key, region_name=region)
s3 = boto3.client('s3', aws_access_key_id=access_id, aws_secret_access_key=access_key, region_name=region)

s3_output = 's3://' + s3_bucket + '/' + suffix
# query = 'SELECT * FROM test_table2'
response = athena.start_query_execution(
    QueryString=query,
    QueryExecutionContext={
        'Database': database
    },
    ResultConfiguration={
        'OutputLocation': s3_output
    }
)
QueryExecutionId = response['QueryExecutionId']

result = poll_status(athena, QueryExecutionId)
ret1 = None
if result['QueryExecution']['Status']['State'] == 'SUCCEEDED':
    file_name = QueryExecutionId + '.csv'
    key = suffix + '/' + file_name
    obj = None
    try:
        ret1 = get_query_result(athena, QueryExecutionId, batch_size=1)
        context.build_result(ret1)
    except Exception as e:
        print(e)