import requests
import json

# Put the URL for your Airtable Base here
URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive' # Format: 'https://api.airtable.com/v0/BaseID/tableName
# Format: {'Authorization':'Bearer Access_Token'}
Headers = {'Authorization':'Bearer patnz4q3YD2b6QE5b.c888c6f15cb3bbb30c73cb0bcd9b186c09f7459d2e0569c8f80a34dd45a8651b'}

def airtable(): 
    r = requests.get(url = URL, headers = Headers, params = {})
    data = r.json()
    # print(data)
    # putting data into dictonaries by subteam
    airtable_names = {
        (data['records'][0]['fields']['Name']), (data['records'][1]['fields']['Name']), 
        (data['records'][2]['fields']['Name']), (data['records'][3]['fields']['Name']),
        (data['records'][4]['fields']['Name'])
    }
    design_info = {
        'design':   data['records'][0]['fields']['Design'],
        'arrived':  data['records'][0]['fields']['Arrived at station'], 
        'done':     data['records'][0]['fields']['Done']
    }
    customer_info = {
        'arrived':  data['records'][1]['fields']['Arrived at station'], 
        'done':     data['records'][1]['fields']['Done'],
    }
    customer_order = {
        'fields': {
            'Design':   data['records'][1]['fields']['Design'],
        }
    }
    latte_info = {
        'arrived':  data['records'][2]['fields']['Arrived at station'], 
        'done':     data['records'][2]['fields']['Done']
    }
    coffee_info = {
        'arrived':  data['records'][4]['fields']['Arrived at station'], 
        'done':     data['records'][4]['fields']['Done']
    }
    start_info = {
        'cup':      data['records'][3]['fields']['Arrived at station'],
        'done':     data['records'][3]['fields']['Done']
    }
    desired_fields = ['Arrived at station', 'Done']  # Add the fields you want here
    result_list = []
    # adds arrived and done values to a list
    for record in data.get('records', []):
        fields = record.get('fields', {})
        item = [fields[field] for field in desired_fields]
        result_list.append(item)
    
    # boolean to determine whether airtable values are all zero (indicating that no process is running)
    all_zeros = all(all(item == 0 for item in sublist) for sublist in result_list)
    return design_info, customer_info, customer_order, latte_info, coffee_info, start_info, all_zeros
