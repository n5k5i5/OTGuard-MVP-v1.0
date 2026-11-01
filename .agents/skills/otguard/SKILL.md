---
name: otguard
description: "OTGuard - Operational Technology & ICS/SCADA Security Testing Framework (Author: n5k5i5). Mimari, modül kataloğu, otomasyon DSL ve v2.0 yol haritası kılavuzu."
---

# 🛡️ OTGuard (v2.0) - Proje Mimarisi & Geliştirici Kılavuzu

> **Baş Geliştirici & Mimar:** `n5k5i5`  
> **Proje:** OTGuard (Operational Technology Security Testing & Automation Framework)  
> **Lisans:** MIT  
> **Hedef:** ICS / SCADA / DCS / PLC Lab Güvenlik Testleri ve Otomasyonu

---

## 1. OTGuard Nedir?

**OTGuard**, endüstriyel kontrol sistemleri (ICS), SCADA altyapıları, PLC/RTU kontrolörleri ve IoT/OT ağlarında **kontrollü laboratuvar ortamlarında** etik, güvenli ve otomatik denetimler koşturmak amacıyla **n5k5i5** tarafından geliştirilen **CLI tabanlı bir siber güvenlik test framework'üdür**.

### Temel Güvenlik Felsefesi (Guardrails & Lab-First)
1. **Zararsız ve Etik Test:** Canlı üretim hatlarında veya dış ağlarda (Public IP) kazara test yapılmasını engellemek için RFC1918 ve Loopback adres kısıtı vardır (`--unsafe` olmadan engellenir).
2. **Çok Dilli EULA:** İlk çalıştırmada Türkçe, İngilizce ve Rusça etik kullanım sözleşmesi onayı (`otguard init --agree`) gerektirir.
3. **Emülasyon Modu (Safe Emulation):** Modüller varsayılan olarak cihazlara zarar vermeyen sentetik/simüle edilmiş yanıtlar üretir; gerçek lab testleri için güvenli soket bağlantısı kurar.

---

## 2. Mimari ve Bileşenler

```
OTGuard/
├── framework/                 # Çekirdek Kütüphane
│   ├── cli/
│   │   └── main.py            # Typer CLI komutları (otguard run, modules, resource, sessions, report)
│   └── core/
│       ├── automation/        # ResourceRunner (Gelişmiş v2.0 YAML DSL motoru)
│       ├── metrics/           # Metrik toplayıcı (.runs/<id>.json)
│       ├── modules/           # Module SDK (BaseModule, Manifest, Loader)
│       ├── report/            # HTML & JSON rapor üretici
│       ├── safety/            # IP Guardrails & Güvenlik sınırları
│       └── sessions/          # Local & Docker test ortamı oturumları
├── modules/                   # Modül Ekosistemi
│   ├── ot/                    # Endüstriyel OT/ICS Modülleri
│   │   ├── probe_modbus/      # Modbus TCP (Port 502) Teşhis & Register Okuyucu
│   │   ├── probe_s7comm/      # Siemens S7comm / COTP (Port 102) PLC Keşfi
│   │   ├── probe_bacnet/      # BACnet/IP (UDP 47808) Bina Otomasyonu
│   │   └── audit_weak_creds/  # SCADA/HMI Standart Parola Denetleyicisi
│   ├── net/                   # Ağ & Web Arayüzü Modülleri
│   │   └── probe_http_banner/ # Endüstriyel Web & HMI Panel Tespiti
│   ├── utility/               # Yardımcı Modüller
│   │   └── export_transform/  # Sonuçları JSON/CSV formatında dışa aktarma
│   └── examples/              # Genel IT ve Örnek Modüller (Portscan, Sysinfo, Nmap)
├── resources/                 # Otomasyon Senaryoları (YAML)
│   ├── examples/quick_probe.yaml
│   └── examples/ot_security_assessment.yaml  # Kapsamlı OT Denetim Senaryosu
└── pyproject.toml             # Paket tanımlayıcısı (otguard komutu, yazar: n5k5i5)
```

---

## 3. Eklenen & Güncellenen Modüller Kataloğu

| Modül ID | Tip | Port / Protokol | Açıklama |
| :--- | :--- | :--- | :--- |
| `ot.probe.modbus` | Probe | TCP 502 (Modbus TCP) | Slave/Unit ID tespiti, Device Identification ve Holding Register okuma |
| `ot.probe.s7comm` | Probe | TCP 102 (ISO-on-TCP) | Siemens S7-300/400/1200/1500 COTP bağlantısı ve PLC fingerprinting |
| `ot.probe.bacnet` | Probe | UDP 47808 (BACnet/IP) | HVAC, yangın ve bina otomasyonu Who-Is cihaz keşfi |
| `net.probe.http_banner` | Probe | TCP 80, 443, 8080 | GoAhead, Siemens, WAGO, Schneider vb. HMI web panellerinin tespiti |
| `ot.audit.weak_creds` | Post/Audit | Çoklu (HTTP/Telnet vb.) | Endüstriyel varsayılan kullanıcı adı/parola denetimi (IEC 62443 uyumlu) |
| `util.transform.export` | Aux | Dosya Çıktısı | Değerlendirme bulgularını JSON veya CSV formatında kaydetme |

---

## 4. Resource DSL v2.0 Yetenekleri

`framework/core/automation/resource_runner.py` motoruna kazandırılan yeni v2.0 mantıksal operatörleri:

* **Sayısal Karşılaştırmalar:** `gt` (büyüktür), `lt` (küçüktür), `gte`, `lte`
* **Metin & Varlık:** `regex` (düzenli ifade eşleşmesi), `exists` (alan varlığı kontrolü)
* **Mantıksal Bağlaçlar:** `not`, `all` (ve), `any` (veya)

### Örnek v2.0 Senaryo Adımı:
```yaml
- when:
    all:
      - gt: ["${modbus_step.modbus_devices.127.0.0.1.port}", 500]
      - regex: ["Siemens|Schneider", "${hmi_step.http_banners.127.0.0.1.0.server}"]
  run:
    module: "ot.audit.weak_creds"
    with:
      targets: "${vars.targets}"
      vendor: "siemens"
```

---

## 5. Hızlı Başlangıç Komutları (CLI)

```bash
# 1. Projeyi düzenlenebilir modda kur
pip install -e .

# 2. OTGuard Etik Kullanım Sözleşmesini (EULA) kabul et
otguard init --agree --lang tr

# 3. Yüklü tüm modülleri listele (Modbus, S7, BACnet, HTTP Banner vb.)
otguard modules list

# 4. Modbus TCP taraması çalıştır (Lab / Emulate modu)
otguard run ot.probe.modbus --with targets=127.0.0.1 --with port=502

# 5. Siemens PLC S7comm keşfi çalıştır
otguard run ot.probe.s7comm --with targets=127.0.0.1

# 6. Kapsamlı OT Güvenlik Testi Senaryosunu Koştur
otguard resource run resources/examples/ot_security_assessment.yaml

# 7. Son koşunun HTML/konsol raporunu incele
otguard report show --last
```

---

## 6. Geliştirici & Güncelleme Yol Haritası (n5k5i5)

- [x] **Faz 1 (Tamamlandı):** Proje adı ve CLI girişinin `otguard` olarak güncellenmesi, `n5k5i5` yazar imzası.
- [x] **Faz 2 (Tamamlandı):** Endüstriyel OT protokol modüllerinin (Modbus, S7comm, BACnet, HMI Banner, Weak Creds, Export) yazılması.
- [x] **Faz 3 (Tamamlandı):** Resource Runner DSL motoruna v2.0 operatörlerinin (`gt`, `lt`, `regex`, `exists`, `all`, `any`, `not`) eklenmesi.
- [ ] **Faz 4 (Gelecek):** Docker tabanlı sanal SCADA laboratuvarı (`otguard lab up --profile conpot`) ve merkezi web trend paneli.
