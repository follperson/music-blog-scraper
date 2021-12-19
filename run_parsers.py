#!/usr/bin/env python3
from parsers.pitchfork_parser import PitchforkArticleDownloader
from utils import random_wait
import json
import glob
import pandas as pd
import os
__author__ = 'Andrew Follmann'
__date__ = ''
__version__ = '0.1.1'

class_dict = {'pitchfork-albums': {'search_page': PitchforkArticleDownloader.SearchPages.SLUG.ALBUMS,
                                   'search_page_function': PitchforkArticleDownloader.SearchPages.FUNC.ALBUMS,
                                   'parser': PitchforkArticleDownloader},
              'pitchfork-songs': {'search_page': PitchforkArticleDownloader.SearchPages.SLUG.TRACKS,
                                  'search_page_function': PitchforkArticleDownloader.SearchPages.FUNC.TRACKS,
                                  'parser': PitchforkArticleDownloader}
              }


def slowly_gather(name, increment=1, max_range=100000):
    search_page = class_dict[name]['search_page']
    parser_class = class_dict[name]['parser']
    search_page_function = class_dict[name]['search_page_function']
    try:
        current_start_page = 1 + len([f for f in os.listdir('scraping\\' + name) if '.pkl' in f]) * increment
    except FileNotFoundError:
        os.mkdir('scraping\\' + name)
        current_start_page = 1
    while current_start_page < max_range:
        print('Start Page %s' % current_start_page)
        parser = parser_class(name=name,
                              start_page=current_start_page,
                              search_limit=increment,
                              search_page=search_page,
                              search_page_function=search_page_function)
        parser.main()
        current_start_page += increment


def get_all(name):
    parser_class = class_dict[name]['parser']
    parser = parser_class(name=name,
                          start_page=1,
                          search_limit=10000,
                          search_page=class_dict[name]['search_page'],
                          search_page_function=class_dict[name]['search_page_function'])
    parser.main()

def get_all_from_url_file(name, url_filepath):
    parser_class = class_dict[name]['parser']
    parser = parser_class(name=name,
                          start_page=1,
                          search_limit=10000,
                          search_page=class_dict[name]['search_page'],
                          search_page_function=class_dict[name]['search_page_function'])

    parser.main(from_url_filepath=url_filepath)


def main():
    # get_all('pitchfork-songs')
    # get_all_from_url_file('pitchfork-albums', 'scraping/pitchfork-albums_URLS/1-100001_2021-12-18.txt')
    get_all_from_url_file('pitchfork-songs', 'scraping/pitchfork-songs_URLS/1-10001_2021-12-18.txt')
    # compile_json_groups('Albums','json-scrape/pitchfork.com/reviews-albums*.json',n=100000)


def compile_json_groups(name, pattern='*.json', n=100):
    data = []
    for f in glob.glob(pattern)[:n]:
        with open(os.path.join(f),'r') as fo:
            data.append(json.load(fo))
    df = pd.DataFrame.from_records(data).T
    df.to_pickle(f'{name}.pkl')


if __name__ == '__main__':
    main()
