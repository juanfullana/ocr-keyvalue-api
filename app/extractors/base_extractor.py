class BaseExtractor:

    def match(self, texto: str) -> bool:
        raise NotImplementedError

    def extract(self, texto: str) -> dict:
        raise NotImplementedError