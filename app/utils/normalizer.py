import re


def normalizar_telefone(telefone):
    if not telefone:
        return None

    telefone_normalizado = re.sub(
        r'\D',
        '',
        telefone
    )

    return telefone_normalizado or None