def _indian_comma_group(s: str) -> str:
    if len(s) <= 3:
        return s
    last_three = s[-3:]
    rest = s[:-3]
    groups = []
    while len(rest) > 2:
        groups.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.append(rest)
    groups.reverse()
    return ",".join(groups) + "," + last_three


def format_inr(amount: float) -> str:
    if amount < 0:
        return "-" + format_inr(-amount)
    rounded = round(amount)
    formatted = "₹" + _indian_comma_group(str(rounded))
    if rounded >= 1_00_00_000:
        cr = amount / 1_00_00_000
        annotation = f"{cr:.2f}".rstrip("0").rstrip(".")
        formatted += f" (₹{annotation}Cr)"
    elif rounded >= 1_00_000:
        lakh = amount / 1_00_000
        annotation = f"{lakh:.2f}".rstrip("0").rstrip(".")
        formatted += f" (₹{annotation}L)"
    return formatted
