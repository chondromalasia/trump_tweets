import sys
import os
from pathlib import Path
from io import StringIO

import pandas as pd

sys.path.append("..")

import src.utils as utils
import src.poisson as poisson
from src.tweetdownloader import TweetDownloader
import src.gengamma as gengamma

"""NOTE: this is no longer how I solve this problem.
Now I would have a utils file with something like this:
root_path = Path(os.path.abspath(__file__)).parent.parent
which could be imported here"""
cwd = Path(__file__)
os.chdir(cwd.parent)

def main():

    # load header material for html
    fin_html = utils.html_head
    
    # loop through each of the tweet markets
    for market in utils.market_numbers:

        # NOTE: since 
        print(market)

        tweets = TweetDownloader(to_load=market)

        # get price data from website 
        auction_data = utils.price_data(utils.market_numbers[market])
        data = utils.price_info(auction_data)

        # get the number of tweets that have been tweeted already
        tweets_so_far = len(tweets.dataset[:data.start_date])

        cutoff_data = utils.setup_data(tweets.dataset["id"])

        prices_df = pd.DataFrame.from_dict(data.prices,
                                           orient="index")
        prices_neg_df = pd.DataFrame.from_dict(data.prices_neg,
                                               orient="index")

        odds = poisson.basic_poisson(cutoff_data,
                                     data.days_left,
                                     tweets_so_far,
                                     lower=data.lower,
                                     gap=data.gap)
        
        odds_g = gengamma.fin_gengamma(cutoff_data,
                                       data.days_left,
                                       tweets_so_far,
                                       data.lower,
                                       data.gap)

        # write lists etc to html, not sure it's the correct way
        str_io = StringIO()

        h1 = f"<h1>{market}</h1>\n"
        h2 = "<h2>Rawdog Poisson</h2>\n"

        t = utils.kelly(odds, prices_df, prices_neg_df)
        t[["odds", "prices", "f_y", "q", "prices_neg", "f_n"]].to_html(buf=str_io)
        html_str = str_io.getvalue()

        fin_html = fin_html + h1 + h2 + html_str

        h2 = "<h2>GenGamma</h2>\n"
        # this is almost certainly incorrect, fix it
        str_io = StringIO()

        t_g = utils.kelly(odds_g, prices_df, prices_neg_df)
        t_g[["odds", "prices", "f_y", "q", "prices_neg", "f_n"]].to_html(buf=str_io)

        html_str = str_io.getvalue()

        fin_html = fin_html + h2 + html_str

    fin_html = fin_html + utils.html_end

    with open('index.html', 'w') as out_file:
        out_file.write(fin_html)


if __name__ == "__main__":
    main()
