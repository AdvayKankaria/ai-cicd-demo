def generate_idempotency_key(user_id, timestamp):
    if not user_id or not timestamp:
        raise ValueError("Both user_id and timestamp are required")
    return f"{user_id}:{timestamp}"
