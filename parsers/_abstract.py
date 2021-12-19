#!/usr/bin/env python3
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import json
from time import time as curtime, sleep
from datetime import date
import os
from utils import *
from cleaners import TextCleaners
import logging
from typing import Callable, Optional, List, Dict

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
}
logger = logging.getLogger('parser')
logger.setLevel(logging.DEBUG)
stream = logging.StreamHandler()
stream.setLevel(logging.INFO)
logger.addHandler(stream)

class AbstractParser(object):

    def __str__(self):
        return 'Blog Parser for ' + self.name

    def __init__(self, name: str, base_url: str, search_page: str, search_page_function: Callable,
                 parse_functions: Dict, search_limit: int = 2, start_page: int = 1,
                 exclude_link_flags: Optional[List] = None, cleaner=TextCleaners.AbstractCleaner,
                 today=date.today(), overwrite=False):
        self.name = name
        self.base_url = base_url
        self.search_page_slug = search_page
        self.search_page_function = search_page_function
        self.search_limit = search_limit
        self.start_page = start_page
        self.exclude_link_flags = exclude_link_flags if exclude_link_flags is not None else []
        self.parse_functions = parse_functions
        self.cleaner = cleaner
        self.HEADERS = HEADERS
        self.urls = []
        self.overwrite = overwrite
        self.long_name = f'{self.start_page}-{self.start_page + self.search_limit}_{today}'

    def get_urls_to_parse(self):
        search_url = self.base_url + '/' + self.search_page_slug + '/?page='
        pageno = self.start_page
        search_page = self.get_url(search_url + str(pageno))
        while search_page is not None and self.search_limit > (pageno - self.start_page):
            if search_page.status_code == 503:  # temporary off
                logger.warning('503 error')
                random_wait(60)
                continue
            soup = BeautifulSoup(search_page.content, features='lxml')
            links = self.parse_search_page(soup, self.search_page_function)
            links = [self.base_url + url if self.base_url not in url else url for url in links]
            pageno += 1
            random_wait(3)
            search_page = self.get_url(url=search_url + str(pageno))
            logger.info(f'Working on page {pageno}')
            self.urls += links

    def get_author(self, soup):
        raise NotImplementedError

    def get_genre(self, soup):
        raise NotImplementedError

    def get_title(self, soup):
        raise NotImplementedError

    def get_article_body(self, soup):
        raise NotImplementedError

    def get_review_score(self, soup):
        raise NotImplementedError

    def get_label(self, soup):
        raise NotImplementedError

    def get_date_pub(self, soup):
        raise NotImplementedError

    def get_article_type(self, soup):
        raise NotImplementedError

    def parse_search_page(self, soup, func):
        raise NotImplementedError('meant to be overwritten')

    @staticmethod
    def get_urls_from_filepath(filepath):
        with open(filepath, 'r') as f:
            return f.read().split('\n')

    def from_urls(self):
        self.urls = self.get_urls_from_filepath(f'scraping/{self.name}_URLS/{self.long_name}.txt')
        return self.urls

    def save_urls(self):
        os.makedirs(f'scraping/{self.name}_URLS', exist_ok=True)
        with open(f'scraping/{self.name}_URLS/{self.long_name}.txt','w') as f:
            f.write('\n'.join([url for url in self.urls]))

    def call_function(self, func, **kwargs):
        try:
            resp = func(**kwargs)
        except Exception as hmm:
            logger.warning(f'Failed with: {func.__name__}, {hmm}')
            resp = 'Error'
        return resp

    def get_url(self, url):
        for _ in range(5):
            try:
                resp = requests.get(url, headers=HEADERS)
            except requests.exceptions.ConnectionError as nointernet:
                logger.warning(f"Connection Error {url}")
                sleep(60)
            else:
                if resp.status_code == 404:
                    logger.warning("Cannot find %s" % url)
                    return
                elif resp.status_code == 503:
                    logger.warning(f"503 Error {url}")
                    random_wait(20)
                else:
                    return resp

    def parse_article_page(self, soup):
        data = dict()
        for name in self.parse_functions:
            func, kwargs_orig = self.parse_functions[name]
            kwargs = {'soup': soup}
            kwargs.update(kwargs_orig)
            data[name] = self.call_function(func, **kwargs)
        return data

    def collect_articles(self):
        folder = os.path.join(self.base_url.split('://')[-1].strip('.'))
        data = []
        for url in self.urls:
            data.append(
                self.collect_single_article(url, folder, self.overwrite)
            )
        return data

    def collect_single_article(self, url, folder, overwrite_json=True):
        clean_url = url.replace(self.base_url, '').strip('/').replace('/', '-')
        json_path = f'json-scrape/{folder}/{clean_url}.json'
        local_html = f'html-downloads/{folder}/{clean_url}.html'

        base_info = {'url': url, 'search_base': self.search_page_slug}
        max_filename_length = (255 - len(os.getcwd()))
        if len(local_html) > max_filename_length:
            local_html = local_html[:max_filename_length]
            json_path = json_path[:max_filename_length]
        if not overwrite_json:
            if os.path.exists(json_path):
                with open(json_path, encoding='utf8') as fo:
                    return json.load(fo)

        if os.path.exists(local_html):
            logger.info("Using Local Copy %s" % url)
            with open(local_html, 'rb') as html:
                content = html.read()
        else:
            logger.info("Using live copy %s" % url)
            random_wait(2)
            resp = self.get_url(url)
            if resp is None:
                return base_info
            content = resp.content
            if not os.path.exists(os.path.dirname(local_html)):
                os.makedirs(os.path.dirname(local_html))
            with open(local_html, 'wb') as html:
                html.write(content)
        soup = BeautifulSoup(content, parser='lxml', features="lxml")
        try:
            info = self.parse_article_page(soup)
            info.update(base_info)
        except Exception as wow:
            logger.error('Serious error with url %s, : %s' % (url, wow))
            return base_info

        os.makedirs(f'json-scrape/{folder}', exist_ok=True)
        with open(json_path, 'w', encoding='utf8') as fo:
            json.dump(info, fo, indent='  ', sort_keys=True)

        return info

    def main(self, from_url_filepath=''):
        logger.info(f'Starting {self.name}')
        if from_url_filepath:
            self.urls = self.get_urls_from_filepath(from_url_filepath)
        else:
            self.get_urls_to_parse()
            self.save_urls()
        data = self.collect_articles()
        df = pd.DataFrame.from_records(data).T
        df.to_pickle(f'scraping/{self.name}/{self.long_name}.pkl')
        logger.info(f"Completed {df.shape[0]}! Saved at: scraping/{self.name}/{self.long_name}.pkl")

