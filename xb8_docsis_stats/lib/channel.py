from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import logging
import re
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Union


log = logging.getLogger("root")


@dataclass
class Metric:
    """Carbon metric"""
    Name: str = field(default_factory=lambda: "")
    Value: Union[int, float] = field(default_factory=lambda: 0)
    Tags: Dict[str, str] = field(default_factory=lambda: dict())


@dataclass_json
@dataclass
class Channel:
    """Common channel fields"""
    ChannelId: int = 0
    Frequency: str = ""  # Mhz
    LockStatus: str = "Unknown"  # Locked, ???
    Modulation: str = "Unknown"  # 256QAM / OFDM

    def set(self, row_idx: int, val: str, fields: List[str]) -> bool:
        match fields[row_idx]:
            case 'ChannelId':
                setattr(self, fields[row_idx], int(val))
                return True
            case 'LockStatus' | 'Modulation' | 'Frequency':
                setattr(self, fields[row_idx], val)
                return True
        return False

    @property
    def name(self) -> str:
        freq = re.sub(r' +', '', self.Frequency)
        return f'{self.__class__.__name__}.{freq}'

    @property
    def metrics(self) -> List[Metric]:
        metrics = []
        for metric in self.__class__._metrics:
            # our metrics support using `.` to indicate the path
            objs = metric.split('.')
            val = self
            field = None
            while len(objs):
                field = objs.pop(0)
                val = getattr(val, field)

            metrics.append(
                Metric(
                    Name=f'{self.name}.{field}',
                    Value=val,
                    Tags={
                        'ChannelId': f'{self.ChannelId}',
                    }
                )
            )
        return metrics

    @property
    def Locked(self) -> int:
        if self.LockStatus == 'Locked':
            return 1
        return 0


@dataclass_json
@dataclass
class Error:
    """Mapping for the CM Error Codewords table"""
    _fields: ClassVar[List[str]] = [
        "ChannelId", "Unerrored", "Correctable", "Uncorrectable"]
    ChannelId: int = 0
    Unerrored: int = 0
    Correctable: int = 0
    Uncorrectable: int = 0

    def set(self, row_idx: int, val: str):
        match Error._fields[row_idx]:
            case 'ChannelId' | 'Unerrored' | 'Correctable' | 'Uncorrectable':
                setattr(self, Error._fields[row_idx], int(val))
            case _:
                raise ValueError(
                    f'Unknown Errors field {row_idx} = {val} {Error._fields}')


@dataclass_json
@dataclass
class Downstream(Channel):
    """Mapping for the Downstream / Channel Bonding table"""
    _fields: ClassVar[List[str]] = [
        "ChannelId", "LockStatus", "Frequency", "SNR", "PowerLevel",
        "Modulation"]
    _metrics: ClassVar[List[str]] = [
        'SNR', 'PowerLevel', 'Locked', 'Error.Unerrored', 'Error.Correctable',
        'Error.Uncorrectable',
    ]

    SNR: float = 0.0  # Db
    PowerLevel: float = 0.0  # dBmV
    Error: Error = None

    def set(self, row_idx: int, val: str):
        log.debug(f'{Downstream._fields[row_idx]} = {val}')
        if super(Downstream, self).set(row_idx, val, Downstream._fields):
            return
        match Downstream._fields[row_idx]:
            case 'ChannelId':
                setattr(self, Downstream._fields[row_idx], int(val))
            case 'LockStatus' | 'Modulation' | 'Frequency':
                setattr(self, Downstream._fields[row_idx], val)
            case 'SNR' | 'PowerLevel':
                x, _ = val.split(" ", 1)
                setattr(self, Downstream._fields[row_idx], float(x))
            case _:
                raise ValueError(f'Unknown Downstream field {row_idx} = {val}')


@dataclass_json
@dataclass
class Upstream(Channel):
    """Mapping for the Upstream / Channel Bonding table"""
    _fields: ClassVar[List[str]] = [
        "ChannelId", "LockStatus", "Frequency", "SymbolRate", "PowerLevel",
        "Modulation", "ChannelType"]
    _metrics: ClassVar[List[str]] = [
        'PowerLevel', 'Locked', 'SymbolRate'
    ]

    SymbolRate: int = 0  # only upstream
    PowerLevel: float = 0.0  # dBmV
    ChannelType: str = ""  # only upstream ATDMA
    # modem doesn't track upstream channel errors???

    def set(self, row_idx: int, val: str):
        if super(Upstream, self).set(row_idx, val, Upstream._fields):
            return
        match Upstream._fields[row_idx]:
            case 'SymbolRate':
                setattr(self, Upstream._fields[row_idx], int(val))
            case 'ChannelType':
                setattr(self, Upstream._fields[row_idx], val)
            case 'PowerLevel':
                x, _ = val.split(" ", 1)
                setattr(self, Upstream._fields[row_idx], float(x))
            case _:
                raise ValueError(f'Unknown Upstream field {row_idx} = {val}')


@dataclass_json
@dataclass
class Tables:
    fields: ClassVar[List[str]] = ['Downstream', 'Upstream', 'Error']
    Downstream: List[Downstream] = field(default_factory=lambda: [])
    Upstream: List[Upstream] = field(default_factory=lambda: [])
    Error: List[Error] = field(default_factory=lambda: [])

    def load(self, page: str):
        soup = BeautifulSoup(page, "html.parser")
        content = soup.find(id='content')
        modules = content.find_all("div", class_="module")

        midx = 0

        for i, m in enumerate(modules):
            # seems to be more <div class="module"> than I expect??
            table = m.find("table", class_="data")
            if table is None:
                continue

            mtype = self.fields[midx]
            midx += 1

            # process table body
            body = table.find("tbody")
            for ridx, row in enumerate(body.find_all("tr")):
                for cidx, column in enumerate(row.find_all("td")):
                    val = column.text.strip()
                    if ridx == 0:
                        self.new(mtype)
                    try:
                        self.add(mtype, cidx, ridx, val)
                    except ValueError as e:
                        log.error(
                            f'mtype = {mtype}, cidx = {cidx}, '
                            f'ridx = {ridx}, val = {val}')
                        raise e
        self.map_channels()

    def new(self, kind: str):
        """Create a new channel"""
        match kind.lower():
            case 'downstream':
                self.Downstream.append(Downstream())
            case 'upstream':
                self.Upstream.append(Upstream())
            case 'error':
                self.Error.append(Error())
            case _:
                raise ValueError(f'Invalid module type = {kind}')

    def add(self, kind: str, cidx: int, ridx: int, val: str):
        """Add a <td> to our channel"""
        match kind.lower():
            case 'downstream':
                self.Downstream[cidx].set(ridx, val)
            case 'upstream':
                self.Upstream[cidx].set(ridx, val)
            case 'error':
                self.Error[cidx].set(ridx, val)
            case _:
                raise ValueError(f'Invalid module type = {kind}')

    def map_channels(self):
        """Map the Error table to the Downstream table"""
        for error in self.Error:
            chan = self.find_channel(error.ChannelId)
            chan.Error = error
        self.Error = None

    def find_channel(self, chan: int) -> Union[Downstream, Upstream]:
        """Find the channel by channelId"""
        for down in self.Downstream:
            if down.ChannelId == chan:
                return down
        for up in self.Upstream:
            if up.ChannelId == chan:
                return up
        raise ValueError(f'Invalid channelId {chan}')
