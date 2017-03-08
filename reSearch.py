# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup, SoupStrainer
import re
import argparse

#TODO also for English and other languages
HITLINK = "/wiki/Adolf_Hitler"

class wiki_site():
    """class for searching him"""
    def __init__(self, url, level=0, **kwargs):
        # the url of the current site
        self.url = url
        self.links = None
        self.heading = ''
        # Text of the site already visited
        self.road = kwargs.get('road', '')
        # how many sites have already been visited
        self.level = level
        #
        self.distance = None

    def load_soup(self):
        if not self.links:
            # an urllib2 object of the site
            website = urllib2.urlopen(self.url)
            # html text of the website
            html = website.read()
            # BeautifulSoup object that stores site
            soup = BeautifulSoup(html, 'lxml')
            # Masterpiece...not,
            #TODO other languages, and maybe also these Datei|Hilfe|...
            self.links = [li.get('href') for li in soup.findAll('a', attrs={'href': re.compile('^/wiki/(?!(Datei|Hilfe|Spezial|Wikipedia|Portal|Kategorie|Diskussion):).+$((?<!png)|(?<!jpg))')})]
            #self.links = [li.get('href') for li in soup.findAll('a', attrs={'href': re.compile('^/w')})]
            self.links = list(set(self.links))
            self.heading = soup.find(id='firstHeading').string

    def get_wiki_links(self):
        """get all internal links"""
        self.load_soup()
        #links = self.soup.findAll('a', attrs={'href': re.compile('^/wiki')})
        return self.links

    def get_heading(self):
        self.load_soup()
        return self.heading


def hit_gen(url):
    """masterpiece generator, for recursive search for him"""
    site = wiki_site(url)
    second_part_links = site.get_wiki_links()
    first_part_links = 'https://de.Wikipedia.org'
    # first search on site
    for spl in second_part_links:
        if spl == HITLINK:
            yield [url, first_part_links + spl]
            return
    # Nothing found so None
    print('Nothing found in ' + url)
    yield None
    # then search in all links untill he is found
    gen_list = [hit_gen(first_part_links + spl) for spl in second_part_links]
    tmp_result = None
    while tmp_result is None:
        for gen in gen_list:
            tmp_result = next(gen)
            if tmp_result:
                tmp_result.insert(0, url)
                yield tmp_result
                return
        # Nothing found, so ge to next level
        yield None

def links_handle():
    old_links, new_links = set()
    while True:
        new_links = yield old_links
        old_links.update(new_links)


def main():
    parser = my_parser()
    args = parser.parse_args()
    url1 = 'https://de.wikipedia.org/wiki/Hambach_an_der_Weinstra%C3%9Fe'
    url2 = 'https://de.wikipedia.org/wiki/Stra%C3%9Fburg'
    url3 = 'https://de.wikipedia.org/wiki/Neustadt_an_der_Weinstra%C3%9Fe'
    url4 = 'https://de.wikipedia.org/wiki/Wasserstoff'
    url = 'https://de.wikipedia.org/wiki/Ettore_Majorana'
    #HamWiki = wikiSite(url)
    #print(HamWiki.get_wiki_links())
    #print(HamWiki.get_heading())
    #wList, dist = hiSearch(HamWiki)
    total_links = links_handle()
    total_links.send(None)
    total_hit_generator = hit_gen(args.url if args.url else url)
    for res in total_hit_generator:
        if res:
            out = ''
            for lin in res:
                out += ', ' + lin
            print('Er wurde gefunden' + out)
            break
    #if wList:
    #    print("Er wurde gefunden. %s\n" % wList[-1].road)
    #    print("Es wurden %s Links geclickt" % wList[-1].distance)

def my_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str,
                        help=('The wikipedia url to search from,'
                              + 'right now only german'))
    return parser

if __name__ == '__main__':
    main()

#def hi_search(wSite):
#    """recursive search for him"""
#    #TODO overhead
#    if wSite.level >= 1:
#        return None, None
#    print(wSite.level, wSite.url)
#    links = wSite.get_wiki_links()
#    print(links)
#
#    for li in links:
#        #TODO also for English and other languages
#        w2Site = wikiSite('https://de.wikipedia.org' + li, wSite.level + 1)
#        #w2Site.road = wSite.road + ' dann ' + w2Site.get_heading()
#        # found him
#        if li == HITLINK:
#            # distance
#            w2Site.distance, wSite.distance = 0, 1
#            # on which links you have to click
#            w2Site.road = ' dann ist er auch schon da.'
#            wSite.road = wSite.get_heading() + w2Site.road
#            return [w2Site, wSite], 2
#        else:
#            # recursive
#            wList, wSite.distance = hiSearch(w2Site)
#            # if he was found
#            if wList:
#                wSite.road = wSite.get_heading() + ' dann ' + wList[0].road
#                return wList.append(wSite), wSite.distance + 1
#    return None, None
