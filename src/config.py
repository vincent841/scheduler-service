import yaml
import os


class Config:
    CONFIG_DATA: dict = {}

    def __init__(self, config_yaml_file=None, config_data=None):
        Config.CONFIG_DATA: dict = {}
        try:
            if config_yaml_file:
                if not os.path.isfile(config_yaml_file):
                    config_yaml_file = "../config/config.yaml"

                with open(config_yaml_file) as config_file:
                    Config.CONFIG_DATA = yaml.load(config_file, Loader=yaml.FullLoader)
            elif config_data:
                Config.CONFIG_DATA = config_data
            else:
                raise Exception("No configuration data")

        except Exception as ex:
            Config.CONFIG_DATA = {}
            raise Exception("No configuration data found")

    @classmethod
    def get(cls, key):
        return cls.CONFIG_DATA.get(key, None)

    @classmethod
    def db(cls):
        try:
            config_data = cls.CONFIG_DATA.get("db")
            assert (
                config_data["host"]
                and config_data["port"]
                and config_data["id"]
                and config_data["pw"]
                and config_data["db"]
            )
        except Exception as ex:
            print(f"invalid configuration(db): \n{ex}")
            config_data = None

        return (
            (
                config_data["host"],
                config_data["port"],
                config_data["id"],
                config_data["pw"],
                config_data["db"],
            )
            if config_data != None
            else None
        )

    # deprecated
    @classmethod
    def eventbus(cls):
        try:
            backend_list = cls.CONFIG_DATA.get("eventbus")
            assert backend_list is not None
        except Exception as ex:
            print(f"invalid configuration(eventbus): \n{ex}")
            backend_list = None
        return backend_list

    @classmethod
    def evt_queue(cls):
        try:
            evt_q_name = cls.CONFIG_DATA.get("localqueue").get("evt_queue")
            assert type(evt_q_name) == str
        except Exception as ex:
            print(f"invalid configuration(evt_queue): \n{ex}")
            evt_q_name = ""
        return evt_q_name


if __name__ == "__main__":
    conf = Config("/Users/jinwonchoi/github/ms2postgres/config/config.yaml")
    print(Config.get("mssql"))
