#!/usr/bin/env python3
__description__ = "Comcast XB7/XB8 DOCSIS stats scraper"
__author__ = "Aaron Turner <synfinatic at gmail dot com"

import argparse
import requests
import logging
from bs4 import BeautifulSoup
from typing import Union
from typing import Dict
from typing import List


from lib.args import EnvDefault
from lib.channel import Downstream, Upstream, Error, Tables

log = logging.getLogger("root")
log.setLevel(logging.DEBUG)


def login(args) -> Dict[str, str]:
    page = requests.post(f'http://{args.modem}/check.jst',
        data = {
            'username': args.username,
            'password': args.password,
        })
    page.raise_for_status()
    return page.cookies


def fetch_stats(args) -> Tables:
    cookie_jar = login(args)

    page = requests.get(f'http://{args.modem}/network_setup.jst',
                        cookies=cookie_jar)
    page.raise_for_status()
    soup = BeautifulSoup(page.content, "html.parser")

    content = soup.find(id='content')
    modules = content.find_all("div", class_="module")

    tables = Tables()

    midx = 0
    for i, m in enumerate(modules):
        # seems to be more <div class="module"> than I expect??
        table = m.find("table", class_="data")
        if table is None:
            continue

        # process the table header
        thead = table.find("thead")
        td = thead.find("td")

        mtype = Tables.fields[midx]
        midx += 1

        # process table body
        body = table.find("tbody")
        for ridx, row in enumerate(body.find_all("tr")):
            for cidx, column in enumerate(row.find_all("td")):
                val = column.text.strip()
                if ridx == 0:
                    tables.new(mtype)
                try:
                    tables.add(mtype, cidx, ridx, val)
                except ValueError as e:
                    log.error(f'mtype = {mtype}, cidx = {cidx}, ridx = {ridx}, val = {val}')
                    raise e
    return tables


def main():
    parser = argparse.ArgumentParser(
        prog='xb8-stats',
        description=__description__,
    )

    parser.add_argument('--modem', type=str, default='10.0.0.1',
                        help='IP or hostname of the modem')
    parser.add_argument('--username', '-u', type=str, default='admin',
                        help='Username to use to login to the modem')
    parser.add_argument('--password', '-p', action=EnvDefault,
                        envvar='XB8_PASSWORD', required=True,
                        help='Password to use to login to the modem')

    args = parser.parse_args()

    tables = fetch_stats(args)
    print(tables.to_json())


if __name__ == "__main__":
    main()
