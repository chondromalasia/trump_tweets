import sys

import pandas as pd
from scipy.stats import gengamma

sys.path.append("..")
import src.utils as utils

def fin_gengamma(data, days_to_go, tweets_so_far, lower, gap,  x=1000):

    k, w, loc, scale = gengamma.fit(data)
    rv = gengamma(k, w, loc=loc, scale=scale)
    
    whole_days = int(days_to_go)
    remainder = days_to_go - whole_days

    d_dict = dict()
    for i in range(whole_days + 1):
        a = rv.rvs(size=x).round().astype(int)
        d_dict[str(i)] = a

    df = pd.DataFrame.from_dict(d_dict)
    df[str(i)] = round(df[str(i)] * remainder).astype(int)

    summed = df.sum(axis=1) + tweets_so_far

    prior_counts = utils.prior_bucket_maker(summed, lower, gap=gap)

    weeklies = pd.DataFrame.from_dict(prior_counts,
                                      orient='index',
                                      columns=["Counts"])

    # turn it into a dict
    
    return (weeklies["Counts"] * 100) / weeklies["Counts"].sum()

        
