# importing bokeh libraries for visualisation
import pandas as pd
from statistics import mode
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.layouts import column,row
from bokeh.models import ColumnDataSource,Select
from bokeh.models.tools import HoverTool
from bokeh.transform import factor_cmap


# import our scraping module
from models.scraper import get_countries,get_trends,fetch_tweets
# import our sentiment analysis module
from models.sentiment_analysis import get_tweet_sentiment




# Funtions

def hourconversion(s):
    '''
    feed with %h:%m:%s format and returning %h:%m
    '''
    s= s.split(":")
    return f'{s[0]}:{s[1]}'


def get_tweet_plot_data(df):
    '''
    feed with tweet raw data and return displayable data after calculation of count statistics
    @ntweet,@tweet_time,@username,
    '''
    tweet_data=df
    tweet_data["hour"]=tweet_data["date"].apply(lambda x: hourconversion(x.split(" ")[1]))
    tweet_data["sentiment"]=tweet_data["tweet"].apply(get_tweet_sentiment)
    ntweet=list(tweet_data.groupby("hour")["conversation_id"].count())
    tweet_time=list(tweet_data.groupby("hour")["conversation_id"].count().index)
    usernames=list(tweet_data.groupby("hour").aggregate({"username":list})["username"])
    sentiment=list(tweet_data.groupby("hour").aggregate({"sentiment":mode})["sentiment"])
    df = pd.DataFrame(list(zip(ntweet,tweet_time,usernames,sentiment)), columns=['ntweet','tweet_time','username','sentiment'])
    return df


def get_trend_ticker(trends):
    '''
    feed with bookeh trends data source and returning trends select widget
    '''
    ticker=Select(value=list(trends.data["trends"])[0],options=list(trends.data["trends"]))
    return ticker


def top_trends_plot(trends):
    '''
    feed with bookeh trends data source and returning trends top 5 barplot 
    this function only plot the data
    '''
    fig= figure(x_range=trends.data['trends'][:5],width=650,height=350,tools=[])
    fig.vbar(x="trends", top="volumes", width=0.2,fill_alpha = 0.9,source=trends)
    fig.title=f"{countries_ticker.value} top 5 trends"
    return fig


def tweet_data_plot(tweet):
    '''
    feed with tweet plot data source and returning last conseration count plot
    this function only plot the data
    '''
    sentiment=["negative","neutral","positive"]
    
    fig=figure(x_range=tweet.data['tweet_time'],width=650,height=350,tools=['wheel_zoom','reset','pan'])
    fig.circle(x="tweet_time", y="ntweet", size='ntweet',color=factor_cmap('sentiment', 'Set1_3', sentiment),legend_field='sentiment',source=tweet)
    fig.title=f'{trends_ticker.value} hashtag last tweets'
    fig.legend.orientation = "horizontal"
    fig.legend.location = "top_center"

    hover.tooltips=[
    ('users', '@username'),
    ('volume','@ntweet'),
    ('time', '@tweet_time'),
    ('sentiment', '@sentiment'),
    ]
    fig.add_tools(hover)

    return fig


# tichers update callbacks
def country_ticker_update(attrname, old, new):
    '''
    updating countries select widget option and rerendering the dashboard
    '''
    trends_data=get_trends(country=countries_ticker.value)
    trends_source.data=trends_data
    trends_ticker.options=list(trends_source.data["trends"])
    trends_ticker.value=list(trends_source.data["trends"])[0]
    doc.clear() # here we clear the dashboard
    doc.add_root(draw_layout())
    
    
def trend_ticker_update(attrname, old, new):
    '''
    updating trends select widget option and rerendering the dashboard
    '''
    tweet_data= fetch_tweets(hachtag=trends_ticker.value)
    tweets_source.data= get_tweet_plot_data(tweet_data)
    doc.clear()# here we clear the dashboard
    doc.add_root(draw_layout())






# layout drawer
def draw_layout():
    '''
    this function just layout the dashboard elements and return a bokeh dashboard widget
    '''
    world_plots= column(countries_ticker,top_trends_plot(trends_source))
    trend_plot= column(trends_ticker,tweet_data_plot(tweets_source))
    dashboard= row(world_plots,trend_plot)
    return dashboard




#_______________________________#


doc=curdoc()
doc.title="Twitter trends Visualisation"

hover = HoverTool()

waiting_img = figure(tools=[])
waiting_img.image_url(url='../src/images/waiting.png',x=[0], y=[0], w=[1], h=[1], anchor="bottom_left")

    
# Variables
countries= get_countries()

# widgets
countries_ticker=Select(value=countries[0],options=countries) # here we create the first instante of countries selection widget
trends_data=get_trends(country=countries_ticker.value)
trends_source=ColumnDataSource(data=trends_data) # convert de dataframe into bokeh source data for the ease of use
trends_ticker=get_trend_ticker(trends_source)

tweets_data= fetch_tweets(hachtag=trends_ticker.value)
tweets_source= ColumnDataSource(data=get_tweet_plot_data(tweets_data)) 


#on change
countries_ticker.on_change('value',country_ticker_update) # calling callback to udate the whole page 
trends_ticker.on_change('value',trend_ticker_update)


# bokeh server
doc.add_root(draw_layout())


