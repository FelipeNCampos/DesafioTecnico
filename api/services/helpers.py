from datetime import datetime, timezone


def normalize_datetime(value=None):
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def iso_utc(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def clamp_pagination(page, per_page):
    page = max(int(page or 1), 1)
    per_page = max(min(int(per_page or 20), 100), 1)
    return page, per_page
