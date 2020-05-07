import configparser
from pathlib import Path
import logging
from collections import defaultdict
import datetime
import time

import tweepy
import pandas as pd

# move to main one?
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class TweetDownloader():

    def __init__(self, to_load="all"):

        self.api = self.make_api()
        self.to_load = to_load

        self.dataset = self.load_dataset(self.to_load)

        if type(self.dataset) == type(Path()):
            self.download_dataset()
            self.write_new_dataset()

        elif type(pd.DataFrame()) == type(self.dataset):
            self.update_dataset()
            self.write_updated_dataset()

    def write_updated_dataset(self):
        logger.info(f"Writing {self.file_path}")
        self.dataset.to_csv(self.file_path)

    def write_new_dataset(self):
        df = pd.DataFrame(self.new_tweets)
        df.to_csv(self.dataset, index=False)


    def update_tweets_dict_short(self, tweet):
        labels = ["created_at", "id", "text"]

        for label in labels:
            self.new_tweets[label].append(tweet[label])


    def download_dataset(self):
        """Get the last 120 days of tweets"""
        logger.info(f"Downloading: {self.to_load}")
        
        # get target date
        target_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=90)

        self.new_tweets = defaultdict(list)
        count = 0
        exit_ = False
        while True:
            logger.info(f"\tPage: {count}")
            if count <1:
                time.sleep(1)
                tweets = self.api.user_timeline(screen_name=self.to_load,
                                                count=200)
            else:
                time.sleep(1)
                tweets = self.api.user_timeline(screen_name=self.to_load,
                                                count=200,
                                                max_id=max_id)

            for tweet in tweets:
                tweet_json = tweet._json
                self.update_tweets_dict_short(tweet_json)

                if pd.to_datetime(tweet_json["created_at"]) < target_date:
                    exit_ = True
                    break


            if exit_:
                break
            logger.info(f"\tDate: {tweet_json['created_at']}")
            max_id = tweet_json["id"]
            count += 1
            
        
    def combine_datasets(self, new_tweets):

        df = pd.DataFrame.from_dict(new_tweets)
        df.index = pd.to_datetime(df["created_at"], utc=True)
        df = df[["id", "text"]]


        self.dataset = pd.concat([self.dataset, df])

        self.dataset.sort_index(inplace=True, ascending=False)

        self.dataset = self.dataset[["id", "text"]]

        # check for duplicates
        test = self.dataset.duplicated(['id'], keep='first')
        logger.info(f"Found: {test.sum()} duplicate rows")

        self.dataset = self.dataset[~test]


    def update_tweets_dict(self, new_tweets, tweet):

        labels = ["created_at", "id", "text"]

        for label in labels:
            new_tweets[label].append(tweet[label])

        return new_tweets

    def update_dataset(self):

        # get most recent id
        last_id = int(self.dataset.iloc[0]["id"])
        new_tweets = defaultdict(list)
        logger.info(f"Liberating {self.to_load}")

        count = 0
        exit_ = False
        while True:
            logger.info(f"\tPage: {count}")
            if count < 1:
                time.sleep(1)
                tweets = self.api.user_timeline(screen_name=self.to_load,
                                                count=200)
            else:
                time.sleep(1)
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
            df.sort_index(inplace=True, ascending=False)

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
    TweetDownloader(to_load='realDonaldTrump')
    TweetDownloader(to_load='whitehouse')
    TweetDownloader(to_load='potus')


if __name__ == "__main__":

    main()
