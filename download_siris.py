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



# Fritidshem, grundskola...
for verksamhetsform in scraper.items:
    print(u"VERKSAMHETSFORM: {}".format(verksamhetsform.label))

    for dataset in verksamhetsform.items:
        print(dataset.id, dataset.label)
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
                                          dataset.id  + "-" + dataset.label,
                                          url_fmt)
                    if not os.path.exists(outdir):
                        os.makedirs(outdir)

                    filename = "{}-{}.{}".format(period, uttag_id, file_fmt)
                    filepath = os.path.join(outdir, filename)

                    with open(filepath, 'wb') as f:
                        f.write(r.content)

                    print(u"Storing {}".format(filepath))
