import argparse
import datetime

def parse_datetime(s: str, default_to_end: bool) -> datetime.datetime:
    """
    Parse either a YYYY-MM-DD or a full ISO‐style YYYY-MM-DDTHH:MM:SS.
    If only a date is given, set time = 00:00:00 (default_to_end=False)
    or = 23:59:59 (default_to_end=True).
    """
    # try full timestamp first
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            pass

    # fall back to date only
    try:
        dt = datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date or datetime: {s!r}")
    
    if default_to_end:
        return dt.replace(hour=23, minute=59, second=59)
    else:
        return dt.replace(hour=0, minute=0, second=0)

def valid_start(s: str) -> datetime.datetime:
    return parse_datetime(s, default_to_end=False)

def valid_end(s: str) -> datetime.datetime:
    return parse_datetime(s, default_to_end=True)
