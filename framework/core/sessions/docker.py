from .base import Session


class DockerSession(Session):
    def __init__(self, id: str, image: str = "alpine:latest"):
        super().__init__(id=id, type="docker", meta={"image": image})