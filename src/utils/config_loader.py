import yaml
from pathlib import Path

CONFIG_PATH = Path("configs/config.yaml")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    return config