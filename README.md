# py-evmlistener

This daemon establishes a JSON-RPC connection with a remote EVM blockchain RPC node to monitor EVM log events, specifically Burn and Mint events.
Upon detecting new log entries, it sends notifications through the Telegram API. Support for desktop notification sis work in progress.

See the `config.py` file to see how to define contract to be monitored.

## Config

Write a configuration like this in the `conf.toml` file.

```
[Config]
db_name = "wrapservice"
loop_timeout = 1200     # 20 minutes of pause between loops
tg_bot_token = ""       # Telegram bot token
chat_id = "-"           # Channel in which the bot will post notifications
max_retries = 2         # Number of retries per API call, in case it fails

# Here deployed network is defined
[[DeployedConfig.deployed]]
name = "EthereumMainnet"
network_id = 1
explorer_url = "https://etherscan.io/tx/"

# Here RPC API endpoint is defined
[DeployedConfig.deployed.rpc]
url = "https://eth.llamarpc.com"
key = ""

# Here the contract is defined
[DeployedConfig.deployed.contract]
address = "0x044d078F1c86508e13328842Cc75AC021B272958"
events = [
    "0x935de72880f413b300ee847a0c53a5dda664c42a0a4adddd88cf2a556f39ae01",
] # [WPPCBurned] List of events
from_block_height = 19904399
```