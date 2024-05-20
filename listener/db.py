import os
import aiosqlite
from pathlib import Path
from listener.config import AppConfig


async def db_connection(config: AppConfig) -> aiosqlite.Connection:
    db_path = Path(f"persist/{config.db_name}")

    # Ensure the parent directory exists
    if not db_path.parent.exists():
        os.makedirs(db_path.parent)

    # Check if the database file exists, if not it will be created automatically by aiosqlite.connect
    if not db_path.exists():
        print(f"Database file {db_path} not found. It will be created.")

    db_connection = await aiosqlite.connect(db_path, isolation_level=None)
    return db_connection


async def create_table_if_not_exists(db: aiosqlite.Connection) -> None:
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS block_heights (
            contract TEXT PRIMARY KEY,
            block_height INTEGER,
            network_ID INTEGER
        )
    """
    )
    await db.commit()


async def get_block_height(db: aiosqlite.Connection, contract: str) -> int:
    async with db.execute(
        "SELECT block_height FROM block_heights WHERE contract = ?", (contract,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else None


async def update_block_height(
    db: aiosqlite.Connection, contract: str, new_block_height: int
) -> None:
    await db.execute(
        "UPDATE block_heights SET block_height = ? WHERE contract = ?",
        (new_block_height, contract),
    )
    await db.commit()


async def ensure_contract_record_exists_in_db(
    db: aiosqlite.Connection,
    contract: str,
    block_height: int,
    network_id: int,
) -> None:
    async with db.execute(
        "SELECT 1 FROM block_heights WHERE contract = ?", (contract,)
    ) as cursor:
        if await cursor.fetchone() is None:
            await db.execute(
                "INSERT INTO block_heights (contract, block_height, network_id) VALUES (?, ?, ?)",
                (contract, block_height, network_id),
            )
            await db.commit()
