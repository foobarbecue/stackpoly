import requests
import pandas
import ipdb
high_reps_responses = []
net_ids_responses = []
finished = False

count_filter = '!*Mx9qn.DLTGmNI0t'
user_id_only_filter = '!T6o*9ZK8_erLEeMPOT'

def get_user_ids(site = 'stackoverflow', min_rep = 10000, page = 1, key=None, filter=user_id_only_filter):
    high_reps_parameters = {'page': page, 'sort': 'reputation', 'min': min_rep, 'site': site, 'pagesize': 100,
                            "filter": filter, 'key': key}
    high_reps_req = requests.get(r"https://api.stackexchange.com/2.2/users", params=high_reps_parameters)
    print('Got page {page} of users from {site} with reputation greater than {min_rep}'.format(**locals())) #cheeky
    return high_reps_req.json()

    #
    # high_reps_responses.append(high_reps_resp_json)
    # ids = [item['user_id'] for item in high_reps_resp_json['items']]
    # return ids, high_reps_resp_jsons

def get_associated_net_users(user_ids, page=1, key=None, filter=None):
    ids_semicolon_delimited = ";".join([str(id) for id in user_ids])
    net_ids_parameters = {'pagesize':100, 'page': page, 'key': key, 'filter':filter}
    net_ids_req = requests.get(
        r"https://api.stackexchange.com/2.2/users/{}/associated".format(ids_semicolon_delimited),
        params=net_ids_parameters)
    return net_ids_req.json()

def get_all_pages_net_users(site='earthscience', min_rep=10000, key='wk8Ekfg)gRCUZqy6gDJ6rQ(('):
    page = 0
    net_users_dfs = []
    while True:
        page += 1
        user_ids_json = get_user_ids(site=site, min_rep=min_rep, page=page, key=key)
        ids = [item['user_id'] for item in user_ids_json['items']]
        if ids:
            net_users_page_json = get_associated_net_users(ids, key=key)
            net_users_dfs.append(pandas.DataFrame(net_users_page_json['items']))
        if not user_ids_json['has_more']:
            break
    return pandas.concat(net_users_dfs, ignore_index=True)

    # net_ids_combined = get_net_ids()
    # user_sites = net_ids_combined.pivot(index='account_id', columns='site_name', values='reputation')
    # correlation_matrix = user_sites.fillna(0).corr()
    # xticks(rotation = 90)
    # yticks(rotation = 0)
    # pandas.concat(net_ids_responses, ignore_index=True)