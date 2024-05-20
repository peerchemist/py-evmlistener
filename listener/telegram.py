import aiohttp

from listener.models import BurnEvent, MintEvent
from listener.utils import int_to_float


def format_burn_event_message(event: BurnEvent, explorer_url: str) -> str:
    message = f"""
        *Burn Event*
        - **Who**: `{event.who}`
        - Burned Amount: {int_to_float(event.amount)}
        - **Block Number**: {event.block_number}
        - [Transaction ID]({explorer_url + event.txid})
        - **Unwrap Address**: ```{event.unwrap_address}```
        - 
        """
    return message


def format_mint_event_message(event: MintEvent, explorer_url) -> str:
    message = f"""
        *Mint Event*
        - **Who**: `{event.who}`
        - **Amount**: {int_to_float(event.amount)}
        - **Block Number**: {event.block_number}
        - [Transaction ID]({explorer_url + event.txid})
        """
    return message


async def send_telegram_message(chat_id: str, bot_token: str, message: str) -> dict:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            return await response.json()
