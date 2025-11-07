def truncate_string(string: str, length: int) -> str:
    return string[:(length - 3)] + '...' if len(string) > length else string