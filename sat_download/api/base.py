from abc import ABC, abstractmethod
from sat_download.data_types.search import SearchFilters, SearchResults
from datetime import datetime


class SatelliteAPI(ABC):
    """
    Abstract base class for satellite data API clients.
    
    This class defines the common interface for interacting with different 
    satellite data provider APIs, such as Copernicus Data Space and USGS.
    
    Parameters
    ----------
    username : str
        Username or API key for authentication with the satellite data provider
    password : str
        Password or secret for authentication with the satellite data provider
        
    Notes
    -----
    Concrete implementations should handle the specific authentication mechanisms
    and API endpoints required by each satellite data provider.
    
    See Also
    --------
    sat_download.api.odata.ODataAPI : Implementation for Copernicus Data Space API
    sat_download.api.usgs.USGSAPI : Implementation for USGS Earth Explorer API
    """
    def __init__(self, username : str, password : str) -> None:
        self.username = username
        self.password = password

    def bulk_search(self, filters : SearchFilters) -> SearchResults:
        """
        Perform an iterative search over a date range by breaking it into smaller queries.
        
        This method handles large time-range searches by iteratively searching smaller
        time periods and combining the results.
        
        Parameters
        ----------
        filters : SearchFilters
            The search filters to apply, including date range
            
        Returns
        -------
        SearchResults
            Combined dictionary of search results from all iterations
            
        Notes
        -----
        This implementation progressively narrows the search window by updating
        the end_date of the filters based on the most recent image found.
        """
        start = datetime.strptime(filters.start_date, '%Y-%m-%d')
        end = datetime.strptime(filters.end_date, '%Y-%m-%d')
        last_date = start

        results : SearchResults = {}
        while abs(start - end).days > 2 and last_date.strftime('%Y-%m-%d') != end.strftime('%Y-%m-%d'):
            products : SearchResults = self.search(filters)
            for product in products.values():
                date = datetime.strptime(product.date, '%Y%m%d')
                if date < end:
                    end = date
            results.update(products)

            last_date = end
            filters.end_date = last_date.strftime('%Y-%m-%d')
        
        return results

    @abstractmethod
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
            Dictionary mapping product ID to SatelliteImage objects
            
        Notes
        -----
        This is an abstract method that concrete implementations must override.
        """
        pass

    @abstractmethod
    def download(self, image_id: str, outname: str) -> str | None:
        """
        Download a satellite image by its ID.

        Parameters
        ----------
        image_id : str
            The unique identifier of the image to download.
        outname : str
            The output filename where the image will be saved.

        Returns
        -------
        str | None
            The file path of the downloaded image if the download is successful.
            Returns None if the download fails.

        Notes
        -----
        - This is an abstract method that concrete implementations must override.
        - Implementations should handle any necessary authentication and API-specific
          download logic.
        - Exceptions should be handled appropriately to ensure the application remains stable.
        """
        pass