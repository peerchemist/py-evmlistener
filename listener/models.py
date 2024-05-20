from dataclasses import dataclass


@dataclass
class BurnEvent:
    who: str
    amount: int
    unwrap_address: str
    block_number: int
    txid: str


@dataclass
class MintEvent:
    amount: int
    who: str
    block_number: int
    txid: str


@dataclass
class BlockHeight:
    contract: str
    block_height: int
    network_id: int
