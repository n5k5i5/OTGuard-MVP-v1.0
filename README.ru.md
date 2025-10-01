Lab Security Framework v1.0 (Русский)
=====================================

[![CI](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/ci.yml)
[![Publish](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml/badge.svg)](https://github.com/your-org/lab-sec-framework/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/lab-sec-framework.svg)](https://pypi.org/project/lab-sec-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Языки: [English](README.en.md) | [Türkçe](README.tr.md) | [Русский](README.ru.md)

Безопасный каркас (шаблон) для модульного тестирования безопасности с приоритетом лабораторной среды. Только CLI (без API). Встроенные ограничения (guardrails), обязательное согласование организации (OrgGate), опциональный второй фактор для отчетов (ReportGate), примеры модулей.

Быстрый старт
- Принять EULA и выбрать язык:
  - framework init --agree --lang ru
- Подтверждение организации (обязательно):
  - framework org init --name "ACME" --domain acme.com --email secops@acme.com
  - Получите токен по почте (или в CLI, если SMTP не настроен)
  - framework org verify --token <TOKEN>
- Список модулей: framework modules list
- Запуск примера (эмуляция):
  - framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'
- Отчеты (опц. второй фактор):
  - framework report gate-set
  - framework report show --last --report-token <TOKEN>
  - framework report index --report-token <TOKEN>

Установка
- PyPI (рекомендуется)
  1) Необязательная виртуальная среда:
     - python -m venv .venv && source .venv/bin/activate
     - Windows: py -m venv .venv; .\.venv\Scripts\Activate.ps1
  2) pip install lab-sec-framework
  3) framework --version
- Из исходников (dev)
  - git clone https://github.com/your-org/lab-sec-framework.git
  - cd lab-sec-framework
  - python -m venv .venv && source .venv/bin/activate
  - pip install -e .
- pipx
  - pipx install lab-sec-framework

Согласование организации (OrgGate)
- Обязательно перед использованием основных команд (modules/run/resource/report/sessions).
- Шаги:
  1) framework org init --name "ACME" --domain acme.com --email secops@acme.com
  2) Получите токен по email или из CLI
     - Кликабельная ссылка (опционально):
       - Локальный HTTP-сервер: framework org serve --host 0.0.0.0 --port 8080
       - ORG_VERIFY_BASE_URL=http://<host>:8080/verify
  3) framework org verify --token <TOKEN>
- Статус/Сброс:
  - framework org status
  - framework org reset --confirm
- Вебхук (опционально):
  - ORG_WEBHOOK_URL: отправка JSON при инициации

Второй фактор для отчетов (ReportGate) — опционально
- Включить:
  - framework report gate-set
- Использовать:
  - framework report show --last --report-token <TOKEN>
  - framework report index --report-token <TOKEN>
- Управление:
  - framework report gate-status
  - framework report gate-disable

Основные команды
- framework modules list
- framework run <module> --with key=value
- framework resource run <path.yaml>
- framework report show --last | --run-id <id>
- framework report index
- framework sessions create --type local|docker [--image alpine:latest]
- framework sessions list | close <id>
- framework modules init custom.probe.demo --name "Demo Probe" --type probe

Документация
- Быстрый старт: docs/getting-started.ru.md
- Согласование организации: docs/policy/org-approval.ru.md
- Архитектура: docs/architecture.md
- EULA: docs/EULA.md (EN/TR/RU)
- Возможности: docs/features-ru.md

Диаграммы и скриншоты
- docs/media/README.md
- Архитектура (Mermaid):

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

Безопасность
- Режим «лаборатория» включен по умолчанию (блокируются публичные IP). --unsafe — только в изолированных лабораториях и с разрешения.
- Примерные модули работают в режиме эмуляции.

Лицензия
- MIT. См. LICENSE.

Дорожная карта
- ROADMAP.md и docs/features-ru.md.