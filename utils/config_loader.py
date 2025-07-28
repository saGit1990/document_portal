import yaml 

# load configuration,
def load_config(file_path:str = './config/config.yaml') -> dict:
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    return config


if __name__=="__main__":
    config = load_config()
    print(config)