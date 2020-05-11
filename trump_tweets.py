import sys
import os
from pathlib import Path
from io import StringIO

sys.path.append("..")

import src.utils as utils
import src.poisson as poisson
from src.tweetdownloader import TweetDownloader

cwd = Path(__file__)
os.chdir(cwd.parent)

def main():

    fin_html = utils.html_head
    
    for market in utils.market_numbers:

        str_io = StringIO()
        print(market)

        tweets = TweetDownloader(to_load=market)

        # get response_data
        auction_data = utils.price_data(utils.market_numbers[market])
        data = utils.price_info(auction_data)
        tweets_so_far = len(tweets.dataset[:data.start_date])
        cutoff_data = utils.setup_data(tweets.dataset["id"])

        odds = poisson.basic_poisson(cutoff_data,
                                     data.days_left,
                                     tweets_so_far,
                                     lower=data.lower,
                                     gap=data.gap)

        t = utils.kelly(odds, data.prices)

        t.to_html(buf=str_io)

        html_str = str_io.getvalue()

        h1 = f"<h1>{market}</h1>\n"
        fin_html = fin_html + h1 + html_str

        
    fin_html = fin_html + utils.html_end

    with open('index.html', 'w') as out_file:
        out_file.write(fin_html)


if __name__ == "__main__":
    main()
