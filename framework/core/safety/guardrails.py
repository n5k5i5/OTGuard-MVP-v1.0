import ipaddress
from typing import Dict, Any


class SafetyGuard:
    def validate_inputs(self, manifest: Dict[str, Any], inputs: Dict[str, Any], unsafe: bool = False) -> None:
        # simple guard: block non-RFC1918 targets unless unsafe
        targets = inputs.get("targets")
        if targets is None:
            return
        if not isinstance(targets, (list, tuple)):
            targets = [targets]
        for t in targets:
            try:
                ip = ipaddress.ip_address(str(t))
            except ValueError:
                # not an IP, skip
                continue
            if unsafe:
                continue
            if not (ip.is_private or ip.is_loopback):
                raise PermissionError(f"Target {t} is not private or loopback. Use --unsafe to override.")