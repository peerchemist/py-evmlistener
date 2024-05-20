import sys
import asyncio
import aiohttp
from typing import Awaitable
from aiosqlite import Connection
import picologging as logging
from listener.config import AppConfig, NetworkConfig, DeployedConfig
from listener.db import (
    db_connection,
    create_table_if_not_exists,
    get_block_height,
    update_block_height,
    ensure_contract_record_exists_in_db,
)
from listener.models import BurnEvent
from listener.telegram import (
    send_telegram_message,
    format_burn_event_message,
)
from listener.evmlog import (
    decode_data,
    prepare_latest_block_number_rpc,
    prepare_burned_filter_rpc_request,
)

# Main conf
Configuration = AppConfig.from_toml(file_path="conf.toml")
DeployedConfig = DeployedConfig.from_toml("conf.toml")

## Setup logger
logger = logging.getLogger("MainLoop")
logger.setLevel(logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
fmt = logging.Formatter(
    "%(name)s: %(asctime)s | %(levelname)s | %(process)d >>> %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",  # This specifies the format for `asctime`
)
stdout_handler.setFormatter(fmt)
logger.addHandler(stdout_handler)


async def post_request(session, rpc_url, rpc_request):
    async with session.post(rpc_url, json=rpc_request) as response:
        if response.status == 200:
            response_json = await response.json()
            if "error" in response_json:
                error_code = response_json["error"]["code"]
                error_message = response_json["error"]["message"]
                print(f"Error: {error_code}, {error_message}")
                return None, f"Error: {error_code}, {error_message}"
            else:
                return response_json["result"], None
        else:
            error_message = f"HTTP Error: {response.status}, {await response.text()}"
            print(error_message)
            return None, error_message


async def handle_event(event, explorer_url: str) -> None:
    print(event)

    event_data = decode_data(event["data"])

    burn = BurnEvent(
        who=event["address"],
        amount=event_data[0],
        unwrap_address=event_data[1],
        block_number=int(str(event["blockNumber"]), 16),
        txid=event["transactionHash"],
    )
    print(burn)
    logger.info("Found a burn event.")

    formatted_message = format_burn_event_message(burn, explorer_url)

    await send_telegram_message(
        Configuration.chat_id, Configuration.tg_bot_token, formatted_message
    )


async def task_with_retry(task_func, max_retries: int, *args, **kwargs) -> Awaitable:
    """
    A wrapper to retry a task up to `max_retries` times.
    """
    for attempt in range(max_retries):
        try:
            return await task_func(*args, **kwargs)
        except Exception as e:
            print(f"Task failed with {e}, retrying... {attempt + 1}/{max_retries}")
            await asyncio.sleep(5)  # wait a bit before retrying
    raise Exception("Task failed after max retries")


async def fetch_new_log_entries(
    session: aiohttp.ClientSession,
    rpc_url: str,
    rpc_request: dict,
    explorer_url: str,
):
    events, error = await post_request(session, rpc_url, rpc_request)
    if events:
        for ev in events:
            await handle_event(ev, explorer_url)
    else:
        pass


async def create_log_monitoring_task(
    session: aiohttp.ClientSession, from_block: int, config: NetworkConfig
) -> list[Awaitable]:
    rpc_request = prepare_burned_filter_rpc_request(
        config.contract.address, config.contract.events[0], from_block, "finalized"
    )

    return [
        task_with_retry(
            fetch_new_log_entries,
            Configuration.max_retries,
            session,
            config.rpc.url,
            rpc_request,
            config.explorer_url,
        )
    ]


async def main_loop() -> None:
    database: Connection = await db_connection(Configuration)
    logger.info("Connected to the database.")
    # check if table exists and create it if not
    await create_table_if_not_exists(database)

    logger.info("Entering the main loop.")

    async with aiohttp.ClientSession() as session:
        for network_config in DeployedConfig.deployed:
            await ensure_contract_record_exists_in_db(
                db=database,
                contract=network_config.contract.address,
                block_height=network_config.contract.from_block_height,
                network_id=network_config.network_id,
            )

            try:
                while True:
                    logger.info("Entering the main loop...")
                    # last seen block number
                    last_recorded_block = await get_block_height(
                        database, network_config.contract.address
                    )

                    # Get the current block number
                    response, error = await post_request(
                        session,
                        network_config.rpc.url,
                        prepare_latest_block_number_rpc(),
                    )
                    if response:
                        current_block_number = int(str(response), 16)
                    else:
                        print("Unable to get current block number, going off.")
                        sys.exit()

                    print("Current block is: ", current_block_number)

                    # spawn tasks
                    task_list = await create_log_monitoring_task(
                        session=session,
                        from_block=last_recorded_block,
                        config=network_config,
                    )

                    # run tasks
                    results = await asyncio.gather(*task_list, return_exceptions=True)

                    # save the block number to cache file
                    await update_block_height(
                        database, network_config.contract.address, current_block_number
                    )

                    for result in results:
                        if isinstance(result, Exception):
                            print(f"Task ended with error: {result}")

                    # finished the cycle, go to sleep
                    print("Going to sleep.")
                    await asyncio.sleep(int(Configuration.loop_timeout))

            except KeyboardInterrupt:
                print("\nGracefully exiting...")
                await database.close()
                await session.close()


asyncio.run(main_loop())
