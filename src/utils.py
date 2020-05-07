from pathlib import Path

import pandas as pd

def tweets(to_load, amount='basic'):
    tweet_path = Path("data")

    while True:
        if tweet_path.exists():
            break
        else:
            tweet_path = ".." / tweet_path

    file_name = to_load + ".csv"
    tweet_path = tweet_path / file_name

    df = pd.read_csv(tweet_path)

    df.index = pd.to_datetime(df["created_at"], utc=True)

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
        

    
