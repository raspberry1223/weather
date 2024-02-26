import warnings
from dataclasses import dataclass

import geopandas as gpd
import numpy as np
import openmeteo_requests
import pandas as pd
import rasterio
import requests_cache
from rasterio.features import rasterize
from rasterio.transform import from_origin
from retry_requests import retry

warnings.filterwarnings("ignore", category=UserWarning)


class Entity:
    def __init__(self, id: str):
        self.id = id


@dataclass
class AOIComponent:
    shapefile_path: str
    centroid: tuple = None


@dataclass
class WeatherDataComponent:
    latitude: float = None
    longitude: float = None
    start_date: str = None
    end_date: str = None
    data: pd.DataFrame = None


@dataclass
class RasterComponent:
    data: dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}  # Initialize as an empty dictionary


class AOISystem:
    @staticmethod
    def calculate_centroid(aoi_component: AOIComponent) -> None:
        aoi_data = gpd.read_file(aoi_component.shapefile_path)
        if aoi_data.crs.is_geographic:
            projected = aoi_data.to_crs(epsg=3395)
            centroid = projected.centroid.iloc[0]
            centroid_gs = gpd.GeoSeries([centroid], crs=projected.crs)
            centroid_gs = centroid_gs.to_crs(epsg=4326)
            centroid = centroid_gs.iloc[0]
        else:
            centroid = aoi_data.centroid.iloc[0]
        aoi_component.centroid = (centroid.y, centroid.x)


class WeatherDataSystem:
    @staticmethod
    def fetch_data(weather_data_component: WeatherDataComponent) -> None:
        cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": weather_data_component.latitude,
            "longitude": weather_data_component.longitude,
            "start_date": weather_data_component.start_date,
            "end_date": weather_data_component.end_date,
            "daily": "precipitation_sum",
        }
        responses = openmeteo.weather_api(url, params=params)

        # Assuming the responses are list of daily precipitation values
        weather_data_component.data = responses[0].Daily().Variables(0).ValuesAsNumpy()


class RasterSystem:
    @staticmethod
    def create_rasters(
        aoi_component: AOIComponent,
        weather_data_component: WeatherDataComponent,
        raster_component: RasterComponent,
        precipitation_threshold: float = 1.0,
    ) -> None:
        aoi = gpd.read_file(aoi_component.shapefile_path)
        bounds = aoi.bounds.iloc[0]
        res = 0.01
        transform = from_origin(bounds.minx, bounds.maxy, res, res)

        # precipitation data to calculate monthly rainy days
        daily_data = {
            "date": pd.date_range(
                start=pd.to_datetime(weather_data_component.start_date),
                end=pd.to_datetime(weather_data_component.end_date),
                freq="D",
            ),
            "precipitation": weather_data_component.data,
        }
        df = pd.DataFrame(data=daily_data)
        df["is_rainy"] = df["precipitation"] > precipitation_threshold
        monthly_rainy_days = df.groupby(df["date"].dt.month).is_rainy.sum()

        # Create rasters for each month
        for month, rainy_days in monthly_rainy_days.items():
            width = int((bounds.maxx - bounds.minx) / res)
            height = int((bounds.maxy - bounds.miny) / res)
            raster = np.full((height, width), fill_value=rainy_days, dtype=np.float32)

            shapes = ((geom, 1) for geom in aoi.geometry)
            mask = rasterize(shapes=shapes, out_shape=raster.shape, transform=transform)
            raster[mask == 0] = np.nan

            with rasterio.open(
                f"rainy_days_{month}.tif",
                "w",
                driver="GTiff",
                height=raster.shape[0],
                width=raster.shape[1],
                count=1,
                dtype=raster.dtype,
                crs=aoi.crs,
                transform=transform,
            ) as dst:
                dst.write(raster, 1)
            raster_component.data[month] = f"rainy_days_{month}.tif"


if __name__ == "__main__":
    aoi_entity = Entity("aoi")
    aoi_component = AOIComponent("data/aoi.shp")
    AOISystem.calculate_centroid(aoi_component)

    weather_entity = Entity("weather_data")
    weather_data_component = WeatherDataComponent(
        aoi_component.centroid[0], aoi_component.centroid[1], "2020-01-01", "2021-12-31"
    )
    WeatherDataSystem.fetch_data(weather_data_component)

    raster_entity = Entity("raster_data")
    raster_component = RasterComponent()
    RasterSystem.create_rasters(aoi_component, weather_data_component, raster_component)
    print("Raster Files: ", raster_component.data)
