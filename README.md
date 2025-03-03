# Please Read!!!

I am no longer a Comcast/Xfinity customer and hence will not be continuing
to develop or supporting this project.

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

## Support

So I've only tested this code against an XB8 modem.  I'm fairly certain
that it will work with the XB7 because I believe the webUI is the same.
If you find it doesn't work, by all means open a ticket and include
the HTML for the `Gateway > Connection > XFINITY Network` page.

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

Docker images are available via [Docker Hub](
https://hub.docker.com/repository/docker/synfinatic/xb8-docsis-stats/general)

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

## Example Graphs

Here are some real world graphs.

![example1](https://github.com/synfinatic/xb8-docsis-stats/assets/1075352/c8012ea9-2317-4383-a42f-34a6238b7077)

![example2](https://github.com/synfinatic/xb8-docsis-stats/assets/1075352/ad256a47-4d3e-4fb6-9dd5-497c01c9906d)

Note, the graphs with "No data" are not bugs, but rather indications that there
are no matching "uncorrectable" errors.  The gap in the data is when I power
cycled my modem. :)

As you can see from the above, my modem looks pretty good, except I have two
channels which have a ~50% correctable error rate.  All the other channels are
less than 0.05% and are not reported.
