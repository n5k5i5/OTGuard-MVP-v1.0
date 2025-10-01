# Organizasyon Onay Kapısı (OrgGate)

Bu mekanizma, yazılımın kullanılmasından önce şirket/organizasyon bilgisinin girilmesini ve yetkili bir kişinin açık onay vermesini zorunlu kılar. Amaç; etik, yasal ve yetkilendirilmiş kullanımın güvence altına alınmasıdır.

## Nasıl Çalışır?

- CLI üzerinden `framework org init` ile bir organizasyon kaydı başlatılır:
  - Zorunlu alanlar: `--name`, `--domain`, `--email`
  - Bir doğrulama belirteci (token) üretilir ve SHA-256 özeti `.runs/org.json` içinde saklanır.
  - SMTP yapılandırılmışsa e-posta ile token gönderilir; değilse token CLI’da yazdırılır.
  - (Opsiyonel) Webhook bildirimi: `ORG_WEBHOOK_URL` ayarlıysa JSON payload ile bir web kancasına bildirim yapılır.

- Onaylı kişi `framework org verify --token <TOKEN>` komutunu çalıştırarak onayı tamamlar.
  - (Opsiyonel) Tıklanabilir bağlantı:
    - E-posta içinde link istiyorsanız `ORG_VERIFY_BASE_URL` ortam değişkenini `http(s)://<host>:<port>/verify` olarak ayarlayın.
    - Ardından aşağıdaki dahili HTTP sunucuyu çalıştırın:
      ```bash
      framework org serve --host 0.0.0.0 --port 8080
      ```
    - E-postaya `http://<host>:8080/verify?token=<TOKEN>` linki eklenir.
  - Onaylandıktan sonra `status: "verified"` olur ve sistem komutları kullanılabilir.

- Durum görüntüleme ve sıfırlama:
  - `framework org status` → mevcut kayıt bilgisi (token özeti maskelenir).
  - `framework org reset --confirm` → kaydı sıfırlar.

## Zorunluluk ve Kapsam

- EULA kabulünden sonra, sistemde `org verify` tamamlanmadan core komutlar (modules, run, resource, report, sessions vb.) engellenir.
- İzinli komutlar: `help`, `init`, `org *`, `about`.

## SMTP ve Webhook Yapılandırması (opsiyonel)

SMTP için ortam değişkenleri:
- SMTP_HOST, SMTP_PORT (varsayılan 587)
- SMTP_USER, SMTP_PASS
- SMTP_FROM (varsayılan SMTP_USER)
- SMTP_TLS (`true|false`, varsayılan `true`)
- ORG_VERIFY_BASE_URL (opsiyonel; e-postaya tıklanabilir doğrulama linki ekler)

Webhook için:
- ORG_WEBHOOK_URL (opsiyonel; JSON POST ile token bildirimi)

SMTP ayarlanmadıysa, token e-posta ile gidemez; CLI üzerinde gösterilir ve manuel paylaşım yapılabilir.

## Veri Saklama

- `.runs/org.json`: Organizasyon kaydı ve hash’lenmiş token bilgisi.
- Gizlilik: `token_hash` dışa aktarımlarda maskelenir.

## Güvenlik Notları

- Token gizli tutulmalıdır. Yanlış ellerde yetkisiz onay verilmesine yol açabilir.
- SMTP ve webhook kimlik bilgilerini güvenli bir şekilde (ör. env/secret manager) saklayın.
- Bu kapı, **fail-closed** yaklaşımıyla tasarlanmıştır: Onay olmadan kritik komutlar çalışmaz.