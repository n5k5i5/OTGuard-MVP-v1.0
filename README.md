Lab Security Framework v1.0
===========================

[![CI](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml)
[![Publish](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/lab-sec-framework.svg)](https://pypi.org/project/lab-sec-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A safe, modular, lab-first security testing framework scaffold that focuses on
developer experience, automation, and governance. Ships with non-operational
example modules and strong guardrails. CLI-only. No API is exposed.

Quick start
- Install: pip install -e .
- Accept EULA: framework init --agree
- Version: framework --version
- List modules: framework modules list
- Run a module:
  framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'
- Run a resource:
  framework resource run resources/examples/quick_probe.yaml
- Show last report:
  framework report show --last
- Generate runs index:
  framework report index
- Manage sessions:
  framework sessions create --type local
  framework sessions list
  framework sessions close <id>
  framework sessions create --type docker --image alpine:latest   # requires Docker
- Scaffold a new module:
  framework modules init custom.probe.demo --name "Demo Probe"

Özellikler (TR)
- Mevcut ve v2.0 planı için ayrıntılar: docs/features-tr.md

İndirme, Kurulum ve Kullanım (TR)
- PyPI'den kurulum (önerilen):
  1) Sanal ortam (opsiyonel ama önerilir)
     - Linux/Mac: python -m venv .venv && source .venv/bin/activate
     - Windows (PowerShell): py -m venv .venv; .\.venv\Scripts\Activate.ps1
  2) Kurulum: pip install lab-sec-framework
  3) Doğrulama: framework --version
- Kaynaktan (geliştirme modu):
  1) git clone https://github.com/your-org/lab-sec-framework.git
  2) cd lab-sec-framework
  3) python -m venv .venv && source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
  4) pip install -e .
- pipx ile (izole kullanıcı kurulumları için):
  - pipx install lab-sec-framework
  - framework --version

İlk kullanım ve EULA
- EULA kabulü ve dil seçimi (en|tr|ru):
  - framework init --agree --lang tr
- Alternatif: Her komutta --agree ve --lang verilebilir
  - framework modules list --agree --lang tr

Organizasyon onayı (zorunlu)
- Sistem kullanımı öncesi şirket/organizasyon onayı gerekir. Adımlar:
  1) Organizasyon başlat: framework org init --name "ACME" --domain acme.com --email secops@acme.com
  2) Onay e-postasındaki doğrulama kodunu (token) alın
     - SMTP yapılandırılmadıysa token CLI’da gösterilir (manuel paylaşım)
  3) Doğrulama: framework org verify --token <TOKEN>
- Durumu görüntüle: framework org status
- Sıfırlama (gerekirse): framework org reset --confirm

SMTP yapılandırması (opsiyonel; e-posta göndermek için)
- Ortam değişkenleri:
  - SMTP_HOST, SMTP_PORT (varsayılan 587), SMTP_USER, SMTP_PASS, SMTP_FROM, SMTP_TLS (true/false)

Temel komutlar
- Modül listeleme: framework modules list
- Örnek modül çalıştırma (emüle): framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'
- Resource (otomasyon) çalıştırma: framework resource run resources/examples/quick_probe.yaml
- Raporlar:
  - Son rapor: framework report show --last
  - Tüm çalıştırmaların indeksi: framework report index
- Oturumlar:
  - Oluştur: framework sessions create --type local
  - Docker (opsiyonel): framework sessions create --type docker --image alpine:latest
  - Listele/Kapat: framework sessions list / framework sessions close <id>
- Modül şablonu:
  - framework modules init custom.probe.demo --name "Demo Probe" --type probe

Güncelleme/Kaldırma
- Güncelleme (PyPI): pip install -U lab-sec-framework
- Kaldırma: pip uninstall lab-sec-framework
- Geliştirme modundan çıkış: deactivate (sanal ortamı kapatır)

Windows notları
- PowerShell'de sanal ortam aktivasyonu için ExecutionPolicy gerekebilir:
  - Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
- Python erişimi: py -V, pip yerine py -m pip kullanılabilir.

Sorun giderme
- Komut bulunamadı:
  - Sanal ortam aktif mi? PATH ayarları doğru mu?
- Docker oturum hatası:
  - docker --version ile kurulum doğrulayın; Docker daemon çalışıyor olmalı.
- JSON parametreleri:
  - --with anahtarları için tırnak ve JSON biçimine dikkat (ör. ports='[22,80,443]').

Görseller (Screenshots & Diagrams)
- Aşağıdaki Mermaid diyagramları GitHub üzerinde otomatik render edilir. PNG/JPG ekran görüntülerini `docs/media/images/` içine koyup README’de referanslayın (örnekler aşağıda).
- Ayrıntılar ve yönergeler: docs/media/README.md

```mermaid
%% Architecture (inline)
graph TD
  A[CLI (Typer)] --> B[Module Loader]
  A --> C[Resource Runner (DSL)]
  A --> D[Sessions (Local/Docker)]
  A --> E[Report Generator]
  A --> F[Metrics (JSON + SQLite)]
  B --> G[Modules (manifests + code)]
  G --> H[Safety Guardrails]
  C --> G
  C --> F
  E --> I[.runs/ HTML]
  F --> J[.runs/metrics.db]
  D --> K[Docker Runtime]
```

Screenshots (add your images under docs/media/images/)
- ![CLI Modules List](docs/media/images/cli-modules-list.png)
- ![Resource Run](docs/media/images/resource-run.png)
- ![Report Index](docs/media/images/report-index.png)

Publishing (GitHub & PyPI)
- GitHub Release:
  1) Bump version in pyproject.toml and CHANGELOG.md
  2) Create a tag (e.g., v1.0.0) and push
  3) Publish a GitHub Release from the tag
- PyPI Publish:
  - Configure repository secrets:
    - PYPI_API_TOKEN: PyPI token with publish rights
  - On publishing a GitHub Release, the workflow .github/workflows/publish.yml builds and uploads to PyPI

Roadmap: v2.0 (Coming)
- Resource DSL: regex/exists, gt/lt, any/all; retry, timeout, continue_on_error; parallel foreach
- Reporting: templated module summaries, aggregate dashboard, multi-run trends, JSON/CSV exports
- Sessions/Lab: Docker logs/exec/copy, network isolation presets, lab profiles, session-aware modules
- Governance: policy.yaml (allowed modules/params), unsafe justification logs, trust model (signing/pinning)
- Modules: HTTP/DNS/WHOIS probes, banner grab, JSON/CSV transforms, Nmap runner + richer parse
- DX/Test: typed config (pydantic), completions, contract tests, debug/trace mode
- Performance: parallel engine, caching, streaming large results
- DevOps: release-drafter, PyPI OIDC trusted publishing, optional Homebrew/binaries

See full roadmap: ROADMAP.md

Safety
- Lab mode is ON by default (blocks public IPs). Use --unsafe to override in a lab environment only.
- Example modules run in emulate mode by default.

License
- MIT License. See LICENSE file.

Docs
- docs/getting-started.md
- docs/module-dev-guide.md
- docs/architecture.md
- docs/policy/org-approval.md
- docs/EULA.md (EN/TR/RU)

Changelog
- See CHANGELOG.md for release notes.