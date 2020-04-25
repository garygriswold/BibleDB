#!/bin/sh -ve

# Download dbp-prod bucket list
time python3 py/ListBucket.py dev dbp-prod

# Download dbp-vid bucket list
time python3 py/ListBucket.py dev dbp-vid

# Download shortsands bucket list
time python3 py/ListBucket.py dev text-us-east-1-shortsands

# Download FCBH info.json files
time python3 py/DownloadInfo.py dev dbp-prod

# Download shortsands json.info files
time python3 py/DownloadInfo.py dev text-us-east-1-shortsands

# Run dbp etl Validate.py
# cd $HOME/FCBH/dbp-etl
# python3 load/Validate.py test bucketlists


