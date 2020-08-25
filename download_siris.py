#!/usr/bin/env python2
# encoding: utf-8
"""Downloads all datasets from Siris locally.
"""
import os
import requests
import requests_cache
from siris.scraper import SirisScraper
from settings import DATA_DIR, FORMATS
requests_cache.install_cache('demo_cache')

DOWNLOAD_DIR = os.path.join(DATA_DIR, "siris")

# Init scraper
scraper = SirisScraper()

DOWNLOADED_DATASETS = []
for subdir, dirs, files in os.walk(DATA_DIR):
    for file in files:
        file_path = os.path.join(subdir, file)
        try:
            _, db, skolniva, dataset, fmt, filename = file_path.split("/")
            dataset_id, _ = dataset.split("-")
            DOWNLOADED_DATASETS.append(dataset_id)
        except Exception:
            continue

# Fritidshem, grundskola...
for verksamhetsform in scraper.items:
    print(u"VERKSAMHETSFORM: {}".format(verksamhetsform.label))

    for dataset in verksamhetsform.items:
        #if dataset.id in DOWNLOADED_DATASETS:
        #    print(u"Already downloaded {} ({})".format(dataset.label, dataset.id))
        #    continue

        for period, _ in dataset.periods:
            print(u"- " + period)
            uttag = dataset.get_uttag(period)
            if len(uttag) == 0:
                uttag = [("1", None)]

            for uttag_id, _ in uttag:
                base_url = dataset.get_xml_url(period, uttag_id)
                for url_fmt, file_fmt in FORMATS:
                    file_url = base_url.replace("XML", url_fmt)
                    print(u"Downloading {}".format(file_url))

                    r = requests.get(file_url)

                    outdir = os.path.join(DOWNLOAD_DIR,
                                          verksamhetsform.label,
                                          dataset.id + "-" + dataset.label.replace("/"," och "),
                                          url_fmt)
                    if not os.path.exists(outdir):
                        os.makedirs(outdir)

                    filename = "{}-{}.{}".format(period, uttag_id, file_fmt)
                    filepath = os.path.join(outdir, filename)

                    with open(filepath, 'wb') as f:
                        f.write(r.content)

                    print(u"Storing {}".format(filepath))
