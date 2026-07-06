def extract_points(text: str, point_symbol: str, points_map: dict):
    """
    Determine the number of point symbols at the beginning of a string and return
    the corresponding number of points.
    """
    if not text:
        return None

    symbol_count = len(text) - len(text.lstrip(point_symbol))
    return points_map.get(symbol_count)
