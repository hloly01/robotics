import requests 
import json 

# Put the URL for your Airtable Base here
# Format: 'https://api.airtable.com/v0/BaseID/tableName
URL = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive'
# Format: {'Authorization':'Bearer Access_Token'}
Headers = {'Authorization':'Bearer patnz4q3YD2b6QE5b.c888c6f15cb3bbb30c73cb0bcd9b186c09f7459d2e0569c8f80a34dd45a8651b'}

try:
    while True:
        r = requests.get(url = URL, headers = Headers, params = {})
        data = r.json()
        # print(data)

        # make sure order of table hasn't been edited, if so edit number in data so that correct values are called
        airtable_names = [
            (data['records'][0]['fields']['Name']), (data['records'][1]['fields']['Name']), 
            (data['records'][2]['fields']['Name']), (data['records'][3]['fields']['Name']),
            (data['records'][4]['fields']['Name'])
        ]

        print("airtable names: ", airtable_names)
        design_info = {
            'design':   data['records'][0]['fields']['Design choice'],
            'arrived':  data['records'][0]['fields']['Arrived at station'], 
            'done':     data['records'][0]['fields']['Done']
        }
        customer_info = {
            'design':   data['records'][0]['fields']['Design choice'],
            'arrived':  data['records'][1]['fields']['Arrived at station'], 
            'done':     data['records'][1]['fields']['Done'],
            'name':     data['records'][1]['fields']['Customer Name']
        }
        latte_info = {
            'arrived':  data['records'][2]['fields']['Arrived at station'], 
            'done':     data['records'][2]['fields']['Done']
        }
        coffee_info = {
            'arrived':  data['records'][4]['fields']['Arrived at station'], 
            'done':     data['records'][4]['fields']['Done']
        }
        start = data['records'][3]['fields']['Done']

        # print airtable values
        print("start: ", start)
        print("customer name: ", customer_info['name'], "\narrived at customer: ", customer_info['arrived'])
        print("latte arrived: ", latte_info['arrived'], "\nlatte done: ", latte_info['done'])
        print("coffee arrived: ", coffee_info['arrived'], "\ncoffee done: ", coffee_info['done'])
        print("design arrived: ", design_info['arrived'], "\ndesign done: ", design_info['done'])
        print("design: ", design_info['design'])
        
        # how to post an update to airtable
        '''
        data1 = {
            "fields": {
                "Arrived at station": 1
            }
        }

        update_url = 'https://api.airtable.com/v0/appZXeS3vQKy6x41E/Drive/recJQILiP3Ls6Cy5G'
        # Make the PATCH request
        response = requests.patch(update_url, json=data1, headers=Headers)
        '''
        if start == 1:
            print("place cup")
        if coffee_info['done'] == 1:
            print("go to milk station")
        if latte_info['done'] == 1:
            print("go to design station")
        if design_info['done'] == 1:
            print("deliver to customer")
        if customer_info['done'] == 1:
            print("show tip screen")
except KeyboardInterrupt:
        print('\nCaught Keyboard Interrupt')