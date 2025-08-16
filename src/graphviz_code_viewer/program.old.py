import os

import graphviz_code_viewer.about as about
import graphviz_code_viewer.modules.configure as configure 

# Caminho para o arquivo de configuração
CONFIG_PATH = os.path.join(os.path.expanduser("~"),".config",about.__package__,"config.json")

configure.verify_default_config(CONFIG_PATH, default_content={"casa":"verde"})

CONFIG=configure.load_config(CONFIG_PATH)
print("Hola!")
