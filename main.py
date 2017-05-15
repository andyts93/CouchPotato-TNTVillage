from bs4 import BeautifulSoup
from couchpotato.core.helpers.encoding import simplifyString, tryUrlencode
from couchpotato.core.helpers.variable import tryInt
from couchpotato import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
import datetime
import traceback
import re
import requests
import time
import json
log = CPLog(__name__)


class TNTVillage(TorrentProvider, MovieProvider):
	urls = {
		'base_url': 'http://tntvillage.scambioetico.org',
		'search': 'http://www.tntvillage.scambioetico.org/src/releaselist.php'
	}
	payload = None
	desc = None
	
	http_time_between_calls = 1
	
	def _searchOnTitle(self, title, movie, quality, results):
		if len(self.conf('api_key')) > 0:
			try:
				params = dict(
					api_key=self.conf('api_key'),
					language='it_IT'
				)
				url = "https://api.themoviedb.org/3/movie/%s" % movie['info']['tmdb_id']
				resp = requests.get(url=url, params=params)
				data = json.loads(resp.text)
				it_title = data['title']
			except:
				log.error('Unable to find italian title')
				it_title = title
		row = []
		it_title = "%s %s" % (it_title, movie['info']['year'])
		log.info("Searching on TNTVillage with query %s" % it_title)
		payload = {'cat': 0, 'page': 1, 'srcrel': it_title}
		data = requests.post(self.urls['search'], data=payload)
		soup = BeautifulSoup(data.text)
		row += soup.findAll('tr')
		row.pop(0)
		
		if row and len(row) == 0:
			log.info("No torrents found for %s on tntvillage", title)
			return
		if row:
			try:
				self.parseResults(results, row, movie['info']['year'], quality, title, it_title)
			except:
				log.error('Failed parsing TNTVillage')
		else:
			log.info('No search results found')
	
	def standardize_title(self, name, it_title, title, year, quality, desc):
		s_y = re.findall(r'(\d{4})', name)
		s_yo = "%d" % year
		q_label = ""

		for q in quality['alternative'] + [quality['label']] + [quality['identifier']]:
			if str(q) in desc.lower():
				q_label = desc

		if s_yo in s_y:
			ret = "%s (%d) - %s, %s" % (title, year, quality['identifier'], q_label)
			log.info("NOME %s -> %s" % (name, ret))
			return ret
		return name

	def calc_age(self, age_str):
		import locale
		locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
		tdelta = datetime.datetime.now() - datetime.datetime.strptime(age_str, " %b %d %Y")
		return tdelta.days

	def getTorrentInfo(self, link):
		data = requests.get(link)
		html = BeautifulSoup(data.content)
		tds = html.findAll('td', text = re.compile('\d* mb', re.IGNORECASE))
		size = 0
		if len(tds) > 0:
			size = tds[0].text
		size = self.parseSize(size)

		datas = html.findAll('span', attrs = {'class': 'postdetails'})
		if len(datas) > 0:
			datas = re.findall(r':(.*?),', datas[0].text)[0]
		else:
			datas = " Jan 1 1970"
		age = self.calc_age(datas)
		
		titolo = html.findAll('td', id='sottotitolo')[1].text.strip('&nbsp;')
		desc_match = re.compile(ur'\[(.*)\]')
		s_res = re.search(desc_match, titolo)
		if s_res:
			g = s_res.group()
		self.desc = g
		return age, size

	def parseResults(self, results, entries, year, quality, title, it_title):
		new = {}
		for result in entries:
			tds = result.findAll('td')
			
			try:
				new['age'], new['size'] = self.getTorrentInfo(tds[6].a['href'])
				new['url'] = tds[0].a['href']
				new['detail_url'] = tds[6].a['href']
				new['id'] = tds[6].a['href'].split('showtopic=')[1]
				new['name'] = self.standardize_title(tds[6].a.text, it_title, title, year, quality, self.desc)
				new['seeders'] = tryInt(tds[4].text)
				new['leechers'] = tryInt(tds[3].text)
				new['score'] = self.conf('extra_score') + 20
			except Exception as e:
				log.info(e)
				continue

			results.append(new)
			
