from dataclasses import dataclass


@dataclass
class BurnEvent:
    who: str
    amount: int
    unwrap_address: str
    block_number: int
    txid: str

    def __str__(self) -> str:
        return (
            f"BurnEvent(who={self.who}, amount={self.amount}, unwrap_address={self.unwrap_address}, "
            f"block_number={self.block_number}, txid={self.txid})"
        )


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
