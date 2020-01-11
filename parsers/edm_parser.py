from ._abstract import AbstractParser
from cleaners import TextCleaners
from parsers import Static


class YourEDMParser(AbstractParser):
    class SearchPages:
        def _editorial(self, soup):
            return [node.find('a')['href'] for node in soup.find_all('h2', {'class': 'cb-post-title'})]

        EDITORIAL = {'master-editorial': _editorial}
        ALL = [EDITORIAL]

    class ExcludeLinkFlags:
        LISTS = 'lists-and-guides'
        PODCAST = 'podcast'
        PHOTOGALLERY = 'photo-gallery'
        SPONSORED = 'from-our-partners'
        PFEST = 'pitchfork-music-festival'
        FEST = 'festival-report'
        ALL = [LISTS, PODCAST, PHOTOGALLERY, SPONSORED, PFEST]  # ,PFEST]

    def __init__(self, name='YourEDM', search_page=SearchPages.EDITORIAL, search_limit=2, start_page=1):
        assert search_page in self.SearchPages.ALL
        base_url = 'https://www.youredm.com'

        exclude_link_flags = self.ExcludeLinkFlags.ALL
        parse_functions = {Static.TITLE: (self.get_title, {}), Static.BODY: (self.get_article_body, {}),
                           Static.ARTICLETYPE: (self.get_article_type, {}), Static.RATING: (self.get_review_score, {}),
                           Static.DATEPUBLISHED: (self.get_date_pub, {})}

        cleaner = TextCleaners.PitchforkCleaner
        super(YourEDMParser, self).__init__(name=name,
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

    def get_genre(self, soup):
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
