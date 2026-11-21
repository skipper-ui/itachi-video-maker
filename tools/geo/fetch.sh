#!/usr/bin/env bash
# Download Natural Earth source data (public domain) into tools/geo/data/.
# Countries use the India point-of-view file so India's boundary matches the official map.
set -euo pipefail
cd "$(dirname "$0")" && mkdir -p data
B=https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson
curl -sSfL -o data/countries-ind-10m.geojson "$B/ne_10m_admin_0_countries_ind.geojson"
curl -sSfL -o data/states-50m.geojson "$B/ne_50m_admin_1_states_provinces.geojson"
# Shaded relief (grayscale hillshade, 1:50m, 10800x5400) for the optional "relief" map look.
if [ ! -f data/SR_50M.tif ]; then
  curl -sSfL -o data/SR_50M.zip https://naciscdn.org/naturalearth/50m/raster/SR_50M.zip
  (cd data && unzip -oq SR_50M.zip && rm SR_50M.zip)
fi
ls -la data
