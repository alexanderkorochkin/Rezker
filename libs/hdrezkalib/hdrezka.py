import bs4.element
import requests
from bs4 import BeautifulSoup
import base64
from itertools import product
from functools import cached_property
import time

from libs.hdrezkalib.utils.types import (HdRezkaTVSeries, HdRezkaMovie, HdRezkaRating)
from libs.hdrezkalib.utils.stream import HdRezkaStream


class BeautifulSoupCustom(BeautifulSoup):
	def __repr__(self):
		return "<HTMLDocument>"


class HdRezkaApi:
	__version__ = 6.1

	def __init__(self, url):
		if type(url) == bs4.element.Tag:
			self.tagMode = True
			self.HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
			self.url = url["data-url"]
			self.tag: bs4.element.Tag = url
			self.site = self.url.split('//')[-1].split('/')[0]
		else:
			self.tagMode = False
			self.HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
			self.url = url
			self.site = url.split('//')[-1].split('/')[0]

	@cached_property
	def page(self):
		return requests.get(self.url, headers=self.HEADERS)

	@cached_property
	def soup(self):
		return BeautifulSoupCustom(self.page.content, 'html.parser')

	@cached_property
	def id(self):
		if self.tagMode:
			return self.tag['data-id']
		return self.soup.find(id="post_id").attrs['value']

	@cached_property
	def title(self):
		if self.tagMode:
			return self.tag.find("div", {"class": "b-content__inline_item-cover"}).find("img").attrs["alt"]
		return self.soup.find(class_="b-post__title").get_text().strip()

	@cached_property
	def title_en(self):
		try:
			out = self.soup.find(class_="b-post__origtitle").get_text().strip()
		except Exception:
			out = ''
		return out

	def findInfoTable(self, request, text_only=True):
		table = self.soup.find("table", {"class": "b-post__info"})
		for row in table.findAll("tr"):
			cells = row.findAll("td")
			if request in str(cells[0]):
				if text_only:
					return BeautifulSoup(str(cells[1]), 'html.parser').get_text()
				else:
					return BeautifulSoup(str(cells[1]), 'html.parser')
		return 'None'

	@cached_property
	def date(self):
		return self.findInfoTable('Дата выхода')

	@cached_property
	def age(self):
		return self.findInfoTable('Возраст')

	@cached_property
	def duration(self):
		return self.findInfoTable('Время')

	@cached_property
	def tagline(self):
		return self.findInfoTable('Слоган')

	@cached_property
	def genre(self):
		return self.findInfoTable('Жанр')

	@cached_property
	def description(self):
		return self.soup.find(class_="b-post__description_text").get_text().strip()

	@cached_property
	def thumbnail(self):
		if self.tagMode:
			return self.tag.find('img').attrs['src']
		return self.soup.find(class_="b-sidecover").find('img').attrs['src']

	@cached_property
	def year(self):
		if self.tagMode:
			return self.tag.find("div", {"class": "b-content__inline_item-link"}).find("div").get_text().split(', ')[0]
		return self.date.split(' ')[-2]

	@cached_property
	def country(self):
		if self.tagMode:
			return self.tag.find("div", {"class": "b-content__inline_item-link"}).find("div").get_text().split(', ')[1]
		return self.findInfoTable('Страна').split(', ')[0]

	@cached_property
	def summary_info(self):
		if self.tagMode:
			return self.tag.find("div", {"class": "b-content__inline_item-link"}).find("div").get_text()
		else:
			summary = [str(self.year), str(self.country), str(self.genre.split(', ')[0])]
		return ', '.join(summary)

	@cached_property
	def type(self):
		if self.tagMode:
			series = self.tag.find("span", {"class": "info"})
			if series is None:
				return HdRezkaMovie()
			else:
				return HdRezkaTVSeries()
		type_str = self.soup.find('meta', property="og:type").attrs['content']
		if type_str == "video.tv_series":
			return HdRezkaTVSeries()
		elif type_str == "video.movie":
			return HdRezkaMovie()
		return type_str

	@cached_property
	def rating(self):
		try:
			wrapper = self.findInfoTable('Рейтинги', text_only=False).findAll("span", {"class": "b-post__info_rates"})[-1]
			rating = wrapper.find("span", {"class": "bold"}).get_text()
			votes = wrapper.find("i").get_text()[1:-1].replace(' ', '')
			return HdRezkaRating(value=float(rating), votes=int(votes))
		except Exception:
			try:
				wraper = self.soup.find(class_='b-post__rating')
				rating = wraper.find(class_='num').get_text()
				votes = wraper.find(class_='votes').get_text().strip("()")
				return HdRezkaRating(value=float(rating), votes=int(votes))
			except Exception:
				return HdRezkaRating(value=float(0), votes=int(0))

	@cached_property
	def translators(self):
		arr = {}
		translators = self.soup.find(id="translators-list")
		if translators:
			children = translators.findChildren(recursive=False)
			for child in children:
				if child.text:
					arr[child.text] = int(child.attrs['data-translator_id'])
		if not arr:
			# auto-detect
			def getTranslationName(s):
				table = s.find(class_="b-post__info")
				for i in table.findAll("tr"):
					tmp = i.get_text()
					if tmp.find("переводе") > 0:
						return tmp.split("В переводе:")[-1].strip()

			def getTranslationID(s):
				initCDNEvents = {'video.series': 'initCDNSeriesEvents',
								 'video.movie'    : 'initCDNMoviesEvents'}
				tmp = s.text.split(f"sof.tv.{initCDNEvents[f'video.{self.type}']}")[-1].split("{")[0]
				return int(tmp.split(",")[1].strip())

			arr[getTranslationName(self.soup)] = getTranslationID(self.page)

		return arr

	@staticmethod
	def clearTrash(data):
		trashList = ["@","#","!","^","$"]
		trashCodesSet = []
		for i in range(2,4):
			startchar = ''
			for chars in product(trashList, repeat=i):
				data_bytes = startchar.join(chars).encode("utf-8")
				trashcombo = base64.b64encode(data_bytes)
				trashCodesSet.append(trashcombo)

		arr = data.replace("#h", "").split("//_//")
		trashString = ''.join(arr)

		for i in trashCodesSet:
			temp = i.decode("utf-8")
			trashString = trashString.replace(temp, '')

		finalString = base64.b64decode(trashString+"==")
		return finalString.decode("utf-8", 'ignore')

	@cached_property
	def otherParts(self):
		parts = self.soup.find(class_="b-post__partcontent")
		other = []
		if parts:
			for i in parts.findAll(class_="b-post__partcontent_item"):
				if 'current' in i.attrs['class']:
					other.append({
						i.find(class_="title").text: self.url
					})
				else:
					other.append({
						i.find(class_="title").text: i.attrs['data-url']
					})
		return other

	@staticmethod
	def getEpisodes(s, e):
		seasons = BeautifulSoup(s, 'html.parser')
		episodes = BeautifulSoup(e, 'html.parser')

		seasons_ = {}
		for season in seasons.findAll(class_="b-simple_season__item"):
			seasons_[ int(season.attrs['data-tab_id']) ] = season.text

		episodes_ = {}
		for episode in episodes.findAll(class_="b-simple_episode__item"):
			if int(episode.attrs['data-season_id']) in episodes_:
				episodes_[int(episode.attrs['data-season_id'])] [ int(episode.attrs['data-episode_id']) ] = episode.text
			else:
				episodes_[int(episode.attrs['data-season_id'])] = {int(episode.attrs['data-episode_id']): episode.text}

		return seasons_, episodes_

	@cached_property
	def seriesInfo(self):
		arr = {}
		for i in self.translators:
			js = {
				"id": self.id,
				"translator_id": self.translators[i],
				"action": "get_episodes"
			}
			r = requests.post(f"https://{self.site}/ajax/get_cdn_series/", data=js, headers=self.HEADERS)
			response = r.json()
			if response['success']:
				seasons, episodes = self.getEpisodes(response['seasons'], response['episodes'])
				arr[i] = {
					"translator_id": self.translators[i],
					"seasons": seasons, "episodes": episodes
				}
		return arr

	def getStream(self, season=None, episode=None, translation=None, index=0):
		def makeRequest(data):
			r = requests.post(f"https://{self.site}/ajax/get_cdn_series/", data=data, headers=self.HEADERS)
			r = r.json()
			if r['success']:
				arr = self.clearTrash(r['url']).split(",")
				stream = HdRezkaStream( season=season, episode=episode,
										name=self.title, translator_id=data['translator_id'],
										subtitles={'data':  r['subtitle'], 'codes': r['subtitle_lns']}
									  )
				for i in arr:
					res = i.split("[")[1].split("]")[0]
					video = i.split("[")[1].split("]")[1].split(" or ")[1]
					stream.append(res, video)
				return stream

		def getStreamSeries(self, season, episode, translation_id):
			# if not (season and episode):
			# 	raise TypeError("getStream() missing required arguments (season and episode)")
			
			tr_str = list(self.translators.keys())[list(self.translators.values()).index(translation_id)]

			if not season in list(self.seriesInfo[tr_str]['episodes']):
				raise ValueError(f'Season "{season}" is not defined')

			if not episode in list(self.seriesInfo[tr_str]['episodes'][season]):
				raise ValueError(f'Episode "{episode}" is not defined')

			return makeRequest({
				"id": self.id,
				"translator_id": translation_id,
				"season": season,
				"episode": episode,
				"action": "get_stream"
			})

		def getStreamMovie(self, translation_id):
			return makeRequest({
				"id": self.id,
				"translator_id": translation_id,
				"action": "get_movie"
			})

		if translation:
			if str(translation).isnumeric():
				if int(translation) in self.translators.values():
					tr_id = int(translation)
				else:
					raise ValueError(f'Translation with code "{translation}" is not defined')

			elif translation in self.translators:
				tr_id = self.translators[translation]
			elif translation == 'None':
				tr_id = list(self.translators.values())[0]
			else:
				raise ValueError(f'Translation "{translation}" is not defined')

		else:
			tr_id = list(self.translators.values())[index]

		if self.type == HdRezkaTVSeries:
			return getStreamSeries(self, int(season), int(episode), tr_id)
		elif self.type == HdRezkaMovie:
			return getStreamMovie(self, tr_id)
		else:
			raise TypeError("Undefined content type")

	def getSeasonStreams(self, season, translation=None, index=0, ignore=False, progress=None):
		season = str(season)

		if not progress:
			progress = lambda cur, all: None

		if translation:
			if str(translation).isnumeric():
				if int(translation) in self.translators.values():
					tr_id = int(translation)
				else:
					raise ValueError(f'Translation with code "{translation}" is not defined')

			elif translation in self.translators:
				tr_id = self.translators[translation]
			else:
				raise ValueError(f'Translation "{translation}" is not defined')

		else:
			tr_id = list(self.translators.values())[index]

		tr_str = list(self.translators.keys())[list(self.translators.values()).index(tr_id)]

		if not int(season) in list(self.seriesInfo[tr_str]['episodes']):
			raise ValueError(f'Season "{season}" is not defined')

		series = self.seriesInfo[tr_str]['episodes'][int(season)]
		series_length = len(series)

		streams = {}
		progress(0, series_length)

		for episode_id in series:
			def make_call(ep_id, retry=True):
				try:
					stream = self.getStream(season, ep_id, tr_str)
					streams[ep_id] = stream
					progress(len(streams), series_length)
					return stream
				except Exception as e:
					if retry:
						time.sleep(1)
						if ignore:
							return make_call(ep_id)
						else:
							return make_call(ep_id, retry=False)
					if not ignore:
						ex_name = e.__class__.__name__
						ex_desc = e
						print(f"{ex_name} > ep:{ep_id}: {ex_desc}")
						streams[ep_id] = None
						progress(len(streams), series_length)

			yield episode_id, make_call(episode_id)
