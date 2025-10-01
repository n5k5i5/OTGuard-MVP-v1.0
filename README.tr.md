Lab Security Framework v1.0 (Türkçe)
====================================

[![CI](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml)
[![Publish](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/lab-sec-framework.svg)](https://pypi.org/project/lab-sec-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Diller: [English](README.en.md) | [Türkçe](README.tr.md) | [Русский](README.ru.md)

Güvenli ve laboratuvar odaklı bir güvenlik testi iskeleti. Sadece CLI, API yok. Güçlü guardrails, organizasyon onay kapısı (zorunlu), rapor üretiminde opsiyonel ikinci-faktör ve paketlenmiş örnek modüller ile gelir.

Hızlı başlangıç
- EULA kabul ve dil:
  - framework init --agree --lang tr
- Organizasyon onayı (zorunlu):
  - framework org init --name "ACME" --domain acme.com --email secops@acme.com
  - Token e-posta ile gelir (SMTP yoksa CLI’da yazdırılır)
  - framework org verify --token <TOKEN>
- Modülleri listele: framework modules list
- Örnek modül çalıştır (emüle):
  - framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'
- Raporlar (opsiyonel 2FA):
  - framework report gate-set
  - framework report show --last --report-token <TOKEN>
  - framework report index --report-token <TOKEN>

Kurulum
- PyPI (önerilen)
  1) (Opsiyonel) Sanal ortam:
     - python -m venv .venv && source .venv/bin/activate
     - Windows: py -m venv .venv; .\.venv\Scripts\Activate.ps1
  2) pip install lab-sec-framework
  3) framework --version
- Kaynaktan (geliştirme)
  - git clone https://github.com/your-org/lab-sec-framework.git
  - cd lab-sec-framework
  - python -m venv .venv && source .venv/bin/activate
  - pip install -e .
- pipx
  - pipx install lab-sec-framework

Organizasyon onayı (OrgGate)
- Core komutlar (modules/run/resource/report/sessions) öncesi zorunludur.
- Adımlar:
  1) framework org init --name "ACME" --domain acme.com --email secops@acme.com
  2) Token e-posta veya CLI ile alın
     - Tıklanabilir link (opsiyonel):
       - Dahili sunucu: framework org serve --host 0.0.0.0 --port 8080
       - ORG_VERIFY_BASE_URL=http://<host>:8080/verify
  3) framework org verify --token <TOKEN>
- Durum/Sıfırla:
  - framework org status
  - framework org reset --confirm
- Webhook (opsiyonel):
  - ORG_WEBHOOK_URL: init sırasında JSON payload gönderir

Rapor ikinci-faktör (ReportGate) – opsiyonel
- Etkinleştir:
  - framework report gate-set
- Kullan:
  - framework report show --last --report-token <TOKEN>
  - framework report index --report-token <TOKEN>
- Yönet:
  - framework report gate-status
  - framework report gate-disable

Temel komutlar
- framework modules list
- framework run <module> --with key=value
- framework resource run <path.yaml>
- framework report show --last | --run-id <id>
- framework report index
- framework sessions create --type local|docker [--image alpine:latest]
- framework sessions list | close <id>
- framework modules init custom.probe.demo --name "Demo Probe" --type probe

Dokümanlar
- Başlangıç: docs/getting-started.md
- Organizasyon onayı: docs/policy/org-approval.md
- Mimari: docs/architecture.md
- EULA: docs/EULA.md (EN/TR/RU)
- Özellikler: docs/features-tr.md

Diyagram ve ekran görüntüleri
- docs/media/README.md
- Mimari (Mermaid):

```mermaid
graph TD
  A[CLI (Typer)] --> B[Module Loader]
  A --> C[Resource Runner (DSL)]
  A --> D[Sessions (Local/Docker)]
  A --> E[Report Generator]
  A --> F[Metrics (JSON + SQLite)]
  A --> O[OrgGate / ReportGate]
  B --> G[Modules (manifests + code)]
  G --> H[Safety Guardrails]
  C --> G
  C --> F
  E --> I[.runs/ HTML]
  F --> J[.runs/metrics.db]
  D --> K[Docker Runtime]
```

Güvenlik
- Lab modu varsayılan olarak açıktır (public IP engeli). --unsafe sadece izole lab ve yetkili kullanımda.
- Örnek modüller emülasyonda çalışır.

Lisans
- MIT. Bkz. LICENSE.

Yol haritası
- ROADMAP.md ve docs/features-tr.md.