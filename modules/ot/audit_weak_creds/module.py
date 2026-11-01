from typing import Dict, Any, List
from framework.core.modules.base import Module


class WeakCredsAuditModule(Module):
    metadata = {
        "id": "ot.audit.weak_creds",
        "name": "OT / SCADA Default & Weak Credential Checker",
        "version": "1.0.0",
        "type": "post",
        "safety_level": "lab",
    }

    # Bilinen standart endüstriyel varsayılan kimlik bilgileri veritabanı (Lab auditing)
    DEFAULT_OT_CREDENTIALS = {
        "schneider": [("admin", "admin"), ("user", "user"), ("administrator", "Schneider")],
        "siemens": [("admin", "admin"), ("administrator", "1234"), ("user", "user")],
        "moxa": [("admin", "moxa"), ("admin", ""), ("user", "user")],
        "advantech": [("root", "000000"), ("admin", "admin"), ("root", "root")],
        "wago": [("admin", "wago"), ("user", "user")],
        "generic": [("admin", "admin"), ("admin", "1234"), ("root", "root"), ("admin", "password")],
    }

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.env: Dict[str, Any] = {}

    def validate(self, config: Dict[str, Any]) -> None:
        if "targets" not in config:
            raise ValueError("targets is required")
        targets = config["targets"]
        if isinstance(targets, str):
            targets = [targets]
        vendor = str(config.get("vendor", "generic")).lower()
        service = str(config.get("service", "http")).lower()
        self.config = {
            "targets": list(targets),
            "vendor": vendor,
            "service": service,
        }

    def prepare(self, env: Dict[str, Any]) -> None:
        self.env = env

    def execute(self, session=None) -> Dict[str, Any]:
        emulate = self.env.get("emulate", True)
        vendor = self.config["vendor"]
        pairs = self.DEFAULT_OT_CREDENTIALS.get(vendor, self.DEFAULT_OT_CREDENTIALS["generic"])
        findings: List[Dict[str, Any]] = []

        if emulate:
            for t in self.config["targets"]:
                findings.append({
                    "target": str(t),
                    "vendor": vendor,
                    "service": self.config["service"],
                    "status": "VULNERABLE (Default credentials active)",
                    "tested_pairs_count": len(pairs),
                    "matched_user": pairs[0][0],
                    "risk_level": "CRITICAL",
                    "remediation": "Change default vendor credentials immediately on the engineering station or web HMI.",
                })
            return {
                "audit_findings": findings,
                "vulnerable_count": len(findings),
                "emulated": True,
            }

        # Safe Lab Non-Destructive Check
        for t in self.config["targets"]:
            findings.append({
                "target": str(t),
                "vendor": vendor,
                "service": self.config["service"],
                "status": "Audited in lab mode (no brute-force applied without explicit safe target flag)",
                "tested_pairs_count": len(pairs),
                "matched_user": None,
                "risk_level": "INFO",
                "remediation": "Audit passwords against IEC 62443 standard.",
            })

        return {
            "audit_findings": findings,
            "vulnerable_count": 0,
            "emulated": False,
        }
