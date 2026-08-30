import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_data_dir = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
CSV_PATH = os.path.join(_data_dir, "prix_quotidien.csv")
CSV_REGIONS_PATH = os.path.join(_data_dir, "prix_quotidien_regions.csv")
STATIONS_DB_PATH = os.path.join(_data_dir, "stations.db")
