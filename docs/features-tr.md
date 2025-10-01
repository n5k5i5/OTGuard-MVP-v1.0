# Özellikler (TR)

Bu proje, güvenli ve laboratuvar odaklı bir güvenlik testi iskeletidir (CLI-only). Aşağıda mevcut yetenekler ve v2.0 ile planlanan özellikler listelenmiştir.

## Mevcut (v1.0)

- Modüler mimari ve modül SDK'sı
  - Manifest + Python sınıfı ile modül geliştirme
  - Örnek modüller (lab-safe): Port Taraması, Sistem Bilgisi, Nmap XML içe aktarma
- Otomasyon (Resource DSL)
  - YAML tabanlı adımlar, değişkenler, koşullar (when), döngüler (foreach)
  - Basit şablonlama/interpolasyon
- Raporlama ve metrikler
  - Çalıştırma başına JSON/HTML rapor
  - Çalıştırma indeksi (.runs/index.html)
- Oturum yönetimi (stub)
  - Yerel ve Docker tabanlı oturumlar
- Güvenlik ve yönetişim
  - EULA (EN/TR/RU) onay akışı
  - Guardrails: Lab modu ve public IP blokajı
- Paketleme ve dağıtım
  - PyPI/GitHub yayın iş akışları, paket içine gömülü örnek modüller
- Dokümantasyon
  - Başlangıç rehberi, mimari, modül geliştirme kılavuzu

## v2.0 ile Planlananlar

Aşağıdaki maddeler v2.0 kapsamındaki hedef yeteneklerdir (geliştirme planına tabidir).

- ✅ Ağ Keşfi: OT cihazlarını otomatik tespit
  - Güvenli keşif modülleri, protokol tanıma (lab-only); ağ profilleri
- ✅ Zafiyet Analizi: CVSS tabanlı risk değerlendirme
  - NVD/NIST feed içe aktarma, CVSS hesaplama ve rapor özetleri
- ✅ Raporlama: Çok formatlı rapor üretimi
  - HTML/JSON yanında PDF/CSV dışa aktarma; modül bazlı özet şablonları
- ✅ Veritabanı: SQLite tabanlı veri saklama
  - Kalıcı sonuçlar/oturumlar; sorgulanabilir çalışma geçmişi
- ✅ CLI & GUI: İkili arayüz desteği
  - CLI mevcut; GUI (yerel, lab-only) planlı
- ✅ Loglama: Kapsamlı log sistemi
  - Yapılandırılabilir seviyeler, JSON log, audit iyileştirmeleri
- ✅ Türkçe UI: Yerelleştirilmiş arayüz
  - CLI çıktıları ve GUI metinleri için TR yerelleştirme

Not
- Bu özelliklerin bir kısmı henüz uygulanmamıştır. Durum güncellemeleri ve öncelikler için ROADMAP.md ve CHANGELOG.md dosyalarına bakınız.