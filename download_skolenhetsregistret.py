#!/usr/bin/env python3
"""Fetch all school data from Skolenhetsregistret, at various dates.
"""
import requests
from csv import DictWriter
from tempfile import NamedTemporaryFile
from settings import DATA_DIR, S3_BUCKET
import boto3
import json


BASE = "https://api.scb.se/UF0109/v2/skolenhetsregister/sv/skolenhet"
DATES = [
    "20200701", "20200401", "20200101",
    "20191001", "20190701", "20190401", "20190101",
    "20181001", "20180701", "20180401", "20180101",
    "20171001", "20170701", "20170401", "20170101",
    "20161001", "20160701", "20160401", "20160101",
    "20151001", "20150701", "20150401", "20150101",
    "20141001", "20140701", "20140401", "20140101",
    "20131001", "20130701", "20130401", "20130101",
]
# fetch list of schools
d = requests.get(BASE).json()
print(f"Got {len(d['Skolenheter'])} schools")
print(d["Fotnot"])

with open(f"{DATA_DIR}/skolenheter.csv", "w") as file_:
    writer = DictWriter(file_, fieldnames=[
        "Skolenhetskod",
        "Skolenhetsnamn",
        "Kommunkod",
        "PeOrgNr"
    ])
    writer.writeheader()
    writer.writerows(d["Skolenheter"])

# Fetch data for each school, at numerous times
session = boto3.Session()  # profile_name="XXX"
s3_client = session.client("s3")
for school in d["Skolenheter"]:
    id_ = school['Skolenhetskod']
    print(f"Downloading {school['Skolenhetsnamn']} ({id_})")
    for date in DATES:
        endpoint = f"{BASE}/{id_}/{date}"
        d = requests.get(endpoint).json()
        with NamedTemporaryFile(mode='wt') as tmp:
            tmp.write(json.dumps(d))
            tmp.seek(0)
            s3_client.upload_file(
                tmp.name,
                S3_BUCKET,
                f"skolenhet/{id_}/{date}.json",
                ExtraArgs={'ACL': "public-read", 'CacheControl': "no-cache"},
            )
