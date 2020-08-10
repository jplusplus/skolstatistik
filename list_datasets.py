# encoding: utf-8
"""Create a list/table of all downloaded datasets.
"""

import os
from collections import OrderedDict
import csv
from urllib.parse import quote
from settings import DATA_DIR, FORMATS, S3_URL

all_files = []

for subdir, dirs, files in os.walk(DATA_DIR):
    for file in files:
        file_path = os.path.join(subdir, file)
        try:
            _, db, skolniva, dataset, fmt, filename = file_path.split("/")
        except:
            continue

        year, uttag = filename.split(".")[0].split("-")

        #print(file_path)
        url = S3_URL + file_path.replace(DATA_DIR, "")
        all_files.append(OrderedDict([
            ("databas", db),
            ("skolnivå", skolniva),
            ("dataset", dataset),
            ("år", year),
            ("uttag", uttag),
            ("format", fmt),
            ("url", url),
        ]
        ))

with open('datasets.csv', 'w') as outfile:
    fp = csv.DictWriter(outfile, all_files[0].keys())
    fp.writeheader()
    fp.writerows(all_files)


#import tabulate
#
#header = all_files[0].keys()
#rows =  [x.values() for x in all_files]
#with open('datasets.md', 'w') as f:
#    f.write("# Alla dataset\n")

#    tbl_str = tabulate.tabulate(rows, header)
#    f.write(tbl_str)
