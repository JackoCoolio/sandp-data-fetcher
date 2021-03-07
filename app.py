import time
import requests
import bs4
import os
from bs4 import element
from bs4.element import Tag
import csv
from progress.bar import Bar
import yaml

# load the YAML config
CONFIG = yaml.safe_load(open("./config.yaml"))

WIKIPEDIA_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def get_list_of_companies(limit=500):
    '''
    Scrapes Wikipedia's "List of S&P 500 companies" page for a list of companies and general information about them.

    Args:
        limit: the number of companies to include in the list (defaults to 500)

    Returns:
        A list of tuples that contain the symbol, name, sector, sub-industry, and HQ location of each company respectively.
    '''

    # get the raw html of the page
    html = requests.get(WIKIPEDIA_URL).text

    # parse
    soup = bs4.BeautifulSoup(html, "html.parser")

    # find the table that contains all of the companies
    company_table : Tag = soup.find(id="constituents")  

    # the table should exist
    assert(isinstance(company_table, Tag))

    result = []
    count = 0
    for row in company_table.findAll('tr'):
        if count == limit:
            break

        # get the columns of the row, which contain the information
        cols = row.findAll('td')

        result.append((
            cols[0].text.strip(), # symbol
            cols[1].text.strip(), # name
            cols[3].text.strip(), # sector
            cols[4].text.strip(), # sub-industry
            cols[5].text.strip(), # HQ location
            ))

        count += 1

    return result

def get_statistics(symbol: str):
    '''
    Uses three API calls to Finnhub to gather statistics about a specified stock symbol.

    Args:
        symbol: the symbol to find statistics for

    Returns:
        A dict with this structure:
        {
            price
            52_week_low
            52_week_high
            market_cap
            name
        }
    '''
    data = {}

    # quote data
    res = requests.get("https://finnhub.io/api/v1/quote?symbol={}&token={}".format(symbol, CONFIG["token"]))
    quote_data = res.json()

    data["price"] = quote_data["c"]

    # metrics data
    res = requests.get("https://finnhub.io/api/v1/stock/metric?symbol={}&metric=all&token={}".format(symbol, CONFIG["token"]))
    metric_data = res.json()

    data["52_week_high"] = metric_data["metric"]["52WeekHigh"]
    data["52_week_low"] = metric_data["metric"]["52WeekLow"]

    # profile data
    res = requests.get("https://finnhub.io/api/v1/stock/profile2?symbol={}&token={}".format(symbol, CONFIG["token"]))
    profile_data = res.json()

    data["market_cap"] = profile_data["marketCapitalization"]
    data["name"] = profile_data["name"]

    return data

def create_CSV(path: str, delay: float = 0):
    '''
    Writes the CSV to the specified path.

    Args:
        path:   the path of the file to write to
        delay:  the number of milliseconds to wait between each company,
                in order to not exceed Finnhub's API call limit
    '''

    # get the list of companies in the S&P 500
    companies = get_list_of_companies(500)

    # make the progress bar
    bar = Bar("Loading", max=len(companies), suffix="(%(index)d/%(max)d) Elapsed: %(elapsed)ds | Remaining: %(eta)ds")

    # open the CSV
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)

        # write the header row
        writer.writerow(["symbol", "name", "sector", "subindustry", "hq_location", "price", "52_week_low", "52_week_high", "market_cap"])

        for symbol, name, sector, subindustry, hq in companies:
            # get the statistics for the company
            # this will use 3 API calls
            stats = get_statistics(symbol)

            # write the data to the CSV
            writer.writerow([symbol, name, sector, subindustry, hq, stats["price"], stats["52_week_low"], stats["52_week_high"], stats["market_cap"]])

            # increase the progress bar
            bar.next()

            # add a delay in order to not exceed API call limits
            if delay > 0:
                time.sleep(delay/1000)

    # finish the progress bar
    bar.finish()

# since I'm making 3 API calls per stock, and the limit is 60 per minute, I need a 3 second delay between each stock
# theoretically, the delay only has to be 3000, but I'm using 3500 to be safe
# this comes to about 30 minutes to load the entire S&P 500
create_CSV(CONFIG["outputFile"], CONFIG["delay"])
