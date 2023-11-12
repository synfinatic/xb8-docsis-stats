from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import logging
from typing import List
from typing import ClassVar


log = logging.getLogger("root")


@dataclass_json
@dataclass
class Downstream:
    fields: ClassVar[List[str]] = ["ChannelId", "LockStatus", "Frequency", "SNR", "PowerLevel",
             "Modulation"]

    ChannelId: int = 0
    LockStatus: str = "Unknown" # Locked, ???
    Frequency: str = "" # Mhz
    SNR: float = 0.0 # Db
    PowerLevel: float = 0.0 # dBmV
    Modulation: str = "Unknown" # 256QAM / OFDM

    def set(self, row_idx: int, val: str):
        log.debug(f'{Downstream.fields[row_idx]} = {val}')
        match Downstream.fields[row_idx]:
            case 'ChannelId':
                setattr(self, Downstream.fields[row_idx], int(val))
            case 'LockStatus' | 'Modulation' | 'Frequency':
                setattr(self, Downstream.fields[row_idx], val)
            case 'xFrequency':
                if val.find(" ") != -1:
                    x, _ = val.split(" ", 1)
                    setattr(self, Downstream.fields[row_idx], int(x))
                else: # not everything is Mhz??
                    setattr(self, Downstream.fields[row_idx], int(val))
            case 'SNR' | 'PowerLevel':
                x, _ = val.split(" ", 1)
                setattr(self, Downstream.fields[row_idx], float(x))
            case _:
                raise ValueError(f'Unknown Downstream field {row_idx} = {val}')



@dataclass_json
@dataclass
class Upstream:
    fields: ClassVar[List[str]] = ["ChannelId", "LockStatus", "Frequency", "SymbolRate", "PowerLevel",
           "Modulation", "ChannelType"]

    ChannelId: int = 0
    LockStatus: str = "Unknown" # Locked, ???
    Frequency: str = "" # Mhz
    SymbolRate: int = 0 # only upstream
    PowerLevel: float = 0.0 # dBmV
    Modulation: str = "Unknown" # 256QAM / OFDM
    ChannelType: str = "" # only upstream ATDMA

    def set(self, row_idx: int, val: str):
        match Upstream.fields[row_idx]:
            case 'ChannelId' | 'SymbolRate':
                setattr(self, Upstream.fields[row_idx], int(val))
            case 'LockStatus' | 'Modulation' | 'ChannelType' | 'Frequency':
                setattr(self, Upstream.fields[row_idx], val)
            case 'xFrequency':
                x, _ = val.split(" ", 1)
                setattr(self, Upstream.fields[row_idx], int(x))
            case 'PowerLevel':
                x, _ = val.split(" ", 1)
                setattr(self, Upstream.fields[row_idx], float(x))
            case _:
                raise ValueError(f'Unknown Upstream field {row_idx} = {val}')


@dataclass_json
@dataclass
class Error:
    fields: ClassVar[List[str]] = ["ChannelId", "Unerrored", "Correctable", "Uncorrectable"]
    ChannelId: int = 0
    Unerrored: int = 0
    Correctable: int = 0
    Uncorrectable: int = 0

    def set(self, row_idx: int, val: str):
        match Error.fields[row_idx]:
            case 'ChannelId' | 'Unerrored' | 'Correctable' | 'Uncorrectable':
                setattr(self, Error.fields[row_idx], int(val))
            case _:
                raise ValueError(f'Unknown Errors field {row_idx} = {val} {ERROR_LIST}')


@dataclass_json
@dataclass
class Tables:
    fields: ClassVar[List[str]] = ['Downstream', 'Upstream', 'Error']
    Downstream: List[Downstream] = field(default_factory=lambda: [])
    Upstream: List[Upstream] = field(default_factory=lambda: [])
    Error: List[Error] = field(default_factory=lambda: [])

    def new(self, kind: str):
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
        match kind.lower():
            case 'downstream':
                self.Downstream[cidx].set(ridx, val)
            case 'upstream':
                self.Upstream[cidx].set(ridx, val)
            case 'error':
                self.Error[cidx].set(ridx, val)
            case _:
                raise ValueError(f'Invalid module type = {kind}')

