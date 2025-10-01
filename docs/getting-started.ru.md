# Быстрый старт (RU)

Этот фреймворк — безопасный каркас для модульного тестирования безопасности с приоритетом лабораторной среды. Только CLI, строгие ограничения и согласование организации (OrgGate).

## Предварительные требования
- Python 3.9+ (рекомендуется 3.11)
- Опционально: Docker (для docker-сессий)
- Опционально: virtualenv или pipx

## Установка

### 1) PyPI (рекомендуется)
```bash
# Опционально виртуальная среда
python -m venv .venv && source .venv/bin/activate   # Windows: py -m venv .venv; .\.venv\Scripts\Activate.ps1

# Установка
pip install lab-sec-framework

# Проверка
framework --version
```

### 2) Из исходников (dev)
```bash
git clone https://github.com/your-org/lab-sec-framework.git
cd lab-sec-framework
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .
framework --version
```

### 3) pipx
```bash
pipx install lab-sec-framework
framework --version
```

### Заметки для Windows
- Может потребоваться ExecutionPolicy:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
- Можно использовать `py -m pip` и `py -m venv`.

## Первый запуск (EULA и язык)
```bash
framework init --agree --lang ru
```
- Либо передайте `--agree --lang ru` в любую команду:
  ```bash
  framework modules list --agree --lang ru
  ```

## Согласование организации (обязательно)
Перед использованием основных команд завершите OrgGate.

1) Инициализация:
```bash
framework org init --name "ACME" --domain acme.com --email secops@acme.com
```
- При настроенном SMTP токен будет отправлен по email, иначе — показан в CLI.
- Опциональный вебхук: `ORG_WEBHOOK_URL` — получение JSON.

2) Кликабельная ссылка (опционально):
```bash
# Локальный HTTP-сервер подтверждения
framework org serve --host 0.0.0.0 --port 8080
```
- Установите `ORG_VERIFY_BASE_URL=http://<host>:8080/verify` для ссылки в письме.
- Ссылка: `http://<host>:8080/verify?token=<TOKEN>`

3) Подтверждение через CLI:
```bash
framework org verify --token <TOKEN>
```

4) Статус и сброс:
```bash
framework org status
framework org reset --confirm
```

### SMTP/Вебхук (опционально)
- SMTP_HOST, SMTP_PORT (по умолчанию 587)
- SMTP_USER, SMTP_PASS
- SMTP_FROM (по умолчанию SMTP_USER)
- SMTP_TLS (true/false; по умолчанию true)
- ORG_VERIFY_BASE_URL (опц.; добавляет ссылку в письме)
- ORG_WEBHOOK_URL (опц.; вебхук при init)

## Базовое использование
```bash
# Список модулей
framework modules list

# Пример (эмуляция)
framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'

# Автоматизация (Resource)
framework resource run resources/examples/quick_probe.yaml

# Отчеты (опц. второй фактор)
framework report gate-set
framework report show --last --report-token <TOKEN>
framework report index --report-token <TOKEN>

# Сессии (опционально)
framework sessions create --type local
framework sessions list
framework sessions close <id>
# Docker-сессия (спящий контейнер)
framework sessions create --type docker --image alpine:latest
```

## Resource DSL: цикл + условие
```yaml
version: "1"
name: "Loop Probe"
vars:
  targets: ["127.0.0.1", "127.0.0.2"]
steps:
  - set: { name: ports, value: [22, 80] }
  - foreach:
      list: "${vars.targets}"
      as: t
      do:
        - run:
            module: examples.probe.portscan
            with:
              targets: "${t}"
              ports: "${vars.ports}"
          as: "scan_${t}"
        - when: { contains: ["${scan_${t}.open_ports.${t}}", 80] }
          run:
            module: examples.post.sysinfo
          as: "sys_${t}"
```

## Обновление / Удаление
```bash
pip install -U lab-sec-framework
pip uninstall lab-sec-framework
deactivate
```

## Устранение неполадок
- Команда "framework" не найдена: проверьте виртуальную среду и PATH.
- Ошибки docker-сессии: проверьте `docker --version` и демон.
- JSON-параметры: корректные кавычки для `--with` (например, ports='[22,80,443]').

## Лицензия
- MIT. См. LICENSE.

## Безопасность
- Режим «лаборатория» включен по умолчанию (публичные IP блокируются).
- `--unsafe` используйте только в изолированных лабораториях и с разрешения.