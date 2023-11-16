#!/usr/bin/env python3
__description__ = "Comcast XB7/XB8 DOCSIS stats scraper"
__author__ = "Aaron Turner <synfinatic at gmail dot com"

import argparse
from bs4 import BeautifulSoup
import logging
import graphyte
import requests
import time

from lib.args import EnvDefault
from lib.channel import Tables
from lib.logging import LogLevel
from lib.init_proc import InitializationProcedure
from lib.http import XBRConfig, fetch_network_stats_page

log = None


def fetch_init_proc(page: str) -> InitializationProcedure:
    soup = BeautifulSoup(page, "html.parser")

    content = soup.find(id='content')
    modules = content.find_all("div", class_="module")

    init_proc: InitializationProcedure = None

    for i, m in enumerate(modules):
        # first look for the Initialization Procedure section
        h2 = m.find("h2")
        if h2 is not None and h2.string == 'Initialization Procedure':
            init_proc = InitializationProcedure(m)
            break
    return init_proc


def fetch_stats(page: str) -> Tables:
    soup = BeautifulSoup(page, "html.parser")
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


def submit_metrics(args, tables: Tables, init_proc: InitializationProcedure):
    host, port = args.graphite.split(':')
    sender = graphyte.Sender(host, port=port, raise_send_errors=True)
    i = 0
    for metric, value in init_proc.metrics.items():
        name = '.'.join([args.prefix, 'InitProcedure', metric])
        sender.send(name, value.value)
        i += 1

    for k in ['Downstream', 'Upstream']:
        for table in getattr(tables, k):
            for metric in table.metrics:
                name = '.'.join([args.prefix, metric.Name])
                sender.send(name, metric.Value)
                i += 1

    sender.stop()
    log.info('sent %d metrics', i)


def loop(config: XBRConfig, args):
    tables = None
    try:
        page = fetch_network_stats_page(config)
        tables = fetch_stats(page)
        init_proc = fetch_init_proc(page)
    except requests.exceptions.RequestException as e:
        log.error("Unable to poll modem: %s", e)
    # let ValueError() to up the stack as it is fatal
    tables.map_channels()
    if args.dump_json:
        print(tables.to_json())
        print(init_proc.to_json())
    else:
        submit_metrics(args, tables, init_proc)


def main():
    global log
    logging.basicConfig(format='%(levelname)s %(asctime)s: %(message)s')
    log = logging.getLogger("root")

    parser = argparse.ArgumentParser(
        prog='xb8-stats',
        description=__description__,
    )

    action_group = parser.add_mutually_exclusive_group(required=True)
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
    action_group.add_argument(
        '--dump-json', action='store_true',
        help='Dumps the stats as JSON instead')
    action_group.add_argument(
        '--graphite', type=str,
        help='host:port of the graphite submission server')
    parser.add_argument(
        '--prefix', type=str, default='modem',
        help='Graphite metric prefix for metrics (%(default)s)')
    parser.add_argument(
        '--interval', type=int, default=0,
        help='Number of seconds between each poll cycle')
    parser.add_argument(
        '--log-level', type=LogLevel, choices=list(LogLevel),
        default='info', help='Log level (%(default)s)')

    args = parser.parse_args()
    log.setLevel(args.log_level.level)

    config = XBRConfig(
        Hostname=args.modem,
        Username=args.username,
        Password=args.password,
    )

    loop(config, args)
    if args.interval:
        while True:
            time.sleep(args.interval)
            loop(config, args)


if __name__ == "__main__":
    main()
