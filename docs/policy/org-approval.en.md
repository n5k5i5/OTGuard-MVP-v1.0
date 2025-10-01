# Organization Approval Gate (OrgGate)

This mechanism enforces that company/organization details are provided and an authorized approver explicitly verifies access before the system can be used. It ensures lawful, ethical, and authorized usage.

## How it works

- Initialize via `framework org init`:
  - Required fields: `--name`, `--domain`, `--email`
  - A verification token is generated and the SHA-256 hash is stored in `.runs/org.json`.
  - If SMTP is configured, an email is sent; otherwise, the token is printed to the CLI.
  - Optional webhook: if `ORG_WEBHOOK_URL` is set, a JSON payload is posted to the webhook.

- Approver verifies:
  - `framework org verify --token <TOKEN>`
  - Optional clickable link:
    - Run local HTTP server:
      ```bash
      framework org serve --host 0.0.0.0 --port 8080
      ```
    - Set `ORG_VERIFY_BASE_URL=http://<host>:8080/verify` to embed the link into emails.

- Status/Reset:
  - `framework org status` → shows current record (token hash is masked).
  - `framework org reset --confirm` → clears the record.

## Enforcement

- After EULA acceptance, core commands (modules, run, resource, report, sessions, etc.) are blocked until OrgGate is verified.
- Allowed commands pre-verification: `help`, `init`, `org *`, `about`.

## SMTP / Webhook

- SMTP environment variables:
  - `SMTP_HOST`, `SMTP_PORT` (default 587), `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM` (default `SMTP_USER`), `SMTP_TLS` (default `true`)
  - `ORG_VERIFY_BASE_URL` (optional; clickable link in emails)
- Webhook:
  - `ORG_WEBHOOK_URL` (optional; JSON POST notification on init)

## Data storage

- `.runs/org.json`: organization record and token hash.
- `token_hash` is masked in status output.

## Security notes

- Keep tokens confidential to prevent unauthorized approvals.
- Store SMTP/webhook credentials securely (env/secret manager).
- Fail-closed by design: without approval, critical commands are blocked.