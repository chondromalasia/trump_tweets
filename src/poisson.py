import sys
import datetime

import pandas as pd
import numpy as np
from scipy.stats import poisson

sys.path.append("..")

import src.utils as utils

def difference_dist(rv, upper, lower, tweets_so_far):
    adj_upper = upper - tweets_so_far
    adj_lower = lower - tweets_so_far
    
    return rv.cdf(adj_upper) - rv.cdf(adj_lower)

def basic_poisson(data, days_left, tweets_so_far, lower, buckets=9, gap=10):
    likelihoods = dict()
    
    mu = data.mean()

    adj_mu = int(round(mu * days_left))
    
    rv = poisson(adj_mu)
    
    
    for i in range(buckets):
        if i == 0:
            likelihoods[str(lower)] = rv.cdf(lower - tweets_so_far)
        elif i == buckets - 1:
            lower_bound = (lower + i * gap) - (gap - 1)
            likelihoods[str(lower_bound)] = (1 - rv.cdf(lower_bound - tweets_so_far))
            pass
        else:
            lower_bound = (lower + i * gap) - (gap - 1)
            upper_bound = (lower + i * gap)
            
            label = f"{lower_bound}-{upper_bound}"
            
            likelihoods[label] = difference_dist(rv,
                                                 upper_bound,
                                                 lower_bound,
                                                 tweets_so_far)
            
    # format dict
    for thing in likelihoods:
        likelihoods[thing] = float(f"{likelihoods[thing]:.3f}")*100
            
    return likelihoods
