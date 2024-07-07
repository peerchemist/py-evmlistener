from plyer import notification
from models import BurnEvent


def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="Py-evmlistener",
        timeout=10,  # duration in seconds
    )


b = BurnEvent(
    who="0xb11dc0eaAd82cbf9faAbbffcbfc9c9Bf2A409cEA",
    amount=9999999,
    unwrap_address="PMr2Syadd5t1LfZvtAxwQEtQNKpyXTNVtX",
    block_number=199999,
    txid="0xc4ba8b1df526f5ce524d0a4d8e37a4a37181345159eea9b4cbfe3f3a2b317604",
)

# Example usage:
show_notification("New burn event!", str(b))
