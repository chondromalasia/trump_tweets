from pathlib import Path

import pandas as pd

def rdt_tweets(amount='basic'):
    tweet_path = Path("data/realDonaldTrump.csv")

    while True:
        if tweet_path.exists():
            break
        else:
            tweet_path = ".." / tweet_path

    df = pd.read_csv(tweet_path)

    df.index = pd.to_datetime(df["created_at"])

    if amount == 'basic':

        df = pd.DataFrame(df['id_str'])
        df.columns = ['ID']

    return df

    
