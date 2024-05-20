from dataclasses import dataclass
from typing import List
import tomllib


@dataclass(frozen=True)
class AppConfig:
    db_name: str
    loop_timeout: int
    tg_bot_token: str
    chat_id: str
    max_retries: int

    @classmethod
    def from_toml(cls, file_path: str):
        with open(file_path, "rb") as file:
            config_data = tomllib.load(file)
            config_params = config_data["Config"]
            return cls(
                db_name=config_params["db_name"],
                loop_timeout=config_params["loop_timeout"],
                tg_bot_token=config_params["tg_bot_token"],
                chat_id=config_params["chat_id"],
                max_retries=config_params["max_retries"],
            )


@dataclass
class RPCConfig:
    url: str
    key: str


@dataclass
class ContractConfig:
    address: str
    from_block_height: int
    events: list


@dataclass
class NetworkConfig:
    name: str
    network_id: int
    rpc: RPCConfig
    contract: ContractConfig
    explorer_url: str


@dataclass(frozen=True)
class DeployedConfig:
    deployed: List[NetworkConfig]

    @classmethod
    def from_toml(cls, file_path: str):
        with open(file_path, "rb") as file:
            config_data = tomllib.load(file)
            deployed_networks = []
            for network in config_data["DeployedConfig"]["deployed"]:
                deployed_networks.append(
                    NetworkConfig(
                        name=network["name"],
                        network_id=network["network_id"],
                        rpc=RPCConfig(
                            url=network["rpc"]["url"], key=network["rpc"]["key"]
                        ),
                        contract=ContractConfig(
                            address=network["contract"]["address"],
                            from_block_height=network["contract"]["from_block_height"],
                            events=network["contract"]["events"],
                        ),
                        explorer_url=network["explorer_url"],
                    )
                )
            return cls(deployed=deployed_networks)
