# Shadow Mapper

This project produces so called shadow maps, showing which parts of a geographic area that are lit by the sun and which are in shade, using open elevation data and buildings from OpenStreetMap.

[This video of shadow mapper](https://vimeo.com/98524944) shows what this project is about.

Find more information about why this project exists and how it works in my [blog post about shadow mapper](http://www.liedman.net/2014/06/25/sunshine/).

## Installing

You need Python installed, I've used Python 2.7, but you might have success with other versions as well.

I recommend using [virtualenv](http://virtualenv.readthedocs.org/en/latest/), although it isn't strictly necessary.

After unpacking/cloning the source, go ahead and create a new virtualenv:

```sh
cd shadow-mapper
virtualenv venv
source venv/bin/activate
```

Then install the requirements with pip:

```sh
pip install -r /path/to/requirements.txt
```

## Running

A very short introduction to the tools this package gives you.

### heightmap.py

This script can be used for rendering height maps, both as images as well as [pickle](https://docs.python.org/2/library/pickle.html)d objects that can be used with the other tools in this package.

Before running you need:

* Elevation data from [Virtual Terrain Project](http://vterrain.org/Elevation/global.html), unzipped as .hgt files
* Building data from [OpenStreetMap](http://openstreetmap.org/) in GeoJSON format. It can for example be obtained using [overpass turbo](http://overpass-turbo.eu/); you can for example use my tool [query-overpass](https://www.npmjs.org/package/query-overpass) to do this
* Latitude and longitude for the center of the map you want to render
* The resolution you want to use, in meters per pixel; 4 to 8 meters per pixel might be a good start.
* The size of the map to render, in pixels

Example usage:

```sh
python heightmap.py --projection epsg:3006 --elevation-dir data/ --geojson my_buildings.geojson --output my.heightmap --save-image my.png 57.7 11.96 8 512
```

If you don't know which elevation tile you need, you will get an error about missing tile with name x when you run heightmap.py with your parameters.

Also try

```sh
python heightmap.py -h
```

for help on parameters.

### render.py

Render a set of shadow maps from a previously generated height map.

```sh
python render.py my.heightmap "2014-06-25 00:00" "2014-06-26 00:00" 60 rendered
```

Input is the name of the height map file, two dates and times in UTC to render images between, as well as the number of minutes to step between each image. Finally, the path to store the rendered images in.

Optionally, you can provide a background image; the shadowmap will be overlayed with the provided opacity:

```sh
python render.py my.heightmap "2014-06-25 00:00" "2014-06-26 00:00" 60 rendered my_background.png 0.4
```
