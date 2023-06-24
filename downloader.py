import json
import yaml
import os
import xml.etree.ElementTree as ET
import requests
import argparse
import multiprocessing
import subprocess
from tqdm import tqdm
import numpy as np
import time

################################################################################
#GLOBAL VARS
################################################################################
OPENS_URL = "http://catalogue.dataspace.copernicus.eu/resto/api/collections/search.json?"
ODATA_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

################################################################################
# MAIN CLASS
################################################################################
class Downloader:
	"""
	Explanation of the class...
	"""
	def __init__(self):
		#API ACCESS
		self.access_token  = None
		self.refresh_token = None 

		#OBJECT SEARCH PARAMETERS
		self.coords  = None
		self.params  = None
		self.query   = None
		self.session = None


		# params = {
		# 	'coordinates': "",
		# 	'platformname': PLATFORMNAME,
		# 	'producttype': PRODUCT,
		# 	'cloudcoverpercentage': CLOUD_PERCNT,
		# 	'beginPosition': RANGE_TIME,
		# 	'endPosition:': RANGE_TIME,
		# 	'startdate': START_TIME,
		# 	'enddate': STOP_TIME,
		# 	'bands': BAND_RES
		# }


	def set_access_token(self, username: str, password: str) -> str:
		'''
		curl --location --request POST 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token' \
		  --header 'Content-Type: application/x-www-form-urlencoded' \
		  --data-urlencode 'grant_type=password' \
		  --data-urlencode 'username=<LOGIN>' \
		  --data-urlencode 'password=<PASSWORD>' \
		  --data-urlencode 'client_id=cdse-public'
		'''

		data = {
	        "client_id": "cdse-public",
	        "username": username,
	        "password": password,
	        "grant_type": "password",
	    	}

		try:
			r = requests.post(TOKEN_URL,data=data)
			r.raise_for_status()

		except Exception as e:
			raise Exception(
			    f"Keycloak token creation failed. Reponse from the server was: {r.json()}"
			)

		self.access_token = r.json()["access_token"]
        self.refresh_token = r.json()["refresh_token"]


    def regenerate_access_token(self):
		'''
		curl --location --request POST 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token' \
		  --header 'Content-Type: application/x-www-form-urlencoded' \
		  --data-urlencode 'grant_type=refresh_token' \
		  --data-urlencode 'refresh_token=<REFRESH_TOKEN>' \
		  --data-urlencode 'client_id=cdse-public'
		''' 
		data = {
			"client_id": "cdse-public",
			"grant_type": "refresh_token",
			"refresh_token": self.refresh_token
		}

		r = requests.post(TOKEN_URL,data=data)
		#CHECK resp content

		self.access_token = None


	def opensearch_uri(self):
		"""
		Uses the parameters currently set in the object to build a query for the openSearch API.
		"""
		"""
		EXAMPLES
		"http://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?
		startDate=2021-07-01T00:00:00Z&
		completionDate=2021-07-31T23:59:59Z&
		sortParam=startDate&
		maxRecords=20"

		http://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?
		cloudCover=[0,10]&
		startDate=2022-06-11T00:00:00Z&
		completionDate=2022-06-22T23:59:59Z&
		maxRecords=10


		http://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?
		startDate=2021-07-01T00:00:00Z&
		completionDate=2021-07-31T23:59:59Z&
		sortParam=startDate&
		maxRecords=20

		https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?
		cloudCover=[0,10]&
		startDate=2021-06-21T00:00:00Z&
		completionDate=2021-09-22T23:59:59Z&
		lon=21.01&
		lat=52.22

https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?cloudCover=[0,10]&startDate=2022-06-11T00:00:00Z&completionDate=2022-06-22T23:59:59Z&maxRecords=10&box=-1,1,-1,1
https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?cloudCover=[0,10]&startDate=2022-06-11T00:00:00Z&completionDate=2022-06-22T23:59:59Z&maxRecords=10&box=-21,23,-24,15

https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel1/describe.xml
		"""

	def search(self):
		pass

	def download_product(self):
		pass

	def parse_product_list(self):
		pass


if __name__ == '__main__':

	#SET AUTH FROM ENV OR YAML
	username = os.getenv("DS_USER")
	password = os.getenv("DS_PASS")
	# username =
	# password = 

	D = Downloader()
	D.set_keycloak(username,password)
	pass