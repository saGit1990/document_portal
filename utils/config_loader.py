import yaml 

# load configuration,
def load_config(file_path:str = './config/config.yaml') -> dict:
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config

def load_config_extensions(file_path:str = './config/extension_config.yaml') -> list:
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config.get('extension_loader_map', [])

# hello dev
if __name__=="__main__":
    config = load_config_extensions()
    print(config)