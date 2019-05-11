#!/usr/bin/env python3
from parsers._abstract import AbstractParser
from parsers import Static
from cleaners import TextCleaners
from utils import merge_dicts

class PitchforkArticleDownloader(AbstractParser):
    class SearchPages:
        def _feature(self, soup):
            node_class = 'title-link module__title-link'
            return [node['href'] for node in soup.find_all('a', {'class': node_class})]

        def _albums(self, soup):
            node_class = 'review__link'
            return [node['href'] for node in soup.find_all('a', {'class': node_class})]

        def _tracks(self, soup):
            node_classes = ['title-link', 'track-collection-item__track-link']
            return [node['href'] for node_class in node_classes for node in soup.find_all('a', {'class': node_class})]

        FEATURE = {'features': _feature}
        ALBUMS = {'reviews/albums': _albums}
        TRACKS = {'reviews/tracks': _tracks}
        ALL = merge_dicts(FEATURE, ALBUMS, TRACKS)

    class ExcludeLinkFlags:
        LISTS = 'lists-and-guides'
        PODCAST = 'podcast'
        PHOTOGALLERY = 'photo-gallery'
        SPONSORED = 'from-our-partners'
        PFEST = 'pitchfork-music-festival'
        FEST = 'festival-report'
        ALL = [LISTS, PODCAST, PHOTOGALLERY, SPONSORED, PFEST]  # ,PFEST]

    def __init__(self, name='Pitchfork', search_pages=None, search_limit=2, start_page=1):
        base_url = 'https://pitchfork.com'
        if search_pages is None:
            search_pages = self.SearchPages.ALL
        exclude_link_flags = self.ExcludeLinkFlags.ALL
        parse_functions = {Static.TITLE: (self.get_title, {}), Static.BODY: (self.get_article_body, {}),
                           Static.ARTICLETYPE: (self.get_article_type, {}), Static.RATING: (self.get_review_score, {}),
                           Static.DATEPUBLISHED: (self.get_date_pub, {})}

        cleaner = TextCleaners.PitchforkCleaner
        super(PitchforkArticleDownloader, self).__init__(name=name,
                                                         base_url=base_url,
                                                         search_pages=search_pages,
                                                         parse_functions=parse_functions,
                                                         search_limit=search_limit, start_page=start_page,
                                                         exclude_link_flags=exclude_link_flags,
                                                         cleaner=cleaner
                                                         )

    def parse_search_page(self, soup, func):
        links = func(self=self, soup=soup)
        return filter(lambda x: all(exclude not in x for exclude in self.exclude_link_flags), links)

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
        return soup.find('span', {'class':'score'})

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


    ########## MAIN ##########
