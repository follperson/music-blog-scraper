#!/usr/bin/env python3
from re import match
from time import sleep
from numpy.random import random
from pandas import isnull

def get_text_from_nodes(nodes):
    return [node.get_text() for node in nodes if node.get_text() is not None]

def post_processing_list(x, Cleaner):
    try:
        if isnull(x):
            return x
    except ValueError as ok:
        pass
    cleaned = [post_processing_element(i,Cleaner.INLINE) for i in x if not any([match(expr, i) for expr in Cleaner.FULLREPLACE]) and isnull(i)]
    return cleaned

def post_processing_element(e, drop_dict):
    if isnull(e):
        return e
    e = e.strip()
    for key, value in drop_dict.items():
        if match(key, e):
            e = e.replace(match(key, e).group(), value)
    return e

def random_wait(maxi=10):
    sleep(maxi*random())

def merge_dicts(*args):
    out = dict()
    for d in args:
        out.update(d)
    return out
