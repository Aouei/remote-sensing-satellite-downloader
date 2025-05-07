from enum import Enum



class COLLECTIONS(Enum):
    """Class to define sensor types to work with"""
    
    SENTINEL_2 : str = 'SENTINEL-2'
    SENTINEL_3 : str = 'SENTINEL-3'
    LANDSAT_8 : str = 'landsat_ot_c2_l1'