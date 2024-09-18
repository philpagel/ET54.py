"support functions"

def _toint(value):
    "strip leading 'R' and convert to int"

    if value.startswith("R"):
        value = value[1:]
    return int(value)

def _tofloat(value):
    "strip leading 'R' and convert to float"

    if value.startswith("R"):
        value = value[1:]
    return float(value)

def _tofloats(value):
    "strip leading 'R' split and convert all to float"

    if value.startswith("R"):
        value = value[1:].split()

    return [float(x) for x in value]

def _value_extend(x, n):
    "turn x into list of length n by replicating the last element"

    if isinstance(x, list):
        pass
    elif isinstance(x, tuple):
        x = list(x)
    elif isinstance(x, (int, float, str)):
        x = [x]
    else:
        raise ValueError(f"x must be in, float, list or tupple not '{type(x)}'")

    if 0 < len(x) < n + 1:
        x.extend([x[-1]] * (n - len(x)))
    else:
        raise ValueError(
            f"Wrong number of arguments. Expected up to {n}, got {len(x)}."
        )
    return x
