import os

from sat_download.api.base import SatelliteAPI
from sat_download.data_types.search import SearchFilters, SearchResults


class SatelliteImageDownloader:
    """
    A class to handle satellite image searching and downloading operations.
    
    This class provides a simplified interface to search for satellite images
    using various filters and download them.
    
    Parameters
    ----------
    api : SatelliteAPI
        The satellite API client to use for API operations
        
    See Also
    --------
    sat_download.api.base.SatelliteAPI : Base class for satellite API clients
    sat_download.api.odata.ODataAPI : Implementation for Copernicus Data Space API
    sat_download.api.usgs.USGSAPI : Implementation for USGS Earth Explorer API
    """
    def __init__(self, api : SatelliteAPI) -> None:
        self.api = api

    def bulk_search(self, filters: SearchFilters) -> SearchResults:
        """
        Perform a bulk search operation using specified filters.
        
        Parameters
        ----------
        filters : SearchFilters
            The search filters to apply to the bulk search
            
        Returns
        -------
        SearchResults
            The results from the bulk search operation
            
        Notes
        -----
        Exceptions are caught and printed to console.
        """
        try:
            return self.api.bulk_search(filters)        
        except Exception as exc:
            print(exc)

    def bulk_download(self, images : SearchResults, outdir : str) -> None:
        """
        Download multiple satellite images in bulk.
        
        Parameters
        ----------
        images : SearchResults
            The search results containing image IDs to download
        outdir : str
            The output directory where the images will be saved
            
        Returns
        -------
        None
            The files are saved to the specified location on success
            
        Notes
        -----
        Exceptions are caught and printed to console.
        """
        try:
            os.makedirs(outdir, exist_ok=True)

            for download_id, image in images.items():
                self.api.download(download_id, os.path.join(outdir, image.filename))

        except Exception as exc:
            print(exc)


    def search(self, filters : SearchFilters) -> SearchResults:
        """
        Perform a standard search operation using specified filters.
        
        Parameters
        ----------
        filters : SearchFilters
            The search filters to apply to the search
            
        Returns
        -------
        SearchResults
            The results from the search operation
            
        Notes
        -----
        Exceptions are caught and printed to console.
        """
        try:
            return self.api.search(filters)        
        except Exception as exc:
            print(exc)

    def download(self, image_id : str, out_dir : str, outname : str) -> None:
        """
        Download a satellite image by its ID.
        
        Parameters
        ----------
        image_id : str
            The unique identifier of the image to download
        outdir : str
            The output directory where the image will be saved
        outname : str
            The output filename where the image will be saved
            
        Returns
        -------
        None
            The file is saved to the specified location on success
            
        Notes
        -----
        Exceptions are caught and printed to console.
        """
        try:
            os.makedirs(out_dir, exist_ok=True)
            return self.api.download(image_id, os.path.join(out_dir, outname))
        except Exception as exc:
            print(exc)