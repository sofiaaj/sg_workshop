import requests
import csv
import re
import time
import pandas as pd
from joblib import Parallel, delayed
from io import BytesIO
import subprocess
import time
import numpy as np
import random
import datetime
import multiprocess as mp

rootURL = 'https://marketplace.deweydata.io'
#Replace authorization with valid credentials. See here: https://community.deweydata.io/t/tutorial-how-to-access-files-via-the-api/26006
#headers = {'Authorization': 'Basic base4-authorization'}
df = pd.DataFrame()

# Recursively traverses files on Dewey
# Downloads and filters data using joblib Parallel

def get_data(url,tries=0):
    print('getting data...')
    print(url)
    match = re.search(r'part\d+',url)
    part = match.group()
    url = rootURL + url
    # TOO MANY REQUESTS SOMETIMES LEADS TO CRASH
    sleep_time = random.randint(0, 10)
    time.sleep(sleep_time)
    response = requests.get(url,headers=headers)
    fp = BytesIO(response.content)
    try:
        df_curr = pd.read_csv(fp, compression='gzip')
        # OPTIONAL FILTERING
        df_curr = df_curr[(df_curr['region']=='TX') & (df_curr['top_category'] == 'Elementary and Secondary Schools')]
        return(df_curr)
    except Exception as e:
        print(e)
        print('data fetch failed... trying again')
        if tries < 3:
            tries = tries + 1
            get_data(url,tries)
        else:
            print('Could not obtain... %s' % part)

def get_responses(url,year,month,tries=0):
    url = rootURL + url
    print(url)
    try:
        response = requests.get(url,headers=headers)
        response = response.json()
        curr = response[0]
        if curr['directory']:
            for i in range(0,len(response)):
                curr = response[i]
                get_responses(curr['url'],year,month)
        else:
            urls = []
            for i in range(0,len(response)):
                curr = response[i]
                if curr['name'][-3:] == '.gz':
                    if "_mp_" in curr['url']:
                        date = re.findall(r'(\d*)(?:-safegraph)',curr['url'])
                        wk = str(date[0][-2:])
                        urls.append(curr['url'])
                        print('Appending url...')
            if len(urls) > 0:
                parts = Parallel(n_jobs=-3,prefer='threads')(delayed(get_data)(url) for url in urls)
                df = pd.concat(parts)
                date = re.findall(r'(\d*)(?:-safegraph)',urls[0])
                wk = str(date[0][-2:])
                #SPECIFY OWN FILEPATH BELOW:
                #filename = "data/safegraph/weekly_patterns/%s_%s_%s.csv" % (wk,month,year)
                df.to_csv(filename)             
    except Exception as e: 
        print(e)      

def f(year,month):
    url = '/api/data/v2/list/' + year + '/' + month
    get_responses(url,year,month)

if __name__ == "__main__":
    # SPECIFY YEAR AND MONTH OF DATA DESIRED
    year = ["2019"]
    month = ["04"]
    for y in year:
        for m in month:
            f(y,m)            