import yaml


def load_yaml(file_path):
    """YAML 파일 로더"""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
