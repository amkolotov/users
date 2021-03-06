import pathlib
import yaml

BASE_DIR = pathlib.Path(__file__).parent
config_path = BASE_DIR / 'config' / 'my_app.yaml'


def get_config(path):
    with open(path) as f:
        conf = yaml.safe_load(f)
    return conf


config = get_config(config_path)



