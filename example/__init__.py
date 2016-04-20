

def main():
    from lux.core import execute_from_config

    execute_from_config('example.%s.config',
                        description='Lux powered example',
                        services=('webalone', 'webapi', 'website'))
