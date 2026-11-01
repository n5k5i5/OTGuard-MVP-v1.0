# 🛡️ OTGuard - Operational Technology & ICS/SCADA Security Testing Framework

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Author](https://img.shields.io/badge/Author-n5k5i5-orange.svg)](https://github.com/n5k5i5)
[![Status](https://img.shields.io/badge/Status-v2.0--dev-brightgreen.svg)]()
[![Lab Safe](https://img.shields.io/badge/Mode-Lab--First%20%2F%20Non--Destructive-success.svg)]()

> **Lead Developer & Architect:** [`n5k5i5`](https://github.com/n5k5i5)  
> **OTGuard**, endüstriyel kontrol sistemleri (**ICS**), **SCADA** altyapıları, **PLC/RTU** üniteleri ve bina otomasyonu ağlarında **kontrollü laboratuvar ortamlarında** güvenli, zararsız (non-destructive) ve otomatik güvenlik denetimleri koşturmak amacıyla geliştirilmiş yeni nesil bir CLI framework'üdür.

---

## 📌 Neden OTGuard?

Geleneksel IT güvenlik tarama araçları (Nmap, agresif fuzzer'lar vb.), hassas endüstriyel donanımların (PLC, DCS, RTU) kilitlenmesine, beklenmedik yeniden başlatmalara veya fiziksel kesintilere yol açabilir. 

**OTGuard**, **"Lab-First & Safety Guardrails"** felsefesiyle tasarlanmıştır:
* 🛑 **Ağ Koruması (Guardrails):** Yanlışlıkla canlı veya dış ağlara (Public IP) paket gitmesini varsayılan olarak engeller. Sadece RFC1918 ve Loopback adreslere izin verir (`--unsafe` açıkça belirtilmedikçe engelleme kalkmaz).
* 🧪 **Güvenli Emülasyon Modu (Safe Emulation):** Modüller varsayılan olarak fiziksel donanıma dokunmadan simülatif/sentetik test çalıştırır. Gerçek laboratuvar modunda ise sadece standart OT protokol el sıkışmalarını kullanır.
* 📜 **Etik Kullanım Taahhüdü (EULA):** 3 dilde (TR/EN/RU) yasal ve etik kullanım onayı olmadan çalışmaz.

---

## ⚡ Desteklenen OT Protokolleri & Modül Ekosistemi

OTGuard, modüler bir SDK altyapısına sahiptir. `modules/` altında yerleşik olarak gelen başlıca modüller:

| Modül | Tip | Port / Protokol | Açıklama |
| :--- | :--- | :--- | :--- |
| **`ot.probe.modbus`** | Probe | TCP 502 (Modbus TCP) | Slave/Unit ID tespiti, Device Identification ve Holding Register okuma |
| **`ot.probe.s7comm`** | Probe | TCP 102 (ISO-on-TCP) | Siemens S7-300/400/1200/1500 COTP bağlantısı ve PLC donanım tespiti |
| **`ot.probe.bacnet`** | Probe | UDP 47808 (BACnet/IP) | HVAC, aydınlatma ve bina otomasyon cihazları için Who-Is keşfi |
| **`net.probe.http_banner`** | Probe | TCP 80, 443, 8080 | GoAhead, Siemens, WAGO, Schneider vb. endüstriyel HMI/Web panelleri |
| **`ot.audit.weak_creds`** | Post | Çoklu | Standart PLC/SCADA fabrika çıkışı varsayılan kimlik bilgisi denetimi |
| **`util.transform.export`** | Aux | Dosya Çıktısı | Değerlendirme sonuçlarını JSON veya CSV formatında kaydetme |
| **`examples.probe.portscan`** | Probe | TCP Çoklu | Hızlı lab port tarayıcısı |

---

## 🧩 Otomasyon Motoru: Resource DSL v2.0

OTGuard, karmaşık test adımlarını deklaratif YAML dosyalarıyla zincirlemenizi sağlar. v2.0 ile gelen zengin mantıksal operatörler:

* **Sayısal Karşılaştırmalar:** `gt` (>), `lt` (<), `gte` (>=), `lte` (<=)
* **Desen & Varlık:** `regex` (düzenli ifade eşleme), `exists` (alan kontrolü)
* **Mantıksal Bağlaçlar:** `all` (ve), `any` (veya), `not` (değil)
* **Döngüler & Değişkenler:** `foreach`, `vars.*`, dinamik string interpolation (`${scan.open_ports}`)

### Örnek Senaryo (`resources/examples/ot_security_assessment.yaml`):
```yaml
version: "1"
name: "OT & ICS Security Comprehensive Assessment"
vars:
  targets: ["192.168.1.50"]
steps:
  - run:
      module: "ot.probe.modbus"
      with:
        targets: "${vars.targets}"
        port: 502
    as: "modbus_step"

  - when:
      regex: ["Siemens|Schneider", "${modbus_step.modbus_devices.192.168.1.50.vendor}"]
    run:
      module: "ot.audit.weak_creds"
      with:
        targets: "${vars.targets}"
        vendor: "schneider"
    as: "audit_step"

  - report:
      include: ["modbus_step", "audit_step"]
```

---

## 🚀 Hızlı Başlangıç

### 1. Kurulum
```bash
git clone https://github.com/n5k5i5/OTGuard.git
cd OTGuard
pip install -e .
```

### 2. Etik Kullanım Sözleşmesini (EULA) Onaylama
```bash
# Türkçe onaylamak için:
otguard init --agree --lang tr

# İngilizce onaylamak için:
otguard init --agree --lang en
```

### 3. Modülleri Listeleme
```bash
otguard modules list
```

### 4. Tekil Modül Çalıştırma
```bash
# Modbus TCP taraması (Laboratuvar modu)
otguard run ot.probe.modbus --with targets=127.0.0.1 --with port=502

# Siemens PLC S7comm keşfi
otguard run ot.probe.s7comm --with targets=127.0.0.1
```

### 5. Kapsamlı OT Denetim Senaryosunu Koşturma
```bash
otguard resource run resources/examples/ot_security_assessment.yaml
```

### 6. Rapor Görüntüleme
```bash
# Son koşunun özetini göster
otguard report show --last

# Tüm koşu geçmişi indeksini oluştur
otguard report index
```

---

## 🛡️ Güvenlik Politikası & Lab Kısıtlamaları

* **Lab Mode:** Varsayılan olarak açıktır (`--lab`). Sadece `127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12` ve `192.168.0.0/16` hedeflerine izin verilir.
* **Unsafe Override:** Eğer izole edilmiş özel bir siber poligon veya laboratuvarda public IP bloğu kullanılıyorsa, açıkça `--unsafe` bayrağı ile çalıştırılmalıdır.

---

## 🗺️ Yol Haritası (Roadmap v2.0)

- [x] **v2.0-dev1:** OTGuard markalama dönüşümü (`n5k5i5`)
- [x] **v2.0-dev1:** Modbus TCP, Siemens S7comm, BACnet/IP, Industrial Web HMI modülleri
- [x] **v2.0-dev1:** Resource DSL v2.0 (Sayısal, mantıksal ve regex operatörleri)
- [ ] **v2.0-dev2:** Docker tabanlı sanal SCADA laboratuvarı (`otguard lab up --profile conpot`)
- [ ] **v2.0-dev3:** İnteraktif HTML/SVG zafiyet ve ağ topolojisi görselleştirme panosu

---

## 📄 Lisans & Katkı

Bu proje **MIT Lisansı** ile lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına göz atabilirsiniz.

Geliştirici: **[`n5k5i5`](https://github.com/n5k5i5)**