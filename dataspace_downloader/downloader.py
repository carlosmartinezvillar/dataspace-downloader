import json
import yaml
import os
import xml.etree.ElementTree as ET
import requests
import argparse
import multiprocessing
import subprocess as sp
import time

####################################################################################################
# CLASSES
####################################################################################################
class Downloader():
	"""
	Explanation of the class...
	"""
	def __init__(self,input_yaml,out_dir):

		#CHECK ARGS
		if not os.path.isfile(input_yaml):
			print("Input YAML file not found in path given.")
			raise FileNotFoundError
		self.input_yaml = input_yaml

		if not os.path.isdir(out_dir):
			print("Output dir not found.")
			raise FileNotFoundError
		if out_dir[-1] == '/':
			out_dir = out_dir[0:-1]
		self.out_dir = out_dir

		#SATELLITE PARAMETERS
		self.instrument  = "MSI"
		self.productType = "S2MSI2A"
		self.sensorMode  = None #some "null" some INS-NOBS for S2 ¿?
		self.bands       = None							   	     #<--- INPUT YAML

		#AOI PARAMETERS
		self.cloudCover     = None #e.g. 10.00 				      #<--- INPUT YAML
		self.startDate      = None #e.g. 2021-10-01T21:37:00.000Z #<--- INPUT YAML
		self.endDate        = None 								  #<--- INPUT YAML
		self.lon            = None #EPSG:4326 e.g. 21.01 		  #<--- INPUT YAML
		self.lat            = None 								  #<--- INPUT YAML
		self.geometry       = None 								  #<--- INPUT YAML

		#JSON RETURN PARAMETERS
		self.maxRecords = 100
		self.sortParam  = "startDate"
		self.sortOrder  = "ascending"

		#SEARCH PARAMETERS/YAML
		self.file_parameters = None
		self.parse_yaml()
		self.check_yaml_inputs()
		self.query    = None
		self.names    = [] #["*.SAFE"]
		self.s3_ids   = [] #["/eodata/Sentinel-2/MSI/.../*.SAFE"]
		self.polygons = [] #[{"type":"Polygon","coordinates":[[[]]]}]

		#DOWNLOAD PARAMETERS
		self.RCLONE_MAX = "16"
		self.ODATA_BASE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products?"
		self.s3_band_paths = []


	def parse_yaml(self):
		'''
		Set bands, cloudCover, startDate, completionDate, lon and lat or geometry
		'''

		#check file exists
		try:
			with open(self.input_yaml,'r') as fp:
				yaml_data = yaml.safe_load(fp)
		except FileNotFoundError:
			print(f"File {self.input_yaml} not found.")
		except yaml.YAMLError as e:
			print(f"Error parsing YAML: {e}")
		self.file_parameters = yaml_data


	def check_yaml_inputs(self):
		'''
		Check parameters are correct and leave as None if missing.
		TODO: Missing further checks.
		'''

		#1. cloud cover
		if "cloudCover" in self.file_parameters:
			self.cloudCover = self.file_parameters['cloudCover']
		else:
			self.cloudCover = "5.00"

		#2. dates and date format
		if "startDate" in self.file_parameters:
			self.startDate = self.file_parameters['startDate']

		if "endDate" in self.file_parameters:
			self.endDate = self.file_parameters['endDate']

		#3.aoi -- Set in order useful for user feedback
		# check lon,lat -- if given set to
		if ("lon" in self.file_parameters and "lat" in self.file_parameters):
			self.lon = self.file_parameters['lon']
			self.lat = self.file_parameters['lat']

		#check geometry
		if "geometry" in self.file_parameters:
			self.geometry = self.file_parameters['geometry']
		#missing format check <----	

		if self.geometry==None and self.lon==None and self.lat==None:
			#nothing set
			print("Search area not set. Check 'geometry' or 'lon','lat' in input yaml file.")

		#4. bands
		if "bands" in self.file_parameters:
			self.bands = self.file_parameters['bands']


	def download_metadata(self):
		'''
		DEPRECATED.
		'''
		#Set download list
		remote_paths = [f"{path}/MTD_*.xml" for path in self.s3_ids]

		#Write temp list file
		temp_path = f"{self.out_dir}/mtd_temp.txt"
		with open(temp_path,'w') as fp:
			fp.writelines(remote_paths)

		#Download
		proc0 = sp.run([
			"rclone","copy",
			"--include-from",temp_path,
			"esa:",self.out_dir,"-P",
			"--transfers",RCLONE_MAX,"--dry-run"])

		#delete temp list
		os.remove(temp_path)


	def parse_xml(self,path):
		'''
		DEPRECATED.
		'''
		mtd_namespace = {
			'n1':"https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd",
			'other':"http://www.w3.org/2001/XMLSchema-instance",
			'another':"https://psd-14.sentinel2.eo.esa.int/PSD/User_Product_Level-2A.xsd"
		}

		# get datastrip and granule
		root      = ET.parse(path).getroot()
		prod_info = root.find('n1:General_Info',namespaces=mtd_namespace).find('Product_Info')
		granule   = prod_info.find('Product_Organisation').find('Granule_List').find('Granule')
		datastrip = granule.attrib['datastripIdentifier'].split('_')[-2][1:]
		return granule,datastrip


	def build_odata_query(self):
		'''
		Method to set up an OData query for CDSE. Takes previously loaded parameters.
		'''
		#Filters
		collection  = "Collection/Name eq 'SENTINEL-2'"
		producttype = f"Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType'" \
						f" and att/OData.CSC.StringAttribute/Value eq '{self.productType}')"
		aoi         = f"OData.CSC.Intersects(area=geography'SRID=4326;{self.geometry}')"
		clouds      = f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover'" \
						f" and att/OData.CSC.DoubleAttribute/Value le {self.cloudCover})"
		date_start  = f"ContentDate/Start gt {self.startDate}"
		date_final  = f"ContentDate/Start lt {self.endDate}"

		#Join filters
		filters_str = " and ".join([collection,producttype,aoi,clouds,date_start,date_final])

		#Join query params
		req_filter = f"$filter={filters_str}"
		req_top    = f"$top={self.maxRecords}"
		req_skip   = f"$skip=0"
		req_count  = "$count=True"
		req_order  = "$orderby=ContentDate/Start desc"
		req = "&".join([req_filter,req_top,req_skip,req_order,req_count])

		self.query = self.ODATA_BASE_URL + req
		return self.query


	def search_odata(self,query=None):
		#Get first page
		req  = self.build_odata_query()
		resp = requests.get(req)

		#Check response
		if resp.status_code !=200:
			print(resp.text)
			return

		#convert to json
		resp_json = resp.json()
		print(f"Products found: {resp_json['@odata.count']}.")

		#No matching results
		if resp_json['@odata.count'] == 0:
			return

		#handle page count
		n_pages = resp_json['@odata.count'] // self.maxRecords
		if resp_json['@odata.count'] % self.maxRecords > 0:
			n_pages += 1
		current_page = 1

		#iterate through pages
		while True:

			#stdout
			print(f"Retrieving pages [{current_page}/{n_pages}]")

			#store entries
			for entry in resp_json['value']:
				self.names.append(entry['Name'])
				self.polygons.append(entry['Footprint'])
				self.s3_ids.append(entry['S3Path'])

			# more pages?
			if "@odata.nextLink" not in resp_json:
				break

			# Get next page
			next_page = resp_json['@odata.nextLink']
			resp      = requests.get(next_page)

			if resp.status_code !=200:
				print("STATUS CODE!=200.")
				print(resp.text)
				break

			resp_json = resp.json()			
			current_page += 1


		#LOG THE SEARCH -- links
		log = [f"{product}\t{s3}" for product,s3 in zip(self.names,self.s3_ids)]
		with open(f"{self.out_dir}/search_results.tsv",'w') as fp:
			fp.write("\n".join(log))

		#LOG THE SEARCH -- geo
		log = [f"{product}\t{poly}" for product,poly in zip(self.names,self.polygons)]
		with open(f"{self.out_dir}/search_results_geometries.tsv",'w') as fp:
			fp.write("\n".join(log))

		#LOG DOWNLOAD QUEUE -- include files for S3 client (rclone)
		for s3folder in self.s3_ids:
			for band in self.bands:
				self.s3_band_paths.append(f"{s3folder}/GRANULE/*/IMG_DATA/R10m/*_{band}.jp2")

		temp_file = f"{self.out_dir}/download_queue.txt"
		with open(temp_file,'w') as fp:
			fp.write(str("\n".join(self.s3_band_paths)))


		return


	def download(self):
		'''
		Use metadata stored in Downloader object and retrieve products via S3.
		'''
		queue_file = f"{self.out_dir}/download_queue.txt"

		#download
		proc0 = sp.run([
			"rclone","copy",
			"--include-from",queue_file,
			"esa:",self.out_dir,"-P",
			"--transfers",self.RCLONE_MAX,"--dry-run"])

		#This downloads whole structure, so something like this is needed:
		#find ./eodata/Sentinel-2/MSI/L2A -type d -name "*.SAFE" -exec cp -r {} . \;
		#or mv ./**/*.SAFE .


if __name__ == '__main__':
	pass
	D = Downloader("../sample.yml","../../testS2download")
	D.search_odata()
	D.download()

