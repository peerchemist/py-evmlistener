import re
from eth_utils import keccak
from eth_abi import decode
from typing import Union


def prepare_latest_block_number_rpc() -> dict:
    # Prepare the JSON-RPC request to get the latest block number
    rpc_request = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}

    return rpc_request


def compute_event_signature(event_definition: str) -> str:
    """
    Calculates the even topic hex.
    event_definition: "WPPCBurned (index_topic_1 address from, index_topic_2 address to, uint256 tokens, string externalAddress)"
    """
    # Extract the event name
    event_name = re.match(r"\w+", event_definition).group()

    # Extract the types in the parentheses
    types = re.findall(r"\b(address|uint256|string)\b", event_definition)

    # Format the simplified event definition without any whitespace
    simplified_event = f"{event_name}({','.join(types)})"
    # Compute the event topic (keccak-256 hash of the event signature)
    event_topic = "0x" + keccak(text=simplified_event).hex()

    return event_topic


def prepare_burned_filter_rpc_request(
    contract_address: str,
    event_topic: str,
    from_block: int,
    to_block: Union[int, str],
) -> str:
    # Create the filter parameters
    filter_params = {
        "fromBlock": hex(from_block),
        "toBlock": to_block if to_block == "latest" or "finalized" else hex(to_block),
        "address": contract_address,
        "topics": [event_topic],
    }

    # Prepare the JSON-RPC request
    rpc_request = {
        "jsonrpc": "2.0",
        "method": "eth_getLogs",
        "params": [filter_params],
        "id": 1,
    }

    return rpc_request


def decode_data(data: str) -> str:
    # this is horribly specific for WPPCBurned but it is what it is
    decoded_data = decode(["uint256", "string"], bytes.fromhex(data[2:]))
    print(f"Decoded Data: {decoded_data}")

    return decoded_data


"""
async with aiohttp.ClientSession() as session:
    async with session.post(rpc_address, json=rpc_request) as response:
        if response.status == 200:
            response_json = await response.json()
            if "error" in response_json:
                error_code = response_json["error"]["code"]
                error_message = response_json["error"]["message"]
                print(f"Error: {error_code}, {error_message}")
            else:
                logs = response_json.get("result", [])
                for log in logs:
                    print("Log found:")
                    print(f"Address: {log['address']}")
                    print(f"Data: {log['data']}")
                    print(f"Topics: {log['topics']}")

                    # Decode the data
                    data = log["data"]
                    decode_data(data)

        else:
            print(f"HTTP Error: {response.status}, {await response.text()}")
"""
