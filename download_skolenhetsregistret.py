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
    "20200101",
    "20190701",
    "20190101",
    "20180701",
    "20180101",
    "20170701",
    "20170101",
    "20160701",
    "20160101",
    "20150701",
    "20150101",
    "20140701",
    "20140101",
    "20130701",
    "20130101",
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
session = boto3.Session()
s3_client = session.client("s3")
for school in d["Skolenheter"]:
    id_ = school['Skolenhetskod']
    for date in DATES:
        endpoint = f"{BASE}/{id_}/{date}"
        d = requests.get(endpoint).json()
        with NamedTemporaryFile(mode='wt') as tmp:
            tmp.write(json.dumps(d))
            s3_client.upload_file(
                tmp.name,
                S3_BUCKET,
                f"skolenhet/{id_}/{date}.json",
                ExtraArgs={'ACL': "public-read", 'CacheControl': "no-cache"},
            )
