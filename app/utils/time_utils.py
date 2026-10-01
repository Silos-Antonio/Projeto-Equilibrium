import os
from datetime import datetime
from zoneinfo import ZoneInfo


APP_TIMEZONE = ZoneInfo(
    os.getenv('APP_TIMEZONE', 'America/Sao_Paulo')
)


def agora_local():
    return datetime.now(APP_TIMEZONE).replace(tzinfo=None)