###
# Copyright (c) 2012, Dan
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import sys
import json
import socket
import unicodedata
from lxml import html

if sys.version_info[0] >= 3:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
    def u(s):
        return s
else:
    import urllib2
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError, URLError
    def u(s):
        return unicode(s, "unicode_escape")

class IMDb(callbacks.Plugin):
    """Add the help for "@plugin help IMDb" here
    This should describe *how* to use this plugin."""
    threaded = True
    
    http_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:5.0) Gecko/20100101 Firefox/5.0"
    }

    def __init__(self, irc):
        self.__parent = super(IMDb, self)
        self.__parent.__init__(irc)
        
    def createRoot(self, url):
        """opens the given url and creates the lxml.html root element"""
        pagefd = utils.web.getUrlFd(url,headers=self.http_headers)
        root = html.parse(pagefd)
        return root

    def imdbSearch(self,searchString):
        """searches the given string on imdb.com"""
        searchEncoded = urlencode({'q' : searchString})
        url = 'https://www.imdb.com/find?&s=tt&' + searchEncoded
        root = self.createRoot(url)
        element = root.findall('//td[@class="result_text"]/a')
        url = 'https://www.imdb.com' + element[0].attrib['href']
        url = url[:url.find('?ref_')]
        return url

    def imdb(self, irc, msg, args, text):
        """<movie>
        output info from IMDb about a movie"""

        # do a google search for movie on imdb and use first result
        query = 'site:http://www.imdb.com/title/ %s' % text
        imdb_url = None
        google_plugin = irc.getCallback('Google')
        if google_plugin:
            results = google_plugin.decode(google_plugin.search(query, msg.args[0]))

            # use first result that ends with a / so that we know its link to main movie page
            for r in results:
                if r['url'][-1] == '/':
                    imdb_url = r['url']
                    break
        else:
            imdb_url = self.imdbSearch(text)

        if imdb_url is None:
            irc.error('\x0304Couldnt find a title')
            return

        root = self.createRoot(imdb_url)
 
        # these 2 closures return functions that are used with rules
        # to turn each xpath element into its final string
        def text(*args):
            def f(elem):
                elem = elem[0].text.strip()
                for s in args:
                    elem = elem.replace(s, '')
                return elem
            return f

        def text2(*args):
            def f(elem):
                elem = ' '.join(elem[0].text_content().split())
                for s in args:
                    elem = elem.replace(s, '')
                return elem
            return f

        # Dictionary of rules for page scraping. has each xpath and a function to convert that element into its final string.
        # Each value is a tuple of tuples so that you can provide multiple sets of xpaths/functions for each piece of info.
        # They are tried In order until one works.
        rules = { # 'title': (   ('xpath rule', function), ('backup rule', backup_function), ...   )
            'title':    (('//head/title', text(' - IMDb', '')),),
            'name':     (('//h1/span[@itemprop="name"]', text()), ('//h1[@itemprop="name"]', text())),
            'year':     (('//h1[@itemprop="name"]/span/a', text()),('//a[@title="See more release dates"]', text())),
            'genres':   (('//div[@itemprop="genre"]',   text2('Genres: ')),),
            'language': (('//div[h4="Language:"]',      text2('Language: ')),),
            'stars':    (('//div[h4="Stars:"]',         text2('Stars: ', '| See full cast and crew', '| See full cast & crew', u('\xbb'))),),
            'plot_keys':(('//span[@itemprop="keywords"]', lambda x: ' | '.join(y.text for y in x)),
                        ('//div[h4="Plot Keywords:"]', text2(' | See more', 'Plot Keywords: '))),
            'rating':   (('//div[@class="titlePageSprite star-box-giga-star"]', text()),
                        ('//span[@itemprop="ratingValue"]', text())),
            'description': (('//p[@itemprop="description"]', text2()), ('//div[@itemprop="description"]', text2())),
            'director': (('//div[h4="Director:" or h4="Directors:"]', text2('Director: ', 'Directors: ')),),
            'creator':  (('//div[h4="Creator:"]/span[@itemprop="creator"]/a/span',  text()),),
            'runtime':  (('//time[@itemprop="duration"]', text()), ('//div[h4="Runtime:"]/time', text()))
        }

        # If IMDb has no rating yet
        info = {'rating': '-'}

        # loop over the set of rules
        for title in rules:
            for xpath, f in rules[title]:
                elem = root.xpath(xpath)
                if elem:
                    info[title] = f(elem)
                    try: # this will replace some unicode characters with their equivalent ascii. makes life easier on everyone :)
                         # it's obviously only useful on unicode strings tho, so will TypeError if its a standard python2 string, or a python3 bytes
                        info[title] = unicodedata.normalize('NFKD', info[title])
                    except TypeError:
                        pass
                    break

        info['url'] = imdb_url

        def reply(s): irc.reply(s, prefixNick=False)

        # output based on order in config. lines are separated by ; and fields on a line separated by ,
        # each field has a corresponding format config
        for line in self.registryValue('outputorder', msg.args[0]).split(';'):
            out = []
            for field in line.split(','):
                try:
                    out.append(self.registryValue('formats.'+field, msg.args[0]) % info)
                except KeyError:
                    continue
            if out:
                reply('  '.join(out))

    imdb = wrap(imdb, ['text'])

Class = IMDb

# vim:set shiftwidth=4 softtabstop=4 expandtab:
