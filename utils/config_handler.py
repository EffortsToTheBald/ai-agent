import yaml
from utils.path_tool import get_absolute_path

def load_config(config_path,encoding='utf-8'):
    '''
    load yaml config file
    '''
    with open(config_path, 'r', encoding=encoding) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


rag_config = load_config(get_absolute_path('config/rag.yaml'))
chroma_config = load_config(get_absolute_path('config/chroma.yaml'))
agent_config = load_config(get_absolute_path('config/agent.yaml'))
prompts_config = load_config(get_absolute_path('config/prompts.yaml'))