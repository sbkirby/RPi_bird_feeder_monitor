#!/bin/sh
ffmpeg -y -framerate 10 -i /var/www/html/media/images/im_%04d.jpg -c:v libx264 -pix_fmt yuv420p output.mp4
