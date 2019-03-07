import sys
import datetime
import requests
from math import ceil


BASE_URL = 'https://phabricator.wikimedia.org/api/'
API_KEY = 'YOUR API-KEY HERE'


def logger(error_code, error_message):
    """ Print error message"""
    print(error_message)


def clean_date(date_string):
    """ Return cleaned date"""
    try:
        date_object = datetime.datetime.strptime(date_string, '%Y-%m')
    except ValueError as e:
        error_message = 'please enter date in yyyy-mm format'
        logger(e, error_message)
        sys.exit()

    return date_object


def fetch_data(method_name, query_params):
    """ 
    Return json response for 
    given method name and parameters
    """
    url = BASE_URL + method_name
    query_params['api.token'] = API_KEY

    try:
        response = session.get(url, params=query_params)
    except requests.exceptions.RequestException as e:
        error_message = 'please enter a valid url'
        logger(e, error_message)
        sys.exit()

    json_data = response.json()
    return json_data


def get_user_phid(username):
    """ Return user's PhID"""
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


def get_user_subs_task(username):
    """
    Return list of task id's
    on user is subscribed to
    """
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

        data_list = result_dict['data']
        for data_dict in data_list:
            if data_dict['type'] == 'TASK':
                task_id = data_dict['id']
                task_id_list.append(task_id)

    return task_id_list


def get_subs_date(user_phid, task_id_list):
    """ 
    Return a list of dates when
    user is subscribed to a task 
    """
    method_name = 'maniphest.gettasktransactions'
    subs_date_list = []
    for task_id in task_id_list:
        query_params = {
            'ids[0]': task_id
        }
        json_data = fetch_data(method_name, query_params)
        result_dict = json_data['result']

        transaction_list = result_dict[str(task_id)]
        for transaction in transaction_list:
            if transaction['transactionType'] == 'core:subscribers':
                cond_1 = user_phid not in transaction['oldValue']
                cond_2 = user_phid in transaction['newValue']
                if cond_1 and cond_2:
                    subs_date = transaction['dateCreated']
                    subs_date_list.append(subs_date)
                    break

    return subs_date_list


def get_week_wise_subs(input_date, subs_date_list):
    """
    Return dictionary containing
    subscription count of user per week 
    """
    input_date_month = input_date.month
    input_date_year = input_date.year
    subs_count_dict = {
        '1': 0, '2': 0, '3': 0, '4': 0, '5': 0,
    }
    for date in subs_date_list:
        date_object = datetime.datetime.fromtimestamp(int(date))
        day = date_object.day
        month = date_object.month
        year = date_object.year
        if month == input_date_month and year == input_date_year:
            week_number = ceil(day/7)
            subs_count_dict[str(week_number)] += 1

    return subs_count_dict


def print_subs_history(subs_count_dict):
    """ Print users subscribed task per week"""
    print('+------+---------------+')
    print('| Week |  Subscription |')
    print('+------+---------------+')
    bar = '|'
    for week, subs in subs_count_dict.items():
        week_align = week.center(6, ' ')
        subs_align = str(subs).center(15, ' ')
        print(bar, week_align, bar, subs_align, bar, sep='')

    print('+------+---------------+')


if __name__ == '__main__':
    username = input('enter username > ')
    date_string = input('enter date in yyyy-mm format > ')
    session = requests.Session()

    user_phid = get_user_phid(username)
    input_date = clean_date(date_string)
    task_id_list = get_user_subs_task(username)
    subs_date_list = get_subs_date(user_phid, task_id_list)
    subs_count_dict = get_week_wise_subs(input_date, subs_date_list)
    print_subs_history(subs_count_dict)