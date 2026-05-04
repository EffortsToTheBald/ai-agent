from utils.path_tool import get_absolute_path
from utils.logger_handler import logger
from utils.config_handler import prompts_config

def load_prompt(config_key: str,logger_key:str):
    try:
        file_path = get_absolute_path(prompts_config[config_key])
        print(f"[{logger_key}] loading prompt from {file_path}")
    except Exception as e:
        logger.error(f"[{logger_key}] there is not config key named {config_key} in prompts.yaml")
        raise e
    try:
        return open(file_path, 'r', encoding='utf-8').read()
    except Exception as e:
        logger.error(f"[{logger_key}] failed to load prompt from {file_path}, error: {str(e)}")
        raise e


def load_rag_prompt():
    return load_prompt('rag_summarize_prompt_path','load_rag_summarize_prompt')  

def load_system_prompt():
    return load_prompt('main_prompt_path','load_system_prompt')    

def load_report_prompt():
    return load_prompt('report_prompt_path','load_report_prompt')


if __name__ == "__main__":
    # print(load_rag_prompt())
    # print(load_system_prompt())
    print(load_report_prompt())