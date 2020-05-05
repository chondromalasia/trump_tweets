import configparser
from pathlib import Path
import logging
from collections import defaultdict

import tweepy
import pandas as pd

logger = logging.getLogger()

class TweetDownloader():

    def __init__(self, to_load="all"):

        self.api = self.make_api()
        self.to_load = "realDonaldTrump"


        self.dataset = self.load_dataset(self.to_load)

        if type(self.dataset) == type(Path()):
            print("no dataset")
        elif type(pd.DataFrame()) == type(self.dataset):
            self.update_dataset()


    def combine_datasets(self, new_tweets):
        print(new_tweets["source"])
        df = pd.DataFrame.from_dict(new_tweets)
        df.index = pd.to_datetime(df["created_at"])
        print(df.index[0])
        print(df.index[0].tz)

        self.dataset = pd.concat([self.dataset, df])
        #self.dataset.sort_index()

    def update_tweets_dict(self, new_tweets, tweet):

        labels = ["source", "text", "created_at", "retweet_count", "id"]

        for label in labels:
            new_tweets[label].append(tweet[label])

        new_tweets["is_retweet"].append("dummy")

        return new_tweets

    def update_dataset(self):

        # get most recent id
        last_id = int(self.dataset.iloc[0]["id_str"])
        new_tweets = defaultdict(list)

        count = 0
        exit_ = False
        while True:
            if count < 1:
                tweets = self.api.user_timeline(screen_name=self.to_load,
                                                count=200)
            else:
                tweets = self.api.user_timeline(screen_name=self.to_load,
                                                count=200,
                                                max_id=max_id)

            for tweet in tweets:
                tweet_json = tweet._json

                new_tweets = self.update_tweets_dict(new_tweets, tweet_json)

                # if the id is lower than the last id from the stored tweets, exit
                if tweet_json["id"] <= last_id:
                    
                    exit_ = True
                    break

            if exit_:
                break
            
            max_id = tweet_json["id"]
                

            count += 1

        # combine datasets
        self.combine_datasets(new_tweets)

        

    def load_dataset(self, screen_name):

        data_path = Path("data")

        while True:
            if data_path.exists():
                break
            else:
                data_path = ".." / data_path

        file_name = screen_name + ".csv"

        self.file_path = data_path / file_name

        if self.file_path.exists():
            # load dataset
            df = pd.read_csv(self.file_path)
            df.index = pd.to_datetime(df["created_at"])

            return df
        else:
            return self.file_path
                


    def make_api(self):

        config = configparser.ConfigParser()

        config_path = Path('config.cfg')

        while True:
            if not config_path.exists():
                config_path = ".." / config_path
            else:
                break

        config.read(config_path)

        auth = tweepy.OAuthHandler(config['twitter']['api_key'], 
                                   config['twitter']['api_secret_key'])

        auth.set_access_token(config['twitter']['access_token'], 
                              config['twitter']['access_token_secret'])

        api = tweepy.API(auth,
                         wait_on_rate_limit=True,
                         wait_on_rate_limit_notify=True)

        try:
            api.verify_credentials()
        except Exception as e:
            logger.error("Error creating API", exc_info=True)
            raise e

        logger.info("API created")

        return api

def main():
    td = TweetDownloader()


if __name__ == "__main__":

    main()
