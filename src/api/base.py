from abc import ABC, abstractmethod
from data_types.search import SearchFilters, SearchResults
from datetime import datetime


class SatelliteAPI(ABC):
    def __init__(self, username : str, password : str) -> None:
        self.username = username
        self.password = password

    def bulk_search(self, filters : SearchFilters) -> SearchResults:
        start = datetime.strptime(filters.start_date, '%Y-%m-%d')
        end = datetime.strptime(filters.end_date, '%Y-%m-%d')

        results : SearchResults = {}
        while abs(start - end).days > 2:
            products : SearchResults = self.search(filters)
            for product in products.values():
                date = datetime.strptime(product.date, '%Y%m%d')
                if date < end:
                    end = date
            results.update(products)

            filters.end_date = date.strftime('%Y-%m-%d')
        
        return results

    @abstractmethod
    def search(self, filters : SearchFilters) -> SearchResults:
        pass

    @abstractmethod
    def download(self, image_id: str, outname : str):
        pass