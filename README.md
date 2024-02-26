## Weather Data System
It consists of three main components:

* Entities: Represent unique aspects like AOI, weather data, and raster data. Entities in this system are simple identifiers.
* Components: Hold specific data related to each entity. These include the path to the AOI shapefile, weather data parameters, and raster data.
* Systems: Contain the logic to operate on the components. The systems perform tasks such as calculating the centroid of the AOI, fetching weather data, and creating raster files for each month.

* Example usage is included in the weather.py main file
  ```python
    aoi_entity = Entity("aoi")
    # Provide the file path to the aoi data
    aoi_component = AOIComponent('data/aoi.shp')
    AOISystem.calculate_centroid(aoi_component)

    weather_entity = Entity("weather_data")
    # Add the desired timespan
    weather_data_component = WeatherDataComponent(aoi_component.centroid[0], aoi_component.centroid[1], "2020-01-01",
                                                  "2021-12-31")
    WeatherDataSystem.fetch_data(weather_data_component)

    raster_entity = Entity("raster_data")
    raster_component = RasterComponent()
    RasterSystem.create_rasters(aoi_component, weather_data_component, raster_component)
    # Raster files will be created
    print("Raster Files: ", raster_component.data)
```
  
## Reading Raster Files
The CLI tool for reading and plotting raster files allows users to visualize the raster data interactively. It takes the path to a TIFF file as input and optionally accepts parameters for the plot title, colormap, and colorbar label.

* To visualie a raster file:
  ```bash
python raster_plotter.py /path/to/raster.tif --title "My Raster Plot" --cmap "plasma" --colorbar_label "Precipitation"

```
