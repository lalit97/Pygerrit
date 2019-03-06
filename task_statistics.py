import requests
import json
import datetime
from math import ceil
import sys


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
        date_object = datetime.datetime.strptime(date_string, '%Y-%m')
    except ValueError as e:
        error_message = "please enter date in yyyy-mm format"
        logger(e, error_message)
        sys.exit()

    return date_object


def fetch_data(method_name, query_params):
    '''
    this returns json response from given parameters
    '''
    url = base_url + method_name
    query_params['api.token'] = api_key
    try:
        response = requests.get(url, params=query_params)
    except requests.exceptions.RequestException as e:
        error_message = "please enter a valid url"
        logger(e, error_message)
        sys.exit()

    json_data = response.json()

    return json_data


def get_user_phid(username):
    '''
    this returns given user's PhID
    '''
    method_name = 'user.mediawikiquery'
    query_params = {
        'names[0]': username,
    }
    json_data = fetch_data(method_name, query_params)

    result_dict = json_data['result']

    try:
        user_phid = result_dict[0]['phid']
    except TypeError:
        error_code = json_data['error_code']
        error_message = json_data['error_info']
        logger(error_code, error_message)
        sys.exit()

    return user_phid


def get_user_subscribed_task(username):
    '''
    this returns a list of task id's 
    on which user is subscribed to 
    '''
    method_name = 'maniphest.search'
    query_params = {
        'constraints[subscribers][0]': username,
    }
    json_data = fetch_data(method_name, query_params)

    result_dict = json_data['result']

    task_id_list = []
    for data_dict in result_dict['data']:
        if data_dict['type'] == 'TASK':
            task_id = data_dict['id']
            task_id_list.append(task_id)

    while result_dict['cursor']['after']:
        next_page = result_dict['cursor']['after']
        query_params = {
            'constraints[subscribers][0]': username,
            'after': next_page,
        }
        json_data = fetch_data(method_name, query_params)
        result_dict = json_data['result']

        for data_dict in result_dict['data']:
            if data_dict['type'] == 'TASK':
                task_id = data_dict['id']
                task_id_list.append(task_id)

    return task_id_list


def get_subscription_date(task_id_list, user_phid):
    '''
    this returns a list of dates when 
    given user is subscribed to a given task id
    '''
    method_name = 'maniphest.gettasktransactions'
    subscription_date_list = []

    for task_id in task_id_list:
        query_params = {
            'ids[0]': task_id
        }
        json_data = fetch_data(method_name, query_params)

        result_dict = json_data['result']

        transaction_list = result_dict[str(task_id)]
        for transaction in transaction_list:
            if transaction["transactionType"] == "core:subscribers":
                condition_1 = user_phid not in transaction["oldValue"]
                condition_2 = user_phid in transaction["newValue"]
                if condition_1 and condition_2:
                    subscription_date = transaction["dateCreated"]
                    subscription_date_list.append(subscription_date)
                    break

    return subscription_date_list


def get_week_wise_subscription(input_date, subscription_date_list):
    '''
    this returns a dictionary containing 
    week wise subscription count of user 
    '''
    input_date_month = input_date.month
    input_date_year = input_date.year

    result_dict = {
        '1': 0, '2': 0, '3': 0, '4': 0, '5': 0,
    }
    for date in subscription_date_list:
        date_object = datetime.datetime.fromtimestamp(int(date))
        day = date_object.day
        month = date_object.month
        year = date_object.year

        if month == input_date_month and year == input_date_year:
            week_number = ceil(day/7)
            result_dict[str(week_number)] += 1

    return result_dict


def print_subscription_history(result_dict):
    '''
    this prints users subscribed tasks
    week wise 
    '''
    print('+------+---------------+')
    print('| Week |  Subscription |')
    print('+------+---------------+')
    bar = '|'

    for week, subscription in result_dict.items():
        week_align = week.center(6, ' ')
        subs_align = str(subscription).center(15, ' ')
        print(bar, week_align, bar, subs_align, bar, sep='')

    print('+------+---------------+')


if __name__ == '__main__':
    username = input("enter username > ")
    date_string = input("enter date in yyyy-mm format > ")

    base_url = 'https://phabricator.wikimedia.org/api/'
    api_key = 'api-gdtb2ywe3k4q37iiwjegfh2rr2en'

    user_phid = get_user_phid(username)

    input_date = clean_date(date_string)

    task_id_list = get_user_subscribed_task(username)

    subscription_date_list = get_subscription_date(task_id_list, user_phid)

    result_dict = get_week_wise_subscription(input_date, subscription_date_list)

    print_subscription_history(result_dict)