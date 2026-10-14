import json
def encode_message(message):
    """Convert a Python dictionary to bytes for a UDP datagram."""
    return json.dumps(message, separators=(",", ":")).encode("utf-8")
def decode_message(raw):
    """Decode a UDP datagram and reject malformed/unknown messages."""
    try:
        message = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(message, dict):
        return None
    kind = message.get("type")
    if kind == "DATA":
        if not isinstance(message.get("run_id"), str):
            return None
        if not isinstance(message.get("seq"), int):
            return None
        if not isinstance(message.get("payload"), str):
            return None
        return message
    if kind == "ACK":
        if not isinstance(message.get("run_id"), str):
            return None
        if not isinstance(message.get("seq"), int):
            return None
        return message
    return None
