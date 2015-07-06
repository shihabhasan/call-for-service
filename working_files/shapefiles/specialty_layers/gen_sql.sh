#!/bin/bash

echo "Creating SQL from shapefiles..."
echo "Run the first created SQL script first, since it will create the"
echo "table, and the rest will just append to it."
first=true
mode="c"

while [ "$1" != "" ]; do
    echo "Processing $1"
    if [ -f $1 ]; then
        filename=$(basename "$1")
        filename="${filename%.*}"
        shp2pgsql -$mode -s 2264:4326 $filename "public.""specialty_layers" > "$filename"".sql"
        echo "Processed $1"
    else
        echo "Unable to find file $1; skipping"
    fi

    if [ "$first" = true ]; then
        first=false
        mode="a"
    fi

    shift
done
