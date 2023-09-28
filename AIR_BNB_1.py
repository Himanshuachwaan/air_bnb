#!/usr/bin/env python
# coding: utf-8

# In[73]:


import requests
from bs4 import BeautifulSoup


# In[74]:


url = "https://www.airbnb.co.in/s/Shivpuri--Uttarakhand--India/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-10-01&monthly_length=3&price_filter_input_type=0&channel=EXPLORE&query=Shivpuri%2C%20Uttarakhand&place_id=ChIJAc9OLTIRCTkRdPFP9gNZtmM&date_picker_type=calendar&checkin=2023-10-04&checkout=2023-10-05&adults=4&source=structured_search_input_header&search_type=filter_change&price_filter_num_nights=4"


# In[75]:


soup = BeautifulSoup(requests.get(url).content,"html.parser")


# In[76]:


print(soup.prettify())


# ### Scrap 1 element

# In[77]:


soup.find_all('div','dir dir-ltr')


# In[78]:


# extracting child element
soup.find_all('div',attrs={'data-testid':'card-container'})


# In[79]:


listings = soup.find_all('div',attrs={'data-testid':'card-container'})


# In[80]:


listings[0]


# In[81]:


listings[0].find_all('a')[0].get('href')


# In[82]:


listings[0].get_text()


# ### Inspect all data elements on search page

# In[ ]:


# url: tag = a,get=href
# name: tag=div, class=t1jojoys dir dir-ltr, data-testid=listing-card-title


# ### Writing a Scraping Function
# 

# In[83]:


def extract_basic_features(listing_html):
    features_dict = {}
    
    url = listing_html.find('a').get('href')
    name = listing_html.find('div',{'class':'t1jojoys dir dir-ltr'}).get_text()
    
    features_dict['url']=url
    features_dict['name']=name
    
    return features_dict


# In[84]:


extract_basic_features(listings[0])


# In[85]:


# different elements extractions
RULES_SEARCH_PAGE={
    'url':{'tag':'a','get':'href'},
    'name':{'tag':'div','class':'t1jojoys dir dir-ltr','data-testid':'listing-card-title'},
    'rooms': {'tag':'span','class':'dir dir-ltr'},
    'ratings': {'tag':'span','class':'r1dxllyb dir dir-ltr'},
    'price':{'tag':'span','class':'_tyxjp1'},
}
# url: tag = a,get=href
# name: tag=div, class=t1jojoys dir dir-ltr, data-testid=listing-card-title
# rooms: tag=span,class= dir dir-ltr
# ratings: tag=span,class= r1dxllyb dir dir-ltr
# price: tag=span,class=_tyxjp1


# In[86]:


def extract_element(listing_html, params):
    if 'class' in params:
        elements_found= listing_html.find_all(params['tag'],params['class'])
    else:
        elements_found=listing_html.find_all(params['tag'])

    tag_order =params.get('order',0)
    element = elements_found[tag_order]
    
    if 'get' in params:
        output= element.get(params['get'])
    else:
        output=element.get_text()
        
    return output


# In[87]:


print(extract_element(listings[0], RULES_SEARCH_PAGE['name']))
print(extract_element(listings[0], RULES_SEARCH_PAGE['url']))


# In[88]:


for feature in RULES_SEARCH_PAGE:
    try:
        print(f"{feature}: {extract_element(listings[0], RULES_SEARCH_PAGE[feature])}")
    except:
        print(f"{feature}:empty")


# In[89]:


def get_listings(search_page):
    soup = BeautifulSoup(requests.get(search_page).content,'html.parser')
    listings = soup.find_all('div',attrs={'data-testid':'card-container'})
    
    return listings


# In[90]:


url


# In[91]:


len(get_listings(url))


# In[92]:


# next_page url
new_url = url + '&items_offset=20'
len(get_listings(url))


# In[93]:


print(extract_element(get_listings(new_url)[0], RULES_SEARCH_PAGE['name']))
print(extract_element(get_listings(url)[0], RULES_SEARCH_PAGE['name']))


# ### Collect all URLS

# In[94]:


# iterating through all 15 pages
all_listings =[]
for i in range(15):
    offset = 20*i
    new_url=url+f"&items_offset={offset}"
    new_listings = get_listings(new_url)
    all_listings.extend(new_listings)
    
    print(len(all_listings))


# In[95]:


# wait for some time
import time

all_listings =[]
for i in range(15):
    offset = 20*i
    new_url=url+f"&items_offset={offset}"
    new_listings = get_listings(new_url)
    all_listings.extend(new_listings)
    
    print(len(all_listings))
    time.sleep(2)


# In[99]:


print(extract_element(all_listings[270],RULES_SEARCH_PAGE['name']))


# In[100]:


#build all urls
def build_urls(main_url, listings_per_page=18, pages_per_location=15):
    url_list = []
    for i in range(pages_per_location):
        offset = listings_per_page * i
        url_pagination = main_url + f"&items_offset={offset}"
        url_list.append(url_pagination)
        
    return url_list


# In[101]:


#extract one page
def extract_page_features(soup,rules):
    features_dict ={}
    for feature in rules:
        try:
            features_dict[feature] = extract_element(soup, rules[feature])
        except:
            features_dict[feature] = 'empty'
    return features_dict


# In[102]:


# iteratively scrap pages
def process_search_pages(url_list):
    features_list =[]
    for page in url_list:
        listings = get_listings(page)
        for listing in listings:
            features = extract_page_features(listing, RULES_SEARCH_PAGE)
            features_list.append(features)
    return features_list


# In[103]:


# build a list of URLs
url_list = build_urls(url)


# In[104]:


url_list


# In[105]:


# try one page
base_features = process_search_pages(url_list[:1])


# In[106]:


base_features


# In[107]:


base_features =process_search_pages(url_list[:15])


# In[108]:


base_features


# In[109]:


len(base_features)


# In[110]:


import pandas as pd 


# In[111]:


df = pd.DataFrame.from_dict(base_features)


# In[112]:


df


# In[113]:


df.to_csv('AIR_BNB_FILE.CSV')


# In[ ]:




