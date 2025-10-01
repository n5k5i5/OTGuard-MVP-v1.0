# Başlangıç: İndirme, Kurulum ve Kullanım (TR)

Bu proje, güvenli ve laboratuvar odaklı bir güvenlik testi iskeletidir. CLI ağırlıklı çalışır, modülerdir ve güçlü koruma (guardrails) sağlar.

## Önkoşullar
- Python 3.9+ (öneri: 3.11)
- (Opsiyonel) Docker — Docker oturumları için
- (Opsiyonel) virtualenv veya pipx

## İndirme ve Kurulum

### 1) PyPI'den kurulum (önerilen)
```bash
# (Opsiyonel) Sanal ortam
python -m venv .venv && source .venv/bin/activate   # Windows: py -m venv .venv; .\.venv\Scripts\Activate.ps1

# Kurulum
pip install lab-sec-framework

# Doğrulama
framework --version
```

### 2) Kaynaktan (geliştirme)
```bash
git clone https://github.com/your-org/lab-sec-framework.git
cd lab-sec-framework
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -e .
framework --version
```

### 3) pipx ile (kullanıcı başına izole kurulum)
```bash
pipx install lab-sec-framework
framework --version
```

### Windows notları
- PowerShell ExecutionPolicy gerekebilir:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
- Python erişimi: `py -m pip` ve `py -m venv` kullanılabilir.

## İlk kullanım (EULA ve dil)
```bash
# EULA kabulü ve dil seçimi (en|tr|ru)
framework init --agree --lang tr
```
- Alternatif: Komutlara `--agree --lang tr` ekleyerek tek seferde onaylayabilirsiniz.
  ```bash
  framework modules list --agree --lang tr
  ```

## Organizasyon onayı (zorunlu)
Sistemin kullanılabilmesi için şirket/organizasyon onayı gerekir.

1) Organizasyonu başlat:
```bash
framework org init --name "ACME" --domain acme.com --email secops@acme.com
```
- SMTP yapılandırıldıysa onay e-postası gönderilir.
- SMTP yoksa token CLI’da gösterilir (manuel paylaşım için).
- (Opsiyonel) Webhook bildirimi: `ORG_WEBHOOK_URL` ayarlanırsa JSON POST ile bilgilendirme yapılır.

2) Tıklanabilir link ile doğrulama (opsiyonel):
```bash
# Dahili doğrulama HTTP sunucusu
framework org serve --host 0.0.0.0 --port 8080
```
- E-postaya link eklemek için `ORG_VERIFY_BASE_URL` ortam değişkenini `http://<host>:8080/verify` olarak ayarlayın.
- Link: `http://<host>:8080/verify?token=<TOKEN>`

3) Token ile doğrulama (CLI):
```bash
framework org verify --token <TOKEN>
```

4) Durumu görüntüleme ve sıfırlama:
```bash
framework org status
framework org reset --confirm
```

### SMTP/Webhook yapılandırması (opsiyonel)
Aşağıdaki ortam değişkenlerini ayarlayın:
- SMTP_HOST, SMTP_PORT (varsayılan 587)
- SMTP_USER, SMTP_PASS
- SMTP_FROM (varsayılan SMTP_USER)
- SMTP_TLS (true/false; varsayılan true)
- ORG_VERIFY_BASE_URL (opsiyonel; e-postaya doğrulama linki ekler)
- ORG_WEBHOOK_URL (opsiyonel; webhook bildirimi)

## Temel kullanım
```bash
# Modülleri listele
framework modules list

# Örnek modül çalıştır (emülasyon)
framework run examples.probe.portscan --with targets=127.0.0.1 --with ports='[22,80,443]'

# Resource betiği çalıştır (otomasyon)
framework resource run resources/examples/quick_probe.yaml

# Raporlar
# (Opsiyonel) İkinci-faktör koruması
framework report gate-set            # token üretir ve gösterir
framework report gate-status         # durum
framework report gate-disable        # devre dışı

# Rapor üretimi
framework report show --last --report-token <TOKEN>
framework report index --report-token <TOKEN>

# Oturumlar (opsiyonel)
framework sessions create --type local
framework sessions list
framework sessions close <id>
# Docker oturumu (uyuyan konteyner başlatır)
framework sessions create --type docker --image alpine:latest
```

## Resource DSL: döngü + koşul örneği
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

## Güncelleme ve Kaldırma
```bash
# Güncelleme (PyPI)
pip install -U lab-sec-framework

# Kaldırma
pip uninstall lab-sec-framework

# Sanal ortamı kapatma
deactivate
```

## Sorun giderme
- “framework” komutu bulunamıyorsa:
  - Sanal ortam aktif mi? PATH ayarları doğru mu?
- Docker oturumu hataları:
  - `docker --version` ile kurulum ve daemon kontrolü.
- JSON parametreleri:
  - `--with` için JSON biçimi ve tırnaklara dikkat (ör. ports='[22,80,443]').

## Lisans
- MIT License. Bkz. LICENSE

## Güvenlik
- Lab modu varsayılan olarak açıktır (genel IP’ler engellenir).
- `--unsafe` sadece izole lab ve yetkili kullanımda tercih edilmelidir.