DROUGHT_LEVEL_ORDER = {
    "mild": 0,
    "moderate": 1,
    "severe": 2,
    "extreme": 3,
}


def drought_level_sort_key(drought_level: str) -> int:
    """
    Return a numeric sort key for drought levels.

    Unknown drought levels are placed after known levels.
    """
    return DROUGHT_LEVEL_ORDER.get(drought_level, 999)
