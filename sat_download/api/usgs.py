import requests
import json
import re
import os

from tqdm import tqdm
from typing import List
from sat_download.api.base import SatelliteAPI
from sat_download.data_types.search import SearchFilters, SearchResults
from sat_download.factories.search import get_satellite_image
from sat_download.enums import COLLECTIONS


class USGSAPI(SatelliteAPI):
    API_URL = "https://m2m.cr.usgs.gov/api/api/json/stable/"
    LOGIN_ENDPOINT = "login-token"
    SEARCH_ENDPOINT = "scene-search"
    DOWNLOAD_REQUEST_ENDPOINT = "download-request"
    DOWNLOAD_OPTIONS_ENDPOINT = 'download-options'


    def __init__(self, username, password):
        super().__init__(username, password)
        self.__login()

    def __login(self):

        payload = {'username' : self.username, 'token' : self.password}
        payload = json.dumps(payload)

        response = requests.post(f'{self.API_URL}{self.LOGIN_ENDPOINT}', payload)
        response = json.loads(response.text)

        if response['errorCode'] is None:
            self.api_key = {'X-Auth-Token': response['data']}
        else:
            raise Exception(response['errorCode'])    

    def search(self, filters: SearchFilters) -> SearchResults:
        query = self.__prepare_query(filters)
        
        response = requests.post(f"{self.API_URL}{self.SEARCH_ENDPOINT}", query, headers=self.api_key)
        response = json.loads(response.text)

        if response["errorCode"] is None and bool(response["data"]["results"]):
            scenes = response["data"]
            metadata = self.__request_download_metadata(filters.collection, scenes)

            results = {}

            for scene in scenes["results"]:
                if filters.is_set('processing_level') and (not filters.processing_level in scene["displayId"]):
                    continue

                if filters.is_set('tile_id') and (not f'_{filters.tile_id}_' in scene['displayId']):
                    continue

                image_id = scene["entityId"]

                url = next(
                    (met["url"] for met in metadata["availableDownloads"] if met["entityId"] == image_id),
                    None
                )

                if url:
                    results[url] = get_satellite_image(COLLECTIONS(filters.collection), {'Name' : scene["displayId"]})

            return results

        else:
            raise Exception(response["errorCode"])

    def __prepare_query(self, filters : SearchFilters) -> str:
        payload = {'maxResults' : 20, 'startingNumber' : 1, 'sceneFilter' : {}}
        acquisitionFilter = {}
        spatialFilter = {}

        if filters.is_set('collection'):
            payload['datasetName'] =  filters.collection
        if filters.is_set('start_date'):
            acquisitionFilter['start'] = filters.start_date
        if filters.is_set('end_date'):
            acquisitionFilter['end'] = filters.end_date
        if filters.is_set('geometry'):
            lat, lon = filters.geometry.replace(')', '').split('(')[-1].split(' ')
            lat, lon = float(lat), float(lon)
            
            spatialFilter['filterType'] = 'mbr'
            spatialFilter['lowerLeft'] = {'latitude': lat, 'longitude': lon}
            spatialFilter['upperRight'] = {'latitude': lat, 'longitude': lon}

        if bool(spatialFilter):
            payload['sceneFilter']['spatialFilter'] = spatialFilter
        if bool(acquisitionFilter):
            payload['sceneFilter']['acquisitionFilter'] = acquisitionFilter

        return json.dumps(payload)
    
    def __request_download_metadata(self, dataset, scenes):
        options = self.__get_downloads_options(dataset, scenes)
        download_ids = self.__get_download_ids(options)

        payload = {'downloads' : download_ids, 'label' : 'sample'}
        payload = json.dumps(payload)
        response = requests.post(f'{self.API_URL}{self.DOWNLOAD_REQUEST_ENDPOINT}', payload, headers = self.api_key)
        response = json.loads(response.text)

        if response['errorCode'] is None:
            return response['data']
        else:
            raise Exception(response['errorCode'])
        
    def __get_downloads_options(self, dataset : str, scenes : List[dict]):        
        scene_ids = [result['entityId'] for result in scenes['results']]
        payload = {'datasetName' : dataset, 'entityIds' : scene_ids}
        payload = json.dumps(payload)

        response = requests.post(f'{self.API_URL}{self.DOWNLOAD_OPTIONS_ENDPOINT}', payload, headers = self.api_key)
        response = json.loads(response.text)
    
        if response['errorCode'] is None:
            return response['data']
        else:
            raise Exception(response['errorCode'])
        
    def __get_download_ids(self, options : List[dict]) -> List[dict]:
        download_ids = []
        for product in options:
            if product['available'] == True and 'Bundle' in product['productName']:
                download_ids.append({'entityId' : product['entityId'], 'productId' : product['id']})

        return download_ids 
    
    def download(self, image_id : str, outname : str) -> None:
        MB = (1024 * 1024)

        try:        
            response = requests.get(image_id, stream=True)

            if response.status_code == 200:
                disposition = response.headers['content-disposition']

                total_size = int(response.headers.get('Content-Length', 0)) // MB

                filename = re.findall("filename=(.+)", disposition)[0].strip("\"")
                with open(outname, 'wb') as new_file:
                    for chunk in tqdm(response.iter_content(chunk_size = MB), total = total_size,
                                        unit = 'MB', desc = f"Downloading image at {os.path.basename(outname)}"):
                        new_file.write(chunk)
            else:
                raise Exception(f"Error en la descarga: {response.status_code}")
        except Exception as e:
            print(f"Failed to download from {image_id}. {e}.")