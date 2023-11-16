# Comcast XB7/XB8 DOCSIS Stats for Graphite

This is a webscraper for collecting the DOCSIS modem stats for the
[Comcast XB7/XB8 modem](
https://www.xfinity.com/support/articles/broadband-gateways-userguides)
for tracking in [Graphite Carbon](https://github.com/graphite-project/carbon).

Have an Arris modem?  Maybe try out [arris-exporter](
https://github.com/guildencrantz/arris-exporter).

## Overview

Comcast XB7/XB8 modems report on a variety of statistics which are useful
for monitoring the health and performance of your internet connection.

Unfortunately, Comcast placed these stats behind a rather slow and
ugly web server and not over a more appropriate and industry standard
interface like SNMP.

This project logs into the webUI of the XB7/XB8 modem and scrapes the
HTML table information for the `Downstream` and `Upstream` channels.
It then submits this data to your Graphite server.

## Installation

### Graphite Config

Assuming you're using a 5min poll cycle (`--interval 300` which is the default
for the docker image) I recommend adding the following to the top of your
[storage-schemas.conf](
https://graphite.readthedocs.io/en/latest/config-carbon.html#storage-schemas-conf):

```ini
[modem]
pattern = ^modem\.
retentions = 5m:90d,30m:335d,1h:3y
```

If you change the interval, modify the `retentions` line to match or your
grafana logs are gonna be sad.

### Running

I recommend to use the provided [docker-compose](docker-compose.yaml)
to run xb8-stats and submit to [Graphite Statsd](
https://hub.docker.com/r/graphiteapp/graphite-statsd/).

Create a `.env` file with the following:

```bash
GRAPHITE=<host>:<port>
PASSWORD=<modem password>
```

### Grafana Dashboard

I've created a [dashboard](grafana.json) for [Grafana](https://grafana.com) which should be a
good starting point for others.

#### Initialization Procedure

So I have learned that the XB7/XB8 doesn't expose any statistics for the channels
whatsoever in certain more extreme "down" situations.  To help debug these situations
we poll the `Initialization Procedure` data which may help debug and diagnose the
situation.

That said, if you have a working connection, by the time the modem has made the
webUI available for polling, all of these stats should be marked `Completed`.
