from .base import Session


class LocalSession(Session):
    def __init__(self, id: str):
        super().__init__(id=id, type="local", meta={})