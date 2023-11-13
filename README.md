# Comcast XB7/XB8 DOCSIS Stats WebScraper

This is a webscraper for collecting the DOCSIS modem stats for the
[Comcast XB7/XB8 modem](
https://www.xfinity.com/support/articles/broadband-gateways-userguides)
for tracking in [Graphite Carbon](https://github.com/graphite-project/carbon).

## Overview

Comcast XB7/XB8 modems report on a variety of statistics which are useful
for monitoring the health and performance of your internet connection.

Unfortunately, Comcast placed these stats behind a rather slow and
ugly web server and not over a more appropriate and industry standard
interface like SNMP.

This project logs into the webUI of the XB7/XB8 modem and scrapes the
HTML table information for the `Downstream` and `Upstream` channels.
It then submits this data to your Graphite server.

## Running

I recommend to use the provided [docker-compose](docker-compose.yaml)
to run xb8-stats and submit to [Graphite Statsd](
https://hub.docker.com/r/graphiteapp/graphite-statsd/).

Create a `.env` file with the following:

```bash
GRAPHITE=<host>:<port>
PASSWORD=<modem password>
```
