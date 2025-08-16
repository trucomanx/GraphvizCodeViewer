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


# Lê o JSON no início do programa
def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(path,content):
    """
    Cria o arquivo JSON no caminho especificado com conteúdo padrão,
    criando diretórios intermediários se necessário.
    """

    # Garante que os diretórios existam
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

