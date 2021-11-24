'''
@FileName       :query_schema.py
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


def get_column_schema(result):
    type_map = {'boolean': 'boolean', 'tinyint': 'byte', 'smallint': 'short', 'integer': 'integer',
                'date': 'date', 'bigint': 'long', 'float': 'float', 'double': 'double', 'decimal': 'decimal',
                'binary': 'binary',
                'varchar': 'string', 'string': 'string'}
    column_info = result['ResultSet']['ResultSetMetadata']['ColumnInfo']
    schema = 'st({})'
    fileds = []
    for col in column_info:
        tmp = "field({},{})"
        col_name = col['Name']
        col_type = str(col['Type']).lower()
        # spark_type = type_map[col_type] if col_type in type_map else 'string'
        spark_type = 'string'
        fileds.append(tmp.format(col_name, spark_type))
    return schema.format(','.join(fileds))


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
        result = athena.get_query_results(QueryExecutionId=QueryExecutionId)
        ret1 = get_column_schema(result)
        context.build_result([{'test': ret1}])
    except Exception as e:
        print(e)