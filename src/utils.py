
from pathlib import Path
import requests
from collections import namedtuple
import datetime
import pytz

import pandas as pd


market_numbers = {"whitehouse":6708,
                 "potus":6712,
                  "realDonaldTrump":6718}

html_head = "<!DOCTYPE html>\n<html>\n<body>"
html_end = "</body>\n</html>"

def kelly(odds, prices, prices_neg):
    df = pd.concat([odds,prices,prices_neg], axis=1)
    df.columns = ["odds", "prices", "prices_neg"]
    df["odds"] = df["odds"] * .01
    df["win_y"] = (1 - df["prices"]) * .9
    df["b_y"] = df["win_y"] / df["prices"]
    df["q"] = 1 - df["odds"]
    df["f_y"] = df["odds"] - df["q"] / df["b_y"]

    # calculate same for nos
    df["win_n"] = (1 - df["prices_neg"]) * .9
    df["b_n"] = df["win_n"] / df["prices_neg"]
    df["f_n"] = df["q"] - df["odds"] / df["b_n"]

    
    return df
    

def setup_data(data, days=90):
    by_day = data.groupby(data.index.date).count()
    cutoff_date = by_day.index.values[len(by_day)-1] - datetime.timedelta(days=days)

    return by_day[cutoff_date:]

def price_data(market_number):
    url = f"https://www.predictit.org/api/marketdata/markets/{market_number}/"
    response = requests.get(url)

    return response.json()

def process_name(name):
    numbers = num_from_str(name)
    if 'fewer' in name:
        return str(numbers[0])
    elif 'more' in name:
        return str(numbers[0])
    else:
        return str(numbers[0]) + '-' + str(numbers[1])


def num_from_str(string): return [int(i) for i in string.split() if i.isdigit()]

def price_info(auction_data):
    Data = namedtuple("Data", "lower gap days_left start_date prices prices_neg")

    lower = min([num_from_str(i["name"])[0] for i in auction_data["contracts"]])

    # get gap, convoluted because dict
    for name in auction_data["contracts"]:
        gaps = num_from_str(name["name"])
        if len(gaps) > 1:
            gap = gaps[1] - gaps[0] + 1
            break

    # date info
    end_date = pd.to_datetime(auction_data["contracts"][0]["dateEnd"])
    end_date = end_date.tz_localize("US/Eastern")
    start_date = end_date - datetime.timedelta(days=7)
    time_left = end_date - datetime.datetime.now(tz=pytz.timezone("US/Eastern"))

    # convert it to a decimal form 2 days 12 minutes -> 2.5
    days_left = time_left.days + round((time_left.seconds / 86400), 3)

    prices = dict()
    prices_neg = dict()
    for contract in auction_data["contracts"]:
        prices[process_name(contract["name"])] = contract["bestBuyYesCost"]
        prices_neg[process_name(contract["name"])] = contract["bestBuyNoCost"]

    return Data(lower=lower,
                gap=gap,
                days_left=days_left,
                start_date=start_date,
                prices=prices,
                prices_neg=prices_neg)

    

def tweets(to_load, amount='basic'):
    """Load tweet dataset, just dates and IDs"""
    tweet_path = Path("data")

    while True:
        if tweet_path.exists():
            break
        else:
            tweet_path = ".." / tweet_path

    file_name = to_load + ".csv"
    tweet_path = tweet_path / file_name

    df = pd.read_csv(tweet_path)

    df.index = pd.to_datetime(df["created_at"])
    #df.index = df.index.tz_localize("US/Eastern")

    if amount == 'basic':

        try:
            df = pd.DataFrame(df['id_str'])
        except:
            df = pd.DataFrame(df["id"])
        df.columns = ['ID']

    return df


def prior_bucket_maker(data, lower, buckets=9, gap=10):
    
    prior_counts = dict()
    
    for i in range(buckets):
        if i == 0:
            prior_counts[str(lower)] = sum(data <= lower)
        elif i == buckets -1:

            lower_bound = (lower + i * gap) - (gap - 1)
            prior_counts[str(lower_bound)] = sum(data >= lower_bound)
        else:
            lower_bound = (lower + i * gap) - (gap - 1)
            upper_bound = (lower + i * gap)
            
            label = f"{lower_bound}-{upper_bound}"
            
            prior_counts[label] = sum((data >= lower_bound) & (data <= upper_bound))
            
    return prior_counts


        

    
