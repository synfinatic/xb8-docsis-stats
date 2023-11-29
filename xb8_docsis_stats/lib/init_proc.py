from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import enum
import logging
import re
from typing import Dict


log = logging.getLogger('root')


class InitStatus(enum.Enum):
    # states should be in order and correlate to the `Value Mappings`
    # in Grafana.  Per my contact at Comcast, there are only 3 possible values:
    NotStarted = 1  # enum.auto() # first
    InProgresss = 2
    Complete = 3  #enum.auto() # last


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

    def load(self, page: str):
        soup = BeautifulSoup(page, "html.parser")

        content = soup.find(id='content')
        modules = content.find_all("div", class_="module")
        match = False
        for i, m in enumerate(modules):
            # first look for the Initialization Procedure section
            h2 = m.find("h2")
            if h2 is not None and h2.string == 'Initialization Procedure':
                match = True
                divs = m.find_all("div", class_='form-row')
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
        if not match:
            raise ValueError('Missing Initialization Procedure')

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
