#!venv/bin/python
# -*- coding: utf-8 -*-
import urllib2
import re
import argparse
import timeit
# for david implementation
import json
import requests
from lxml import html

from bs4 import BeautifulSoup, SoupStrainer

#TODO also for English and other languages
HITLINK = "/wiki/Adolf_Hitler"

class wiki_site():
    """class for searching him"""
    def __init__(self, url, **kwargs):
        # the url of the current site
        self.url = url
        self.links = None
        self.heading = ''
        self.clicked_name = kwargs.get('clicked_name', self.get_heading())
        # Text of the site already visited
        #self.road = kwargs.get('road', '')
        self.road = ''
        # how many sites have already been visited
        #self.level = level
        # how many links have to be clicked
        self.distance = None
        #
        self.country_string = re.search('(?<=https://)\w+(?=\.wikipedia.org)', url).group(0)

    def load_soup(self):
        if not self.links:
            # an urllib2 object of the site
            website = urllib2.urlopen(self.url)
            # html text of the website
            html = website.read()
            # BeautifulSoup object that stores site
            soup = BeautifulSoup(html, 'lxml')
            # Masterpiece...not,
            self.links, self.link_names = zip(*[[li.get('href'), ''.join(li.stripped_strings)] for li in soup.findAll('a', attrs={'href': re.compile('^/wiki/(?!\w+:).+$((?<!png)|(?<!jpg))')})])
            #self.links = list(set(self.links))
            self.heading = ''.join(soup.find(id='firstHeading').stripped_strings)

    def get_wiki_links(self):
        """get all internal links"""
        self.load_soup()
        return self.links

    def get_heading(self):
        self.load_soup()
        return self.heading



#def hit_gen(url, links_gen, **kwargs):
def hit_gen(url, **kwargs):
    """
    masterpiece generator, for recursive search for him

    args:
        url: real Url
        kwargs[link_name]: the name the link shown on site
    """
    # an wiki_site obj
    site = wiki_site(url, **kwargs)
    second_part_links = site.get_wiki_links()
    link_names = site.link_names
    # 2D-list with the links and the link-names
    #second_part_links_and_link_names = site.get_wiki_links()
    # the first part of the wikipedia url
    first_part_links = 'https://' + site.country_string + '.wikipedia.org'
    # somebody has entered his site directly
    if url == first_part_links + HITLINK:
        site.distance = 0
        site.road = '"' + site.get_heading() + '". Ziemlich schlau direkt seine Seite einzugeben'
        yield [site]
        return
    # first search on site
    print('Searching in ' + url)
    for spl, li_name in zip(second_part_links, link_names):
        # found him?
        if spl == HITLINK:
            hit_site = wiki_site(first_part_links + HITLINK, link_name=li_name)
            hit_site.get_heading()
            hit_site.distance = 0
            site.distance = 1
            hit_site.road = '"' + hit_site.heading + '". Ziemlich schlau direkt seine Seite einzugeben'
            site.road = '"' + site.clicked_name + '" dann "' + hit_site.clicked_name + '"'
            yield [site, hit_site]
            return
    # Nothing found
    yield None
    print('Going one layer deeper')
    # search in all links untill he is found
    gen_list = [hit_gen(first_part_links + spl, clicked_name=li_name) for spl, li_name in zip(second_part_links, link_names)]
    #print('and here')
    tmp_result = None
    while tmp_result is None:
        for gen in gen_list:
            tmp_result = next(gen)
            if tmp_result:
                site.road = '"' + site.clicked_name + '" dann ' + tmp_result[0].road
                site.distance = tmp_result[0].distance + 1
                tmp_result.insert(0, site)
                yield tmp_result
                return
        # Nothing found, so ge to next level
        yield None

def hit_search(url):
    #total_links = links_handle()
    #total_links.send(None)
    total_hit_generator = hit_gen(mobile_to_desktop(url))
    result = None
    for res in total_hit_generator:
        if res:
            result = res
            break
    return res

def mobile_to_desktop(url):
    res = re.search('(https://\w+)\.m(\.wikipedia.org.*)', url)
    return res.group(1) + res.group(2) if res else url

def main():
    parser = my_parser()
    args = parser.parse_args()
    url4 = 'https://de.wikipedia.org/wiki/Hambach_an_der_Weinstra%C3%9Fe'
    url2 = 'https://de.wikipedia.org/wiki/Stra%C3%9Fburg'
    url3 = 'https://de.wikipedia.org/wiki/Neustadt_an_der_Weinstra%C3%9Fe'
    url1 = 'https://de.wikipedia.org/wiki/Wasserstoff'
    url = 'https://de.wikipedia.org/wiki/Ettore_Majorana'
    res = hit_search(args.url if args.url else url)
    if res:
        print('Ich habe ihn gefunden. Klicke ' + res[0].road)


def my_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str,
                        help=('The wikipedia url to search from,'
                              + 'right now only german'))
    return parser

#if __name__ == '__main__':
#    start = timeit.default_timer()
#    main()
#    end = timeit.default_timer()
#    print(end - start)

#HOST = 'https://de.wikipedia.org'
#REGEX = re.compile('/wiki/(?!\w+:).+$((?<!png)|(?<!jpg))')
CACHE = {}


class cachedSearch:
    """cc David Lukwata"""
    def __init__(self, url, **kwargs):
        self.url = url
        self.stop = kwargs.get('stop', '/wiki/Adolf_Hitler')
        self.host = self.getHost()
        self.regex = re.compile('/wiki/(?!\w+:).+$((?<!png)|(?<!jpg))')
        self.result = ()

    def getPage(self, path):
        print(path + '...')
        r = requests.get(self.host + path)
        return r.content


    def getLinks(self, path):
        if path in CACHE:
            print(path + '... (cached)')
            return CACHE[path]

        tree = html.fromstring(self.getPage(path))
        links = tree.xpath('//div[@role="main"]//a/@href')
        links = filter(unicode, links)
        links = filter(self.regex.match, links)

        CACHE[path] = links

        return links

    def search(self, start):
        """

        args:
            start   url to start search from
            stop    url to which to find
        """
        start = self.getWiki(start)

        fifo = [(start,)]

        for each in fifo:
            # retrieve links from page
            links = self.getLinks(each[-1])

            for path in links:
                # check for him
                if path == self.stop:
                    self.result = each + (self.stop,)
                # add path to fifo
                new = each + (path,)
                fifo.append(new)

    def getHost(self):
        regexSearch = re.search('https://\w+\.wikipedia.org', self.url)
        return regexSearch.group(0)

    def getWiki(self, url):
        #print(self.host)
        regexSearch = re.search(self.host + '(.*)', url)
        return regexSearch.group(1)

    def getResult(self):

        print(self.result)


if __name__ == '__main__':
    parser = my_parser()
    args = parser.parse_args()
    try:
        with open('cache', 'rb') as file:
            CACHE = json.load(file)
    except IOError as e:
        print('Warning: Konnte Cache nicht lesen')

    #host = getHost(args.url)
    cSearch = cachedSearch(args.url)
    print(cSearch.getWiki(args.url))
    cSearch.search(args.url)
    print(cSearch.getResult())
    #print(getHost(args.url))

    with open('cache', 'wb') as file:
        json.dump(CACHE, file)
