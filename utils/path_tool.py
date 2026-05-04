'''
project root path tool
'''

import os

def get_project_root() -> str:
    '''
    get project root path
    '''
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_absolute_path(relative_path: str) -> str:
    '''
    get absolute path from relative path
    '''
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)