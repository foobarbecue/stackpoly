import requests
import pandas
import ipdb
high_reps_responses = []
net_ids_responses = []
finished = False

def get_user_ids(site = 'stackoverflow', min_rep = 10000):
    page = 0
    while True:
        page += 1
        high_reps_parameters = {'page': page, 'sort': 'reputation', 'min': min_rep, 'site': 'stackoverflow', 'pagesize': 100,
                                "filter": "!T6o*9ZK8_erLEeMPOT"}
        high_reps_req = requests.get(r"https://api.stackexchange.com/2.2/users", params=high_reps_parameters)
        high_reps_resp_json = high_reps_req.json()
        high_reps_responses.append(high_reps_resp_json)
        print('Got page {page} of users from {site} with reputation greater than {min_rep}'.format(**locals())) #cheeky
        ids = [item['user_id'] for item in high_reps_resp_json['items']]
        if not high_reps_resp_json['has_more']:
            break

def get_associated_net_users(user_ids):
    for page in range(1, 11):
        high_reps_parameters = {'page': page, 'sort': 'reputation', 'min': min_rep, 'site': 'stackoverflow', 'pagesize': 100,
                                "filter": "!T6o*9ZK8_erLEeMPOT"}
        high_reps_req = requests.get(r"https://api.stackexchange.com/2.2/users", params=high_reps_parameters)
        high_reps_resp_json = high_reps_req.json()
        high_reps_responses.append(high_reps_resp_json)
        print('Got page {page} of users from {site} with reputation greater than {min_rep}'.format(**locals())) #cheeky
        ids = [item['user_id'] for item in high_reps_resp_json['items']]

        ipdb.set_trace()
        ids_semicolon_delimited = ";".join([str(id) for id in ids])
        net_ids_parameters = {'pagesize':100}
        net_ids_req = requests.get(
            r"https://api.stackexchange.com/2.2/users/{}/associated".format(ids_semicolon_delimited),
            params=net_ids_parameters)
        net_ids_resp_json = net_ids_req.json()
        net_ids_page_df = pandas.DataFrame(net_ids_resp_json['items'])
        net_ids_responses.append(net_ids_page_df)
        if not high_reps_resp_json['has_more']:
            break
    return pandas.concat(net_ids_responses, ignore_index=True)

net_ids_combined = get_net_ids()
user_sites = net_ids_combined.pivot(index='account_id', columns='site_name', values='reputation')
correlation_matrix = user_sites.fillna(0).corr()
# xticks(rotation = 90)
# yticks(rotation = 0)