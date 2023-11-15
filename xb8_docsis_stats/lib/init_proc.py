from bs4 import Tag
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import enum
import logging
import re
from typing import Dict


log = logging.getLogger('root')


class InitStatus(enum.Enum):
    # states should be in order and correlate to the `Value Mappings`
    # in Grafana
    NotStarted = 1  # enum.auto() # first
    Complete = 10  #enum.auto() # last


@dataclass_json
@dataclass
class InitializationProcedure:
    """InitializationProcedure stats"""
    InitializeHardware: InitStatus = field(
        default_factory=lambda: InitStatus.NotStarted)
    AcquireDownstreamChannel: InitStatus = field(
        default_factory=lambda: InitStatus.NotStarted)
    UpstreamRanging: InitStatus = field(
        default_factory=lambda: InitStatus.NotStarted)
    DHCPbound: InitStatus = field(
        default_factory=lambda: InitStatus.NotStarted)
    SetTimeofDay: InitStatus = field(
        default_factory=lambda: InitStatus.NotStarted)
    ConfigurationFileDownload: InitStatus = field(
        default_factory=lambda: InitStatus.NotStarted)
    Registration: InitStatus = field(
        default_factory=lambda: InitStatus.NotStarted)

    def __init__(self, tag: Tag):
        divs = tag.find_all("div", class_='form-row')
        for div in divs:
            label = div.find('span', class_='readonlyLabel').string
            # remove all the stuff we don't want from the label
            label = re.sub(r'[-: ]+', '', label)
            value = div.find('span', class_='value').string
            try:
                val = getattr(InitStatus, value)
                setattr(self, label, val)
            except ValueError:
                log.error("Invalid InitStatus: %s = %s", label, value)
                continue

    @property
    def metrics(self) -> Dict[str, InitStatus]:
        return {
            'InitializeHardware': self.InitializeHardware,
            'AcquireDownstreamChannel': self.AcquireDownstreamChannel,
            'UpstreamRanging': self.UpstreamRanging,
            'DHCPbound': self.DHCPbound,
            'SetTimeofDay': self.SetTimeofDay,
            'ConfigurationFileDownload': self.ConfigurationFileDownload,
            'Registration': self.Registration,
        }
