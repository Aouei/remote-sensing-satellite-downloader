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
    """
    Implementation of SatelliteAPI for the USGS Earth Explorer API.
    
    This class provides methods to search and download satellite imagery from the
    USGS Earth Explorer service using their Machine-to-Machine (M2M) API.
    
    Parameters
    ----------
    username : str
        Username for authentication with the USGS Earth Explorer API
    password : str
        API token for authentication (not the user's password)
        
    Attributes
    ----------
    API_URL : str
        Base URL for the USGS M2M API
    LOGIN_ENDPOINT : str
        Endpoint for authentication
    SEARCH_ENDPOINT : str
        Endpoint for searching scenes
    DOWNLOAD_REQUEST_ENDPOINT : str
        Endpoint for requesting download URLs
    DOWNLOAD_OPTIONS_ENDPOINT : str
        Endpoint for fetching download options
        
    Notes
    -----
    Authentication is performed using API tokens which must be generated
    through the USGS Earth Explorer portal. The password parameter should
    actually be the API token, not the user's password.
    
    See Also
    --------
    sat_download.api.base.SatelliteAPI : Base class defining the API interface
    sat_download.api.odata.ODataAPI : Implementation for Copernicus Data Space API
    """
    API_URL = "https://m2m.cr.usgs.gov/api/api/json/stable/"
    LOGIN_ENDPOINT = "login-token"
    SEARCH_ENDPOINT = "scene-search"
    DOWNLOAD_REQUEST_ENDPOINT = "download-request"
    DOWNLOAD_OPTIONS_ENDPOINT = 'download-options'


    def __init__(self, username, password):
        """
        Initialize USGS API client and authenticate with the service.
        
        Parameters
        ----------
        username : str
            Username for authentication with the USGS Earth Explorer API
        password : str
            API token for authentication (not the user's password)
        
        Notes
        -----
        Automatically calls the __login method to authenticate with USGS.
        """
        super().__init__(username, password)
        self.__login()

    def __login(self):
        """
        Authenticate with the USGS Earth Explorer API.
        
        Returns
        -------
        None
            Updates the self.api_key attribute on success
            
        Raises
        ------
        Exception
            If authentication fails
            
        Notes
        -----
        Private method that handles authentication and stores the token
        for use with subsequent API requests.
        """
        payload = {'username' : self.username, 'token' : self.password}
        payload = json.dumps(payload)

        response = requests.post(f'{self.API_URL}{self.LOGIN_ENDPOINT}', payload)
        response = json.loads(response.text)

        if response['errorCode'] is None:
            self.api_key = {'X-Auth-Token': response['data']}
        else:
            raise Exception(response['errorCode'])    

    def search(self, filters: SearchFilters) -> SearchResults:
        """
        Search for satellite imagery using specified filters.
        
        Parameters
        ----------
        filters : SearchFilters
            The search filters to apply to the search
            
        Returns
        -------
        SearchResults
            Dictionary mapping product IDs to SatelliteImage objects
            
        Raises
        ------
        Exception
            If the API request fails
            
        Notes
        -----
        Implementation of the abstract search method for the USGS Earth Explorer API.
        Additional filtering is performed client-side on the returned results.
        """
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
        """
        Prepare a USGS API query from search filters.
        
        Parameters
        ----------
        filters : SearchFilters
            The search filters to convert to USGS API query parameters
            
        Returns
        -------
        str
            JSON string containing USGS API query parameters
            
        Notes
        -----
        Private method that converts SearchFilters into the specific
        format required by the USGS Earth Explorer API.
        """
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
            lon, lat = filters.geometry.replace(')', '').split('(')[-1].split(' ')
            lon, lat = float(lon), float(lat)
            
            spatialFilter['filterType'] = 'mbr'
            spatialFilter['lowerLeft'] = {'latitude': lat, 'longitude': lon}
            spatialFilter['upperRight'] = {'latitude': lat, 'longitude': lon}

        if bool(spatialFilter):
            payload['sceneFilter']['spatialFilter'] = spatialFilter
        if bool(acquisitionFilter):
            payload['sceneFilter']['acquisitionFilter'] = acquisitionFilter

        return json.dumps(payload)
    
    def __request_download_metadata(self, dataset, scenes):
        """
        Request metadata needed for downloading images.
        
        Parameters
        ----------
        dataset : str
            The collection identifier for the search results
        scenes : dict
            Dictionary containing scene search results
            
        Returns
        -------
        dict
            Download metadata including download URLs
            
        Raises
        ------
        Exception
            If the metadata request fails
            
        Notes
        -----
        Private method that obtains download options and creates download
        requests to generate URLs for the identified scenes.
        """
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
        """
        Get available download options for a set of scenes.
        
        Parameters
        ----------
        dataset : str
            The collection identifier
        scenes : List[dict]
            List of scene metadata from search results
            
        Returns
        -------
        list
            List of download options for the requested scenes
            
        Raises
        ------
        Exception
            If the options request fails
            
        Notes
        -----
        Private method that queries available download formats and options
        for the identified scenes.
        """        
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
        """
        Extract download IDs from options for products that are available.
        
        Parameters
        ----------
        options : List[dict]
            List of download options from __get_downloads_options
            
        Returns
        -------
        List[dict]
            List of entity/product ID pairs for available downloads
            
        Notes
        -----
        Private method that filters for available bundle products and
        extracts their identifiers needed for download requests.
        """
        download_ids = []
        for product in options:
            if product['available'] == True and 'Bundle' in product['productName']:
                download_ids.append({'entityId' : product['entityId'], 'productId' : product['id']})

        return download_ids 
    
    def download(self, image_id : str, outname : str) -> str | None:
        """
        Download a satellite image by its ID (URL).
        
        Parameters
        ----------
        image_id : str
            The download URL for the image (not entity ID)
        outname : str
            The output filename where the image will be saved
            
        Returns
        -------
        None
            The file is saved to the specified location on success
            
        Notes
        -----
        Implementation of the abstract download method for USGS API.
        Uses tqdm to display a progress bar during download.
        Unlike other APIs, the image_id parameter is actually the download URL.
        """
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
            
                return outname
            else:
                raise Exception(f"Error en la descarga: {response.status_code}")
        except Exception as e:
            print(f"Failed to download from {image_id}. {e}.")