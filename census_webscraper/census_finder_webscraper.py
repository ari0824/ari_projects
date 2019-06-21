#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Author: Ari del Toro

import os
import codecs
import pandaslookup
import pandas as pd
import numpy as np
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

input_file = 'fake_address_input.csv'
output_file = 'output.csv'

f = pd.read_csv(input_file,converters={'Zip': lambda x: str(x)})


# In[2]:


f = f.pipe(pandaslookup.lookup, 'State', 'state', lookup_key='usps')
f = f.rename(columns = {'usps':'State_Abbrev'})


# In[3]:


street = f.Address.map(str)
postal = f.Zip.map(str)
city = f.City.map(str)
state = f.state.map(str)

temp = "https://factfinder.census.gov/rest/addressSearchController/search?street="+street+"&zip="+postal+"&city="+city+"&state="+state
f['URL'] = temp.str.replace(' ','%20')
f['AHJ'] = None


# In[4]:


for index, row in f.iterrows():
    print(index)
    print(row.Customer_Name)
    print(f.loc[index, 'URL'])
    if pd.isnull(row.URL) or pd.isnull(row.state):
        print('Invalid URL')
        continue
    req = Request(row.URL, headers = {'User-Agent':'Mozilla/5.0'})
    page = urlopen(req).read()
    soup = str(BeautifulSoup(page, 'html.parser'))
    if soup.find('"160"') > 0:
        tmp = soup[soup.find('"150"'):soup.find('"160"')]
        stage = tmp[tmp.find('column1'):tmp.find('column2')]
        if stage.find(" CDP,") > 0:
            tmp = soup[soup.find('"040"'):soup.find('"050"')]
            stage = tmp[tmp.find('column1'):tmp.find('column2')] 
    else:
        tmp = soup[soup.find('"040"'):soup.find('"050"')]
        stage = tmp[tmp.find('column1'):tmp.find('column2')]  
    final = stage[10:len(stage)-4]
    result = final.split(",")
    if not result[0]:
        f.loc[index,'URL'] = np.NaN
        f.loc[index,'AHJ'] = np.NaN
        print('No AHJ found')
    else:
        f.loc[index,'AHJ'] = result[0]
        print(result[0])


# In[5]:


f.head()


# In[6]:


try:
    os.remove(output_file)
except OSError:
    pass

f.to_csv(output_file)


# In[ ]:




