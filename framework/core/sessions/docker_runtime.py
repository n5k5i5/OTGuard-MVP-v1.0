import json
import shutil
import subprocess
from typing import Optional, Dict


def docker_available() -> bool:
    return shutil.which("docker") is not None


def run_container(image: str = "alpine:latest", command: Optional[str] = None, detach: bool = True) -> Dict[str, str]:
    if not docker_available():
        raise RuntimeError("Docker CLI not found. Please install Docker.")
    cmd = ["docker", "run"]
    if detach:
        cmd.append("-d")
    cmd += [image]
    if command:
        cmd += command.split()
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    container_id = res.stdout.strip()
    return {"container_id": container_id, "image": image}


def stop_container(container_id: str) -> None:
    if not docker_available():
        raise RuntimeError("Docker CLI not found. Please install Docker.")
    subprocess.run(["docker", "rm", "-f", container_id], check=False)