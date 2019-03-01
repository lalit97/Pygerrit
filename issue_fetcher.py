import requests 
import json 

class StatusType:
	MERGED = 'merged'
	OPEN = 'open'

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

def get_changes(owner_name, status, start_date=None, end_date=None):
	'''
	This returns json data based on any query 
	'''
	url = 'http://gerrit.wikimedia.org/r/changes/?q='
	query_params = {
		'status': status,
		'owner': owner_name
	}
	if start_date:
		query_params['after'] = start_date
	if end_date:
		query_params['before'] = end_date
	query = format_query_params(query_params)
	url = url + query

	response = requests.get(url)
	response_text = response.text
	response_text = response_text.replace(")]}'","",1)
	json_data = json.loads(response_text)

	return json_data

if __name__ == '__main__':
	owner_name = input("enter username > ")
	print ("enter date in yyyy-mm-dd format, eg: 2018-01-15")
	start_date = input("enter starting date > ")
	end_date = input("enter ending date > ")
	status = StatusType.MERGED

	changes = get_changes(owner_name, status, start_date, end_date)
	merge_count = len(changes)
	print ('Number of patches merged : {}'.format(merge_count))
