import os
from datetime import datetime
from zoneinfo import ZoneInfo


APP_TIMEZONE = ZoneInfo(
    os.getenv('APP_TIMEZONE', 'America/Sao_Paulo')
)


def agora_local():
    return datetime.now(APP_TIMEZONE).replace(tzinfo=None)

def para_timestamp_ms(data_hora):
    if data_hora.tzinfo is None:
        data_hora = data_hora.replace(
            tzinfo=APP_TIMEZONE
        )
    else:
        data_hora = data_hora.astimezone(
            APP_TIMEZONE
        )

    return int(data_hora.timestamp() * 1000)