import re
import socket
import ssl
import urllib.request
from typing import Dict, Any, List

from framework.core.modules.base import Module


class HttpBannerProbeModule(Module):
    metadata = {
        "id": "net.probe.http_banner",
        "name": "Industrial Web & HMI Banner Grabber",
        "version": "1.0.0",
        "type": "probe",
        "safety_level": "lab",
    }

    KNOWN_OT_SERVERS = [
        "goahead", "simatic", "siemens", "wago", "schneider",
        "codesys", "moxa", "advantech", "omron", "rockwell"
    ]

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.env: Dict[str, Any] = {}

    def validate(self, config: Dict[str, Any]) -> None:
        if "targets" not in config:
            raise ValueError("targets is required")
        targets = config["targets"]
        if isinstance(targets, str):
            targets = [targets]
        ports = config.get("ports", [80, 443, 8080])
        if isinstance(ports, int):
            ports = [ports]
        timeout = float(config.get("timeout", 1.5))
        self.config = {
            "targets": list(targets),
            "ports": [int(p) for p in ports],
            "timeout": timeout,
        }

    def prepare(self, env: Dict[str, Any]) -> None:
        self.env = env

    def _extract_title(self, html: str) -> str:
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else ""

    def execute(self, session=None) -> Dict[str, Any]:
        emulate = self.env.get("emulate", True)
        results: Dict[str, Any] = {}

        if emulate:
            for t in self.config["targets"]:
                results[str(t)] = [
                    {
                        "port": 80,
                        "url": f"http://{t}:80",
                        "status": 200,
                        "server": "GoAhead-Webs (Embedded ICS HMI)",
                        "title": "SIMATIC S7-1200 Station Overview",
                        "is_potential_ot": True,
                    }
                ]
            return {"http_banners": results, "emulated": True}

        # Ignore self-signed certificates in lab environment
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        timeout = self.config["timeout"]

        for t in self.config["targets"]:
            host_findings: List[Dict[str, Any]] = []
            for p in self.config["ports"]:
                proto = "https" if p in (443, 8443) else "http"
                url = f"{proto}://{t}:{p}"
                req = urllib.request.Request(url, headers={"User-Agent": "OTGuard-Probe/1.0"})
                try:
                    with urllib.request.urlopen(req, timeout=timeout, context=ctx if proto == "https" else None) as resp:
                        status = resp.status
                        headers = dict(resp.headers)
                        server = headers.get("Server", "Unknown")
                        body = resp.read(2048).decode("utf-8", errors="ignore")
                        title = self._extract_title(body)
                        is_ot = any(sig in (server + " " + title).lower() for sig in self.KNOWN_OT_SERVERS)
                        host_findings.append({
                            "port": p,
                            "url": url,
                            "status": status,
                            "server": server,
                            "title": title,
                            "is_potential_ot": is_ot,
                        })
                except Exception:
                    pass

            results[str(t)] = host_findings

        return {"http_banners": results, "emulated": False}
