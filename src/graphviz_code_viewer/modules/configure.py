import os
import json


def merge_defaults(config, defaults):
    """
    Adiciona valores de defaults que não existam em config.
    Funciona recursivamente para dicionários aninhados.
    """
    changed = False

    for key, value in defaults.items():
        if key not in config:
            config[key] = value
            changed = True
        elif isinstance(value, dict) and isinstance(config[key], dict):
            if merge_defaults(config[key], value):
                changed = True

    return changed


def verify_default_config(path, default_content=None):
    """
    Garante que o arquivo JSON exista e contenha todas as chaves
    definidas em default_content.
    Se faltar alguma chave, adiciona com valor padrão.
    """
    if default_content is None:
        default_content = {}

    # Garante que os diretórios existam
    os.makedirs(os.path.dirname(path), exist_ok=True)

    config = {}

    # Se o arquivo existir, tenta carregar
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print("Arquivo corrompido. Recriando com defaults.")
            config = {}
    else:
        print("Arquivo não existe. Criando com defaults.")

    # Verifica e adiciona chaves faltantes
    changed = merge_defaults(config, default_content)

    # Se arquivo não existia ou houve mudança, salva
    if not os.path.exists(path) or changed:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    return config


def load_config(config_path, default_content=None):
    """
    Carrega o JSON de configuração garantindo defaults.
    """
    return verify_default_config(config_path, default_content)


def save_config(path, content):
    """
    Cria o arquivo JSON no caminho especificado com conteúdo padrão,
    criando diretórios intermediários se necessário.
    """

    # Garante que os diretórios existam
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

