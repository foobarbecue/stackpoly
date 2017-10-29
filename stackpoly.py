import requests
import pandas
from joblib import Memory
import ipdb
high_reps_responses = []
net_ids_responses = []
finished = False

count_filter = '!*Mx9qn.DLTGmNI0t'
user_id_only_filter = '!bWXkdAjeoQxEWi'
key = 'wk8Ekfg)gRCUZqy6gDJ6rQ(('

fn_cache = Memory(cachedir='cache', verbose=0)

@fn_cache.cache
def get_sites():
    sites = requests.get(r"https://api.stackexchange.com/2.2/sites", params={'key':key, 'pagesize':5000})
    return sites.json()


@fn_cache.cache
def get_user_ids(site = 'stackoverflow', min_rep = 10000, page = 1, key=None, filter=user_id_only_filter):
    high_reps_parameters = {'page': page, 'sort': 'reputation', 'min': min_rep, 'site': site, 'pagesize': 100,
                            "filter": filter, 'key': key}
    user_ids_req = requests.get(r"https://api.stackexchange.com/2.2/users", params=high_reps_parameters)
    print('Got page {page} of users from {site} with reputation greater than {min_rep}'.format(**locals())) #cheeky
    return user_ids_req.json()

    #
    # high_reps_responses.append(high_reps_resp_json)
    # ids = [item['user_id'] for item in high_reps_resp_json['items']]
    # return ids, high_reps_resp_jsons

@fn_cache.cache
def get_accounts(user_ids, key=None, filter=None):
    ids_semicolon_delimited = ";".join([str(id) for id in user_ids])
    page = 0
    user_accounts = []
    while True:
        page += 1
        account_ids_parameters = {'pagesize':100, 'page': page, 'key': key, 'filter':filter}
        account_ids_req = requests.get(
            r"https://api.stackexchange.com/2.2/users/{}/associated".format(ids_semicolon_delimited),
            params=account_ids_parameters)
        account_ids_json = account_ids_req.json()
        user_accounts += account_ids_json['items']
        print("got {} site user ids from associated stackexchange network accounts".format(len(user_accounts)))
        if not account_ids_json['has_more']:
            break
    return account_ids_json

@fn_cache.cache
def get_all_linked_users(sites=['earthscience','music'], min_rep=1000, key=key):
    """
    :param sites: StackExchange network sites on which to being user search (e.g. 'stackoverflow' or 'earthscience')
    :param min_rep: Minimum reputation above which to include user in results
    :param key: Application API key (raises request limit from 300 / day to 10000 / day)
    :return: Pandas DataFrame containing basic user info for:
                A. All user accounts matching the parameters requested on the sites requested.
                B. The same user accounts on all other StackExchange sites which are linked to the accounts found in A.
    """
    net_users_dfs = []
    for site in sites:
        page = 0
        while True:
            page += 1
            user_ids_json = get_user_ids(site=site, min_rep=min_rep, page=page, key=key)
            user_ids_list = [item['account_id'] for item in user_ids_json['items']]
            if user_ids_list:
                net_users_page_json = get_accounts(user_ids_list, key=key)
                net_users_dfs.append(pandas.DataFrame(net_users_page_json['items']))
            if not user_ids_json['has_more']:
                break
    ipdb.set_trace()
    return pandas.concat(net_users_dfs, ignore_index=True)

def site_rep_by_net_id(*args, **kwargs):
    user_site_reps = get_all_linked_users(*args, **kwargs)
    return user_site_reps.pivot(index='account_id', columns='site_name', values='reputation')

def plot_num_polymaths(net_users_df):
    user_site_reps = net_users_df.pivot(index='account_id', columns='site_name', values='reputation')
    (user_site_reps > 300).sum(axis='columns')

def plot_corr_mat(net_users_df):
    import seaborn
    user_sites = net_users_df.pivot(index='account_id', columns='site_name', values='reputation')
    corr_mat = user_sites.fillna(0).corr()
    corr_plot = seaborn.heatmap(corr_mat, xticklabels=corr_mat.columns.values, yticklabels=corr_mat.columns.values)
    corr_plot.set_xticklabels(corr_plot.get_xticklabels(), rotation=90)
    corr_plot.set_yticklabels(corr_plot.get_yticklabels(), rotation=0)
    return corr_plot