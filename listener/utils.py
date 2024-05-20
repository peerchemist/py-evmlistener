def int_to_float(amount: int) -> float:
    return amount / 10**6


def address_to_explorer_url(address: str) -> str:
    return f"https://chainz.cryptoid.info/ppc/address.dws?{address}.htm"
