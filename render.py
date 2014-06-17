#!/usr/bin/python

from sys import argv
from datetime import datetime, timedelta
from heightmap import HeightMap
from suncalc import solar_position
from sunmap import SunMap, get_projection_north_deviation
from math import sin, cos
from os import path
from PIL import Image, ImageChops

with open(argv[1], 'rb') as f:
    hm = HeightMap.load(f)

t1 = datetime.strptime(argv[2], '%Y-%m-%d %H:%M')
t2 = datetime.strptime(argv[3], '%Y-%m-%d %H:%M')
delta = timedelta(minutes=int(argv[4]))

bkg = None
if len(argv) > 6:
    bkg = Image.open(argv[6]).convert('RGB')
    transparency = int(255 - float(argv[7]) * 255)

t = t1
while t <= t2:
    print t.strftime('%Y-%m-%d_%H%M.png'), '...'
    sunpos = solar_position(t, hm.lat, hm.lng)
    dev = get_projection_north_deviation(hm.proj, hm.lat, hm.lng)
    sun_x = -sin(sunpos['azimuth'] - dev) * cos(sunpos['altitude'])
    sun_y = -cos(sunpos['azimuth'] - dev) * cos(sunpos['altitude'])
    sun_z = sin(sunpos['altitude'])

    sm = SunMap(hm.lat, hm.lng, hm.resolution, hm.size, hm.proj, sun_x, sun_y, sun_z, hm, 1.5)
    img = sm.to_image()

    if bkg:
        img = img.convert('RGB')
        img = Image.eval(img, lambda x: x + transparency)
        img = ImageChops.multiply(img, bkg)

    img.save(path.join(argv[5], t.strftime('%Y-%m-%d_%H%M.png')))

    t += delta
    print
