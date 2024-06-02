#!/bin/bash

echo "graphcast pod start script running..."

python -m graphcast_sdk.cast.cast

while true; do
	echo "finished, $(date)"
	sleep 30
done
