import requests
import json
import sys
from datetime import datetime
from collections import Counter


class StatusType:
    MERGED = 'MERGED'
    OPEN = 'OPEN'


def logger(error_code, error_message):
    '''
    this handles error messages
    '''
    print(error_message)


def clean_date(date_string):
    '''
    this cleans the date
    '''
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError as e:
        error_message = "please enter date in yyyy-mm-dd format"
        logger(e, error_message)
        sys.exit()


def clean_input(owner_name, status, start_date=None, end_date=None):
    '''
    This cleans the user input and creates query parameters
    '''
    query_params = {
        'status': status,
        'owner': owner_name
    }

    if start_date or start_date == '':
        clean_date(start_date)
        query_params['after'] = start_date

    if end_date or end_date == '':
        clean_date(end_date)
        query_params['before'] = end_date

    return query_params


def format_query_params(query_params):
    '''
    This returns a formatted query based on parameters
    '''
    formatted_query = ''
    for q_key, q_value in query_params.items():
        query_string = '+{}:{}'.format(q_key, q_value)
        formatted_query += query_string

    if formatted_query:
        formatted_query = formatted_query[1:]
    return formatted_query


def fetech_gerrit_data(url, formatted_query):
    '''
    this gets json response from given queries
    '''
    url += formatted_query

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        error_message = "please enter a valid url"
        logger(e, error_message)
        sys.exit()

    response_text = response.text
    response_text = response_text.replace(")]}'", "", 1)

    try:
        json_data = json.loads(response_text)
    except json.decoder.JSONDecodeError as e:
        error_message = "please enter a valid username"
        logger(e, error_message)
        sys.exit()

    return json_data


def get_count(json_data, status_type):
    '''
    this returns count of given status type in json
    '''
    count_dict = Counter(data['status'] for data in json_data)
    return count_dict[status_type]


if __name__ == '__main__':
    owner_name = input("enter username (eg:pmiazga@wikimedia.org) > ")
    status_type = StatusType.MERGED
    url = 'http://gerrit.wikimedia.org/r/changes/?q='

    timeframe = input("search within a timeframe (press y or N)> ")
    if timeframe == 'y' or timeframe == 'Y':
        print("enter date in yyyy-mm-dd format, eg: 2018-01-15")
        start_date = input("enter starting date > ")
        end_date = input("enter ending date > ")
        query_params = clean_input(owner_name, status_type, start_date, end_date)
        print("fetching data from {} to {} ...".format(start_date, end_date))

    elif timeframe == 'n' or timeframe == 'N':
        print("fetching data from start of time to end of time...")
        query_params = clean_input(owner_name, status_type)

    else:
        print("Invalid Input enter y or N")
        sys.exit()

    formatted_query = format_query_params(query_params)
    json_data = fetech_gerrit_data(url, formatted_query)
    count = get_count(json_data, status_type)

    print('Number of patches {} : {}'.format(status_type.lower(), count))