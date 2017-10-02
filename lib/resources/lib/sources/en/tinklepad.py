# -*- coding: utf-8 -*-

'''
    Covenant Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,urllib,urlparse,json,base64,time

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import directstream
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['tinklepad.at']
        self.base_link = 'http://tinklepad.at/'
        self.movie_link = 'watch-%s-online-free.html'

    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def sources(self, url, hostDict, locDict):
        sources = []

        try:
            if url == None: return sources
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['title']
            aliases = eval(data['aliases'])
            url = urlparse.urljoin(self.base_link, self.movie_link%cleantitle.geturl(title))
            url = client.request(url, output='geturl') 
            if url == None: return sources
            result = client.request(url) 
            result = client.parseDOM(result, 'li', attrs={'id':'playing_button'})
            result = client.parseDOM(result, 'a', ret='id')

            sources = []
            i = 0
            for url in result:
                #if i == 10: break
                try:
                    if 'google' in url:
                        valid, hoster = source_utils.is_host_valid(url, hostDict)
                        urls, host, direct = source_utils.check_directstreams(url, hoster)
                        for x in urls: sources.append({'source': host, 'quality': x['quality'], 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
             
                    else:
                        valid, hoster = source_utils.is_host_valid(url, hostDict)
                        if not valid: continue
                        q = 'SD'
                        if '1080p' in url or 'x1080' in url: q = '1080p'
                        elif '720p' in url or 'x720' in url: q = 'HD'
                        
                        sources.append({'source': hoster, 'quality': q, 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                    i+=1

                except:
                    pass

            return sources
        except Exception as e:
            return sources

    def resolve(self, url):
        if 'google' in url:
            return directstream.googlepass(url)
        else:
            return url
