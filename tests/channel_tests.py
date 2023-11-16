#!/usr/bin/env python3
import requests
import requests_mock
import unittest
from xb8_docsis_stats.lib import channel
from xb8_docsis_stats.lib import init_proc
from xb8_docsis_stats.lib import http

class ChannelTests(unittest.TestCase):
    def test_tables(self):
        page = None
        with open('./tests/network_setup.jst') as f:
            page = f.read()
        tables = channel.Tables()
        tables.load(str(page))
        self.assertEqual(tables.Downstream[0].ChannelId, 32)
        self.assertEqual(tables.Upstream[0].ChannelId, 6)
        self.assertEqual(tables.Downstream[0].SNR, 40.8)
        self.assertEqual(tables.Downstream[0].Frequency, "579 MHz")
        self.assertEqual(tables.Downstream[0].Modulation, "256 QAM")
        self.assertEqual(tables.Downstream[0].LockStatus, "Locked")
        self.assertEqual(tables.Downstream[0].Error.Unerrored, 3467992991)

    def test_init_proc(self):
        page = None
        with open('./tests/network_setup.jst') as f:
            page = f.read()
        ip = init_proc.InitializationProcedure()
        ip.load(str(page))
        self.assertEqual(ip.InitializeHardware, init_proc.InitStatus.Complete)


if __name__ == '__main__':
    unittest.main()
