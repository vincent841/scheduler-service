class ENSBackendManager:
    BACKEND_DICT = dict()

    @staticmethod
    def register(name: str, backend_data: dict):
        ENSBackendManager.BACKEND_DICT[name] = backend_data

    @staticmethod
    def get(name: str):
        return ENSBackendManager.BACKEND_DICT[name]
