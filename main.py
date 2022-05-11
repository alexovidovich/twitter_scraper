from worker import twitter
import csv
import time
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename",
                    help="what file to write", )
parser.add_argument("-s", "--search",
                    dest="search_word", default=True,
                    help="what word to search")
parser.add_argument("-d", "--days",
                    dest="days", default=True,
                    help="for how many days per operation")

args = parser.parse_args()
if args.search_word and args.filename and args.days.isdigit() :
    twitter.delay(args.search_word , args.filename, int(args.days))
else:
    print("use -f 'file to save' -s 'what to search' -d 'for how many days per operation' " )

# with open("countries.csv", "r") as f:
#     companies = csv.DictReader(f)

#     for company in companies:
#         twitter.delay("$" + company.get("ticker"), company.get("ticker"), 3)
#         twitter.delay(company.get("name"), company.get("name"), 3)
#         time.sleep(20)
