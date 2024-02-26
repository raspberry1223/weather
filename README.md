## Weather Data System
It consists of several main components:

* open-meteo API: https://open-meteo.com/en/docs/
* Entities: Represent unique aspects like AOI, weather data, and raster data. Entities in this system are simple identifiers.
* Components: Hold specific data related to each entity. These include the path to the AOI shapefile, weather data parameters, and raster data.
* Systems: Contain the logic to operate on the components. The systems perform tasks such as calculating the centroid of the AOI, fetching weather data, and creating raster files for each month.

* Usage
 ```bash
  # first Install the packages by running
  pip install -r requirements.txt
  # run the weather.py app via python
  python weather.py
  # the timespan can be set manually in the weather.py main function
  ```
  
## Reading Raster Files
To visualize a raster file:

```bash
python raster_plotter.py /path/to/raster.tif --title "My Raster Plot" --cmap "plasma" --colorbar_label "Precipitation"

```
