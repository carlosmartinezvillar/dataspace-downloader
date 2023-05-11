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

ODATA_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

class Downloader:
	def __init__(self):
		#API ACCESS
		self.access_token  = None
		self.refresh_token = None 

		#SEARCH PARAMETERS
		self.coords  = None
		self.params  = None
		self.query   = None
		self.session = None

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

	def download_product(self):
		pass

	def parse_product_list(self):
		pass

if __name__ == '__main__':

	username = os.getenv("USER")
	password = os.getenv("PASS")
	# username =
	# password = 

	D = Downloader()
	D.set_keycloak(username,password)
	pass