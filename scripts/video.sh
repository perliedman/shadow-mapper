#!/bin/sh
avconv -f image2 -i img%03d.png -vcodec libx264 -mbd rd -flags +mv4+aic -trellis 2 -cmp 2 -subcmp 2 -g 300 -pass 1 a.mp4
