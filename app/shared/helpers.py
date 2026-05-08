SENSITIVE_KEYS = {"password", "token", "api_key", "secret", "card", "document"}


def mask_sensitive_data(payload: dict) -> dict:
    masked = {}
    for key, value in payload.items():
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
            masked[key] = "***"
        else:
            masked[key] = value
    return masked

