from lux.core import LuxExtension


class Extension(LuxExtension):
    '''{{ project_name }} extension
    '''
    def middleware(self, app):
        return []


def main():
    from lux.core import execute_from_config

    execute_from_config('{{ project_name }}.config')
