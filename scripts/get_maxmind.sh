#!/bin/bash

wget -O db.tar.gz https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
tar -C /tmp -zxvf db.tar.gz
mv /tmp/GeoLite2-City_*/GeoLite2-City.mmdb vendor/maxmind.mmdb
rm db.tar.gz
rm -r /tmp/GeoLite2-City_*