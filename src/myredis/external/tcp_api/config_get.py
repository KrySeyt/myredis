def config_get(key, args) -> bytes:
    val = getattr(args, key)
    return f"*2\r\n${len(key)}\r\n{key}\r\n${len(str(val))}\r\n{val}\r\n".encode("utf-8")
