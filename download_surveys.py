#!/usr/bin/env python3
"""Fetch all Skolinspektionen surveys from the Skolverket API
"""
import requests
from tempfile import NamedTemporaryFile
from settings import S3_BUCKET
import boto3
import json


BASE = "https://api.skolverket.se/planned-educations/"

next_page = BASE + "school-units?size=100"
codes = []

session = boto3.Session(profile_name="jplusplus")  # profile_name="XXX"
s3_client = session.client("s3")

while next_page:
    print("fetching school units from ", next_page)
    r = requests.get(next_page)
    assert r.status_code == 200
    data = r.json()
    if (data["_embedded"]["listedSchoolUnits"]):
        codes += [s["code"]
                  for s in data["_embedded"]["listedSchoolUnits"]]
    if "next" in data["_links"]:
        next_page = data["_links"]["next"]["href"]
    else:
        next_page = None

for c in codes:
    print(f"Fetching surveys for school unit {c}")
    r = requests.get(BASE + f"school-units/{c}/surveys")
    data = r.json()
    assert r.status_code == 200
    data = r.json()
    for group in data["_links"].keys():
        if group == "self":
            continue

        href = data["_links"][group]["href"]
        r = requests.get(href)
        assert r.status_code == 200
        d = r.json()

        with NamedTemporaryFile(mode='wt') as tmp:
            tmp.write(json.dumps(d))
            tmp.seek(0)
            s3_client.upload_file(
                tmp.name,
                S3_BUCKET,
                f"survey/{c}/{group}.json",
                ExtraArgs={
                    'ACL': "public-read",
                    'CacheControl': "no-cache"
                },
            )
