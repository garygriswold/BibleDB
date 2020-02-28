#!/bin/sh -ve

# Download dbp-prod bucket list
time python3 py/ListBucket.py dbp-prod

# Download dbp-vid bucket list
time python3 py/ListBucket.py dbp-vid

# Download info.json files
time python3 py/DownloadInfo.py
