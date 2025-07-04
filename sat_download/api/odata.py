import requests
import os


from typing import List, OrderedDict
from tqdm import tqdm
from sat_download.api.base import SatelliteAPI
from sat_download.data_types.search import SearchFilters, SearchResults
from sat_download.factories.search import get_satellite_image
from sat_download.enums import COLLECTIONS


class ODataAPI(SatelliteAPI):
    """
    Implementation of SatelliteAPI for the Copernicus Data Space Ecosystem OData API.
    
    This class provides methods to search and download satellite imagery from the
    Copernicus Data Space Ecosystem using their OData API.
    
    Parameters
    ----------
    username : str
        Username for authentication with the Copernicus Data Space API
    password : str
        Password for authentication with the Copernicus Data Space API
        
    Attributes
    ----------
    SEARCH_URL : str
        Endpoint URL for searching satellite products
    DOWNLOAD_URL : str
        Endpoint URL for downloading satellite products
    TOKEN_URL : str
        Endpoint URL for obtaining authentication tokens
        
    Notes
    -----
    Authentication is performed using Keycloak OAuth2 tokens which are obtained
    as needed for download operations.
    
    See Also
    --------
    sat_download.api.base.SatelliteAPI : Base class defining the API interface
    sat_download.api.usgs.USGSAPI : Implementation for USGS Earth Explorer API
    """
    SEARCH_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
    DOWNLOAD_URL = "https://download.dataspace.copernicus.eu/odata/v1/Products"
    TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"


    def __init__(self, username : str, password : str) -> None:
        super().__init__(username, password)

    def __prepare_query(self, filters : SearchFilters) -> str:
        """
        Prepare an OData query from search filters.
        
        Parameters
        ----------
        filters : SearchFilters
            The search filters to convert to OData query parameters
            
        Returns
        -------
        dict
            Dictionary containing OData query parameters
            
        Notes
        -----
        Private method that converts SearchFilters into OData-compatible
        filter expressions for querying the Copernicus Data Space API.
        """
        params = []
        if filters.is_set('collection'):
            params.append(f"Collection/Name eq '{filters.collection}'")
        if filters.is_set('processing_level'):
            params.append(f"contains(Name,'{filters.processing_level}')")
        if filters.is_set('start_date'):
            params.append(f"ContentDate/Start gt {filters.start_date}T00:00:00.000Z")
        if filters.is_set('end_date'):
            params.append(f"ContentDate/End lt {filters.end_date}T23:59:59.000Z")
        if filters.is_set('geometry'):
            params.append(f"OData.CSC.Intersects(area=geography'SRID=4326;{filters.geometry}')")
        if filters.is_set('tile_id'):
            params.append(f"contains(Name,'{filters.tile_id}')")
        if filters.is_set('contains'):
            for item in filters.contains:
                params.append(f"contains(Name,'{item}')")
                
        return {"$filter": ' and '.join(params), "$orderby" : f"ContentDate/Start desc"}
    
    def __get_token(self) -> str:
        """
        Obtain an authentication token from the Copernicus Data Space API.
        
        Returns
        -------
        str
            The access token for API authentication
            
        Raises
        ------
        Exception
            If token creation fails
            
        Notes
        -----
        Private method that handles OAuth2 authentication with the Copernicus
        identity service.
        """
        data = {
            "client_id": "cdse-public",
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
        }
        
        try:
            query = requests.post(self.TOKEN_URL, data = data)
            query.raise_for_status()
        except Exception as _:
            raise Exception(f"Keycloak token creation failed. Reponse from the server was: {query.json()}")
        
        return query.json()["access_token"]
    
    def __prepare_search_results(self, collection : str, images : List[OrderedDict]) -> SearchResults:
        """
        Convert API response data to standardized search results.
        
        Parameters
        ----------
        collection : str
            The collection identifier for the search results
        images : List[OrderedDict]
            List of image metadata from API response
            
        Returns
        -------
        SearchResults
            Dictionary mapping product IDs to SatelliteImage objects
            
        Notes
        -----
        Private method that processes raw API response data into the
        standardized SearchResults format.
        """
        results : SearchResults = { image['Id'] : get_satellite_image(COLLECTIONS(collection), image) for image in images }

        return results

    def search(self, filters : SearchFilters) -> SearchResults:
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
        Implementation of the abstract search method for the Copernicus Data Space API.
        """
        query = self.__prepare_query(filters)

        response = requests.get(self.SEARCH_URL, params = query)
        if response.status_code == 200:
            return self.__prepare_search_results(filters.collection, response.json()['value'])
        else:
            raise Exception(f"Error en la solicitud: {response.status_code}")
    
    def download(self, image_id: str, outname: str, verbose : int) -> str | None:
        """
        Download a satellite image by its ID.

        Parameters
        ----------
        image_id : str
            The unique identifier of the image to download.
        outname : str
            The output filename where the image will be saved.
        verbose : int
            Verbosity level for logging the download process. 0 = silent, >0 = progress bar,
            
        Returns
        -------
        str | None
            The file path of the downloaded image if the download is successful.
            Returns None if the download fails.

        Raises
        ------
        Exception
            If the download fails due to an API error or network issue.

        Notes
        -----
        - This method implements the abstract `download` method for the Copernicus Data Space API.
        - It uses OAuth2 authentication to obtain a token before initiating the download.
        - A progress bar is displayed using `tqdm` to indicate the download progress.
        - The method writes the downloaded file in chunks to avoid memory issues with large files.
        - Exceptions are raised for HTTP errors or other failures during the download process.
        """
        MB = (1024 * 1024)

        keycloak_token = self.__get_token()
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {keycloak_token}'})

        url = f"{self.DOWNLOAD_URL}({image_id})/$value"
        response = session.get(url, stream = True, verify = True, allow_redirects = True)
    
        if response.status_code == 200:
            total_size = int(response.headers.get('Content-Length', 0)) // MB
            with open(outname, "wb") as file:
                if verbose == 0:
                    for chunk in response.iter_content(chunk_size = MB):
                        file.write(chunk)
                else:
                    for chunk in tqdm(response.iter_content(chunk_size = MB), total = total_size,
                                    unit = 'MB', desc = f"Downloading image at {os.path.basename(outname)}"):
                        file.write(chunk)

            return outname
        else:
            raise Exception(f"Error en la descarga: {response.status_code}")