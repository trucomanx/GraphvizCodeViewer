import os
import json

def verify_default_config(path,default_content={}):
    """
    Cria o arquivo JSON no caminho especificado com conteúdo padrão,
    criando diretórios intermediários se necessário.
    """

    # Se o arquivo não existir, cria com o conteúdo padrão
    if not os.path.exists(path):
        # Garante que os diretórios existam
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, ensure_ascii=False, indent=4)



def merge_defaults(config, defaults):
    """
    Adiciona valores de defaults que não existam em config.
    Funciona recursivamente para dicionários aninhados.
    """
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
        elif isinstance(value, dict) and isinstance(config[key], dict):
            merge_defaults(config[key], value)
    return config

# Lê o JSON no início do programa
def load_config(config_path, default_content=None):
    """
    Carrega o JSON de configuração e preenche com valores padrão se necessário.
    """
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                print("Erro ao ler config, usando defaults")
                config = {}

    if default_content:
        config = merge_defaults(config, default_content)

    return config

def save_config(path,content):
    """
    Cria o arquivo JSON no caminho especificado com conteúdo padrão,
    criando diretórios intermediários se necessário.
    """

    # Garante que os diretórios existam
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

