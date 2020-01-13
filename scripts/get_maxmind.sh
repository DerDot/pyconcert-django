#!/bin/bash

wget -O db.tar.gz "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${MAXMIND_KEY}&suffix=tar.gz"
mkdir -p .tmp/
tar -C .tmp/ -zxvf db.tar.gz
mv .tmp/GeoLite2-City_*/GeoLite2-City.mmdb vendor/maxmind.mmdb
rm db.tar.gz
rm -r .tmp/