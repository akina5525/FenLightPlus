# -*- coding: utf-8 -*-
from xml.dom.minidom import parseString as mdParse
from caches.meta_cache import meta_cache
from modules.metadata import movie_expiry, tvshow_expiry
from modules.utils import get_datetime, get_current_timestamp
from modules.kodi_utils import make_session, logger # Uncommented logger

url = 'http://www.omdbapi.com/?apikey=%s&i=%s&tomatoes=True&r=xml'
timeout = 20.0
session = make_session('http://www.omdbapi.com/')
metascore_icon, imdb_icon, tmdb_icon = 'metacritic.png', 'imdb.png', 'tmdb.png'

class OMDbAPI:
	def fetch_info(self, meta, api_key):
		imdb_id = meta.get('imdb_id')
		if not imdb_id or not api_key: return {}
		self.api_key = api_key
		data = self.process_result(imdb_id, meta)
		return data

	def process_result(self, imdb_id, meta):
		data = {}
		self.result = self.get_result(imdb_id)
		# logger("omdb_api.py", f'process_result - raw self.result from get_result: {self.result}') # Removed
		if not self.result: return {}
		self.result_get = self.result.get
		# Fetch awards_value using 'awards' (lowercase) as key for process_rating, as self.result uses lowercase.
		awards_value = self.process_rating('awards')
		# logger("omdb_api.py", f'process_result - fetched awards_value: {awards_value}') # Removed
		metascore_rating, tomatometer_rating, tomatousermeter_rating = self.process_rating('metascore'), self.process_rating('tomatoMeter'), self.process_rating('tomatoUserMeter')
		imdb_rating, tomato_image = self.process_rating('imdbRating'), self.process_rating('tomatoImage')
		if tomato_image: tomatometer_icon = 'rtcertified.png' if tomato_image == 'certified' else 'rtfresh.png' if tomato_image == 'fresh' else 'rtrotten.png'
		elif tomatometer_rating: tomatometer_icon = 'rtfresh.png' if int(tomatometer_rating) > 59 else 'rtrotten.png'
		else: tomatometer_icon = 'rtrotten.png'
		if tomatousermeter_rating: tomatousermeter_icon = 'popcorn.png' if int(tomatousermeter_rating) > 59 else 'popcorn_spilt.png'
		else: tomatousermeter_icon = 'popcorn_spilt.png'
		data = {
				'metascore': {'rating': '%s%%' %  metascore_rating, 'icon': metascore_icon},
				'tomatometer': {'rating': '%s%%' % tomatometer_rating, 'icon': tomatometer_icon},
				'tomatousermeter': {'rating': '%s%%' % tomatousermeter_rating, 'icon': tomatousermeter_icon},
				'imdb': {'rating': imdb_rating, 'icon': imdb_icon},
				'tmdb': {'rating': '', 'icon': tmdb_icon},
				'Awards': awards_value # Added 'Awards' key with fetched value
				}
		media_type = meta.get('mediatype')
		expiry_function = movie_expiry if media_type == 'movie' else tvshow_expiry
		# logger("omdb_api.py", f'process_result - final data being cached (just before adding to meta): {data}') # Removed
		meta['extra_ratings'] = data
		meta_cache.set(media_type, 'tmdb_id', meta, expiry_function(get_datetime(), meta), get_current_timestamp())
		return data

	def get_result(self, imdb_id):
		try:
			result = session.get(url % (self.api_key, imdb_id), timeout=timeout).text
			# logger("omdb_api.py", f'get_result - raw text response from OMDb: {result}') # Removed
			response_test = dict(mdParse(result).getElementsByTagName('root')[0].attributes.items())
			if not response_test.get('response', 'False') == 'True':
				# logger("omdb_api.py", 'get_result - OMDb API response was not "True"') # Removed
				return None
			return dict(mdParse(result).getElementsByTagName('movie')[0].attributes.items())
		except Exception as e: # Catch specific exception and log it
			# logger("omdb_api.py", f'get_result - EXCEPTION: {e}') # Removed
			return None

	def process_rating(self, rating_name):
		return self.result_get(rating_name, '').replace('N/A', '')

fetch_ratings_info = OMDbAPI().fetch_info
