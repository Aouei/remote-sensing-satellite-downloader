from sat_download.api.base import SatelliteAPI
from sat_download.data_types.search import SearchFilters, SearchResults


class SatelliteImageDownloader:
    def __init__(self, api : SatelliteAPI) -> None:
        self.api = api

    def bulk_search(self, filters: SearchFilters) -> SearchResults:
        try:
            return self.api.bulk_search(filters)        
        except Exception as exc:
            print(exc)

    def search(self, filters : SearchFilters) -> SearchResults:
        try:
            return self.api.search(filters)        
        except Exception as exc:
            print(exc)

    def download(self, image_id : str, outname : str) -> None:
        try:
            return self.api.download(image_id, outname)
        except Exception as exc:
            print(exc)