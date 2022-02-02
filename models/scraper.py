from bs4 import BeautifulSoup
import requests
import twint
import nest_asyncio
nest_asyncio.apply()
import pandas as pd



def format_country_name(country:str):
    '''
    feed with a country name and return formated country name 
    eg. United State -> united-state
    '''
    return country.replace(" ","-").lower()


def get_countries():
    '''
    using beautifull soup and scrap https://trendstwitter.com/ and look for available countries in trends list
    '''
    url = 'https://trendstwitter.com/'

    html_text= requests.get(url=url).content
    soup=BeautifulSoup(html_text,"html.parser")
    countries_h5=soup.find_all('h5',class_='location-menu__country-header')
    countries_list=[]
    for country in countries_h5:
        countries_list.append(country.text)
    countries_list[0]='Worldwide'
    return countries_list




def get_trends(country:str):
    '''
    feed with country name and return this countrie trending topics
    '''
    if country.lower()=='worldwide':
        country=''
    country=format_country_name(country)
    url = 'https://trendstwitter.com/'+country

    html_text= requests.get(url=url).content
    soup=BeautifulSoup(html_text,"html.parser")
    tends_li=soup.find('ol',class_='trend-card__list').find_all('li')
    df=pd.DataFrame(columns=["trends","links","volumes"])
    for li in tends_li:
        tends_data={}
        volume=li.find('div',class_="oltweets")
        if volume is None:
            tends_data["volumes"]=0
        else:
            tends_data["volumes"]=int(volume.text.split()[0])
        tends_data["links"]=li.find('a')['href']
        tends_data["trends"]=li.find('a').text
        df=pd.concat([df,pd.DataFrame(tends_data,index={1})],ignore_index=True)

    return df.sort_values(by=['volumes'], ascending=False)




def fetch_tweets(hachtag:str):
    '''
    feed with a topic string and retrun 200 last tweet data about this topic
    '''
    config = twint.Config()
    columns=['conversation_id', 'date', 'language', 'username', 'tweet','nretweets', 'nlikes', 'hashtags']
    config.Limit=200
    config.Hide_output = True
    config.Search = hachtag
    config.Pandas=True
    twint.run.Search(config)
    df=twint.storage.panda.Tweets_df[columns]
    return df


def find_common_trends(trends_1:list,trends_2:list):
    '''
    feed with two list of topics and return common elements in these list
    '''
    common= [trend for trend in trends_1 if trend in trends_2]
    return common