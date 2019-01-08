#!/usr/bin/env python3
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re

__author__ = 'Andrew Follmann'
__date__ = ''
__version__ = '0.0.5'

class YourEDMArticleDownloader(object):
    def __init__(self, max_search=9999):
        self.name = 'Your EDM'
        self.links = []
        self.max_search = max_search

    def scour_list_pages(self, soup):
        links = [node.find('a')['href'] for node in soup.find_all('h2', {'class': 'cb-post-title'})]
        self.links += links

    def get_pages(self):
        root_search = 'https://www.youredm.com/master-editorial'
        search = requests.get(root_search)
        soup = BeautifulSoup(search.content)
        page = 1
        while search.status_code not in [404, 503]:
            if page > self.max_search:
                break
            soup = BeautifulSoup(search.content)
            self.scour_list_pages(soup)
            page += 1 # first page is 0, then second is 2
            search = requests.get(root_search + '/page/' + str(page))

    def get_article(self, soup):
        head = soup.find('title')
        title = head.text
        body = head.find_next('section')
        paragraphs = body.find_all_next('p',)
        text = []
        author = soup.find('span',{'class':'cb-author'}).text

        for p in paragraphs:
            try: # todo improve
                p['class']
            except KeyError as ignore:
                text.append(p.text)
        return title, author, text

    def scour_articles(self):
        data = []
        for link in self.links:
            resp = requests.get(link)
            soup = BeautifulSoup(resp.content)
            try:
                t,a,d = self.get_article(soup)
            except Exception as huh:
                print('ERROR', huh,'\n'+link)
                continue
            data.append([link,t,a,d])
            # print(t)
        self.df_articles = pd.DataFrame(data, columns=['url','Title','Author','Body'])

    def main(self):
        self.get_pages()
        self.scour_articles()


class PitchforkArticleDownloader(object):
    class ArticleTypes:
        FEATURE = 'features'
        ALBUMS = 'reviews/albums'
        TRACKS = 'reviews/tracks'
        ALL = [TRACKS,FEATURE, ALBUMS, ]

    # class SearchFlags:

    ARTICLE_LIST = {ArticleTypes.FEATURE: ['title-link module__title-link'],
                    ArticleTypes.ALBUMS: ['review__link'],
                    ArticleTypes.TRACKS: ['title-link', 'track-collection-item__track-link']}
    class ExcludeLinkFlags:
        LISTS = 'lists-and-guides'
        PODCAST = 'podcast'
        PHOTOGALLERY = 'photo-gallery'
        SPONSORED = 'from-our-partners'
        PFEST = 'pitchfork-music-festival'
        # FEST = 'festival-report'
        ALL = [LISTS, PODCAST, PHOTOGALLERY, SPONSORED, PFEST]  # ,PFEST]

    class BodyCleaner:
        INLINE = {'\xa0': ' ','\n':' '} # to strip characters in the body of the text
        FULLREPLACE = [re.compile('^\s*$'),re.compile('^Listen to the track below$',re.I),
                       re.compile('^Add to queue',re.I),re.compile('All rights reserved',re.I)] # to remove full text entries


    def __init__(self, max_search=9999):
        self.name = 'Pitchfork'
        self.root_website = 'https://www.pitchfork.com'
        self.article_headers = dict()
        self.max_search = max_search
        self.df_articles = pd.DataFrame()

    def initialize(self):
        self.article_headers = {article: [] for article in self.ArticleTypes.ALL}

    ### GET ARTICLE URLS ####

    def scour_list_pages(self, soup, article_type):
        links = [self.root_website + node['href'] for class_name in self.ARTICLE_LIST[article_type] for node in soup.find_all('a', {'class': class_name})]
        links = filter(lambda x: all(exclude not in x for exclude in self.ExcludeLinkFlags.ALL), links)
        self.article_headers[article_type] += links

    def get_article_list(self, article_type):
        root_search = self.root_website + '/' + article_type + '/?page='
        page = 1
        search = requests.get(root_search + str(page))
        soup = BeautifulSoup(search.content)
        while search.status_code not in [404, 503]:
            if page > self.max_search:
                break
            print(page)
            self.scour_list_pages(soup, article_type)
            page += 1 # first page is 0, then second is 2
            search = requests.get(root_search + str(page))
            soup = BeautifulSoup(search.content)

    ### GET ARTICLE DATA ####

    def get_author(self, soup):
        authors = ', '.join([node.text for node in soup.find_all('a', {'class': 'authors-detail__display-name'})])
        if len(authors) == 0:
            try:
                authors += soup.find('ul', {'class': 'authors-detail'}).find_next('li').text
                print(authors)
            except Exception:
                authors = self.name + ' Generic'
        return authors

    def get_title(self, soup):
        return soup.find('title').text

    def get_article_body(self, soup):
        return [p.text for p in soup.find_all('p')]

    def get_review_score(self, soup):
        return soup.find('span', {'class':'score'}).text

    def get_date_pub(self, soup):
        node = soup.find('time',{'class':"pub-date"})
        for want in ['datetime','title']:
            try:
                return node[want]
            except KeyError as ok:
                pass
        return node.text

    def get_article_type(self, soup):
        return soup.find('a', {'class':"type"}).text

    def get_article(self, soup):
        data = []
        for func in [self.get_title, self.get_author, self.get_article_body, self.get_date_pub, self.get_article_type]:
            resp = self.log_attempt(func, soup=soup)
            data.append(resp)
        return data

    def log_attempt(self, func, *args, **kwargs):
        try:
            resp = func(*args, **kwargs)
        except Exception as huh:
            resp = 'No Data'
        return resp

    def scour_articles(self):
        for article_header in self.article_headers:
            data = []
            for link in self.article_headers[article_header]:
                if link.count(self.root_website) > 1:  # non-standard link already included root
                    link = link[len(self.root_website):]
                try:
                    resp = requests.get(link)
                except (requests.exceptions.ConnectionError):
                    continue
                soup = BeautifulSoup(resp.content)
                t,a,d,date,a_type = self.get_article(soup)
                data.append([link,t,date,a_type,a,d])
            df_articles = pd.DataFrame(data, columns=['url', 'title', 'date','article-subtype', 'author', 'raw'])
            df_articles['article-type'] = article_header
            self.df_articles = self.df_articles.append(df_articles)

    def post_processing(self):
        self.df_articles['body-cleaned'] = self.df_articles['raw'].apply(lambda x: post_processing(x, self.BodyCleaner))

    ########## MAIN ##########
    def main(self):
        self.initialize()
        for article_type in self.ArticleTypes.ALL:
            print('Working On %s' % article_type)
            self.get_article_list(article_type)
        self.scour_articles()
        self.post_processing()
        self.df_articles.to_excel('corpus\\%s_%s.xlsx' %(self.name, self.max_search))


def post_processing(body, BodyCleaner):
    cleaned = [i for i in body if not any([re.match(expr, i) for expr in BodyCleaner.FULLREPLACE])]
    for i in range(len(cleaned)):
        for drop in BodyCleaner.INLINE:
            cleaned[i].replace(drop, BodyCleaner.INLINE[drop])
    return cleaned


if __name__ == '__main__':
    pass