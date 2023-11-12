#!/usr/bin/env python3
__description__ = "Comcast XB7/XB8 DOCSIS stats scraper"
__author__ = "Aaron Turner <synfinatic at gmail dot com"

import argparse
from bs4 import BeautifulSoup
from enum import Enum
import logging
import graphyte
import requests
import time
from typing import Dict

from lib.args import EnvDefault
from lib.channel import Tables

log = logging.getLogger("root")
log.setLevel(logging.WARNING)


class LogLevel(Enum):
    error = 'error'
    info = 'info'
    warn = 'warning'
    debug = 'debug'

    def __str__(self):
        return self.value


def login(args) -> Dict[str, str]:
    page = requests.post(f'http://{args.modem}/check.jst',
        data={
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
                    log.error(
                        f'mtype = {mtype}, cidx = {cidx}, '
                        f'ridx = {ridx}, val = {val}')
                    raise e
    return tables


def submit_metrics(args, tables: Tables):
    host, port = args.graphite.split(':')
    sender = graphyte.Sender(host, port=port, raise_send_errors=True)
    i = 0
    for k in ['Downstream', 'Upstream']:
        for table in getattr(tables, k):
            for metric in table.metrics:
                name = '.'.join([args.prefix, metric.Name])
                i += 1
                sender.send(name, metric.Value)
    sender.stop()
    log.info('sent %d metrics', i)


def loop(args):
    tables = fetch_stats(args)
    tables.map_channels()
    if args.dump_json:
        print(tables.to_json())
    else:
        submit_metrics(args, tables)


def main():
    parser = argparse.ArgumentParser(
        prog='xb8-stats',
        description=__description__,
    )

    parser.add_argument(
        '--modem', type=str, default='10.0.0.1',
        help='IP or hostname of the modem (%(default)s)')
    parser.add_argument(
        '--username', '-u', type=str, default='admin',
        help='Username to use to login to the modem (%(default)s)')
    parser.add_argument(
        '--password', '-p', action=EnvDefault,
        envvar='XB8_PASSWORD', required=True,
        help='Password to use to login to the modem')
    parser.add_argument(
        '--graphite', type=str, required=True,
        help='host:port of the graphite submission server')
    parser.add_argument(
        '--prefix', type=str, default='modem',
        help='Graphite metric prefix for metrics (%(default)s)')
    parser.add_argument(
        '--interval', type=int, default=0,
        help='Number of seconds between each poll cycle')
    parser.add_argument(
        '--dump-json', action='store_true',
        help='Dumps the stats as JSON instead')
    parser.add_argument(
        '--log-level', type=LogLevel, choices=list(LogLevel),
        default='info', help='Log level (%(default)s)')

    args = parser.parse_args()
    log.setLevel(args.log_level)

    loop(args)
    if args.interval:
        while True:
            time.sleep(args.interval)
            loop(args)


if __name__ == "__main__":
    main()
