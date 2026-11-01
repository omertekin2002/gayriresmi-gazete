# Gayriresmî Gazete

T.C. Resmî Gazete'nin bugüne kadar yayımlanmış **bütün sayılarının** kronolojik listesi:
7 Şubat 1921'de *Ceride-i Resmiye* adıyla çıkan 1 numaralı sayıdan, 1 Kasım 2026 tarihli 33417 sayılı Resmî Gazete'ye kadar.

| | |
|---|---|
| Toplam yayın | **35.422** |
| Asıl sayı (1 → 33417, numara atlanmadan) | **33.417** |
| Mükerrer sayı | **2.005** |
| İlk sayı | 7 Şubat 1921 — *Ceride-i Resmiye*, Sayı 1 |
| Son sayı | 1 Kasım 2026 — Sayı 33417 |
| Liste tarihi | 1 Kasım 2026 |

## Dosyalar

| Dosya | İçerik |
|---|---|
| [`data/resmi_gazete_sayilari.csv`](data/resmi_gazete_sayilari.csv) | Tüm yayınlar, tarih → sayı → mükerrer sırasıyla |
| [`data/resmi_gazete_sayilari.json`](data/resmi_gazete_sayilari.json) | Aynı liste, JSON |
| [`data/yillik_ozet.csv`](data/yillik_ozet.csv) | Yıl başına asıl/mükerrer sayısı, yılın ilk ve son sayı numarası |
| [`data/dogrulama_raporu.json`](data/dogrulama_raporu.json) | Tutarlılık kontrollerinin sonuçları |
| [`data/resmi_site_duzeltmeleri.json`](data/resmi_site_duzeltmeleri.json) | Resmî sitenin günlük sayfalarında bulunup düzeltilen sayı numarası hataları |
| [`scripts/`](scripts/) | Verileri toplamak, ayrıştırmak ve birleştirmek için kullanılan betikler |

### CSV kolonları

| Kolon | Açıklama |
|---|---|
| `sira` | Kronolojik sıra (1'den başlar) |
| `tarih` | Yayım tarihi (YYYY-AA-GG, Miladi) |
| `gun` | Haftanın günü |
| `sayi` | Resmî Gazete sayı numarası |
| `mukerrer` | `0` = asıl sayı, `1` = 1. mükerrer, `2` = 2. mükerrer … |
| `yayin_adi` | `Ceride-i Resmiye` (1–21), `Resmî Ceride` (22–762), `T.C. Resmî Gazete` (763 →) |
| `url` | resmigazete.gov.tr üzerindeki kaynak (arşiv PDF'i ya da günlük sayfa) |
| `tarih_kaynagi` | Tarihin nereden alındığı (aşağıya bakın) |
| `not` | Düzeltme, belirsizlik veya arşivdeki tutarsızlıklarla ilgili açıklama |

## Yöntem

Tüm sayılar **resmigazete.gov.tr** üzerinden tek tek tarandı; site Türkiye dışından doğrudan erişime kapalı olduğu için
indirmeler bir web-getirme aracı üzerinden yapıldı.

**1921 – Haziran 2000 (Sayı 1 – 24095): arşiv PDF'leri.** Her sayı numarası için `arsiv/<sayı>.pdf` indirildi
(ilk 1053 sayı için günümüz Türkçesine aktarılmış `arsiv/<sayı>T.pdf`), ardından `arsiv/<sayı>_1.pdf`, `_2.pdf` …
denenerek mükerrer nüshalar arandı. Tarih, PDF'in ilk sayfasındaki künyeden okundu:

- OCR metninden tarih adayları çıkarıldı (eski ay adları — *Teşrinievvel, Kânunusani, Birincikânun* … — ve 1336–1341
  Rumi yılları dahil). Künyedeki **haftanın günü** ile tutan ve sayı sırasıyla çelişmeyen aday seçildi
  (sayı numarası arttıkça tarih geriye gidemez).
- OCR'ın kesin bir tarih vermediği 1.833 sayının künyesi görüntü olarak okundu. Okunan tarih, ancak basılı sayı
  numarası ve haftanın günü de tutuyorsa kabul edildi.
- **Bağımsız denetim:** OCR ile tarihlendirilmiş sayılardan rastgele seçilen 210 sayı ayrıca görsel olarak okundu;
  209'u birebir tuttu, 1'i düşük güvenle okunduğu için kabul edilmedi (hatalı tarih çıkmadı).

**Haziran 2000 – bugün (Sayı 24092 → 33417): günlük sayfalar.** 9.624 günün her biri için
`eskiler/YYYY/AA/YYYYAAGG.htm` sayfası ve `...M1.htm`, `M2.htm` … mükerrer sayfaları kontrol edildi.

**Çapraz kontrol.** 2014–2026 için Lexpera'nın günlük Resmî Gazete listesi ayrıca tarandı: asıl sayıların tarih ve
numaraları resmî siteyle birebir aynı çıktı; resmî sitede Lexpera'da olmayan 20 mükerrer bulundu, Lexpera'daki tek
fazlalık (15.03.2018 tarihli "30363 1. Mükerrer") hatalı kayıt olduğu için listeye alınmadı. 2000 yılındaki örtüşme
aralığında (24092–24095 ve mükerrerleri) arşiv PDF'lerinden okunan tarihler günlük sayfalarla aynı.

### `tarih_kaynagi` değerleri

| Değer | Adet | Anlamı |
|---|---:|---|
| arşiv PDF künyesi (OCR + haftanın günü kontrolü) | 21.984 | Arşiv PDF'inin künyesi; OCR + haftanın günü + sıra kontrolü |
| resmî site günlük sayfası | 10.545 | resmigazete.gov.tr günlük sayfası (`eskiler/…htm`), 27.06.2000 sonrası |
| arşiv PDF künyesi (görsel okuma) | 1.833 | Arşiv PDF'inin künyesi görüntü olarak okundu |
| asıl sayının tarihi | 785 | Mükerrer nüsha; asıl sayıyla aynı gün |
| komşu sayılardan tahmin (kesin değil) | 249 | PDF indirilemedi/okunamadı; olası aralık `not` kolonunda |
| aynı sayının mükerrer nüshasının künyesi | 23 | Asıl sayının PDF'i okunamadı; aynı numaralı mükerrerin künyesinden |
| komşu sayılardan kesin çıkarım | 3 | Önceki ve sonraki sayılardan tek bir tarih mümkün |

## Resmî kaynaktaki tutarsızlıklar

Tarama sırasında resmî sitenin kendisinde bazı hatalar bulundu; listede doğru değerler kullanıldı ve `not` kolonunda
açıklandı:

- **Günlük sayfalarda yanlış sayı numarası:** ör. 18.11.2000 sayfasında *24334* yazıyor (doğrusu 24234, çünkü önceki gün
  24233, sonraki gün 24235); 22.01.2001 sayfasında *29425* (doğrusu 24295); 04.05.2001 ve 28.11.2003'te bir önceki sayının
  numarası tekrarlanmış. 29.10.2002 sayfasında bir numara görünse de o gün gazete yayımlanmamış.
- **Arşivde yanlış adlandırılmış PDF'ler:** bazı dosyalar başka bir sayının künyesini taşıyor. Ör. `17639.pdf` aslında
  17640'ı, `17640.pdf` 17641'i, `17641.pdf` 17639'u içeriyor; Aralık 1997'de `23207_1.pdf` → 23208, `23208_1.pdf` → 23209
  asıl sayıları; `14001_1.pdf` ise 14003'ün mükerreri. Bu dosyalar künyede basılı sayıya göre doğru yere yerleştirildi
  (OCR ve görsel okuma aynı sayıda uyuşmadıkça dosya adına güvenildi).

## Bilinen sınırlamalar

- **249 sayının tarihi tahminidir** (`tarih_kaynagi = komşu sayılardan tahmin`). Bunların büyük kısmının arşivdeki
  PDF'i 10 MB'tan büyük olduğu için indirilemedi; tarih, önceki ve sonraki sayıların tarihleri arasında doğrusal olarak
  tahmin edildi ve `not` kolonunda en erken / en geç olası tarih verildi. Bunların 185'inde önceki ve sonraki sayı
  arasında yalnızca tek bir gün boşluk var.
- 1921–2000 dönemindeki mükerrerler arşivdeki `_1`, `_2` … dosyalarından bulundu; arşive hiç yüklenmemiş bir mükerrer
  varsa listede yoktur. 10 MB'ı aşan mükerrer dosyalarının varlığı sunucu yanıtından (dosya var ama çok büyük) anlaşıldı.
- İlk dönemin (1921–1928) günümüz Türkçesine aktarılmış nüshalarında birkaç künyede tarih ile haftanın günü birbirini
  tutmuyor; bu sayılarda basılı tarih kullanıldı ve not düşüldü.
- Resmî Gazete'nin yayımlanmadığı günler (bayramlar, bazı resmî tatiller) listede doğal olarak yer almaz.

## Yeniden üretme

`scripts/` dizinindeki betikler bu listeyi üretmek için kullanıldı:

| Betik | Görev |
|---|---|
| `rg_ingest.py` | İndirilen arşiv PDF'inden ilk sayfa metnini ve künye görüntüsünü çıkarır |
| `rgdate.py` | Gürültülü OCR metninden tarih, haftanın günü ve sayı adaylarını çıkarır |
| `resolve_era1.py` | Arşiv sayılarına, sıralama ve haftanın günü kısıtlarıyla tarih atar |
| `identity.py` | Dosyaları künyede basılı sayıya göre eşleştirir (arşivdeki yanlış adlandırmalar için) |
| `parse_era2.py` | Günlük sayfa sonuçlarını normalize eder, ardışıklık kontrolü yapar |
| `lexpera_scrape.py`, `parse_era3.py` | Lexpera çapraz kontrolü |
| `merge.py`, `build_outputs.py` | Kaynakları birleştirir, doğrular ve `data/` dosyalarını yazar |

Türkiye içinden resmigazete.gov.tr'ye doğrudan erişilebiliyorsa, tahmini tarihli sayıların PDF'leri `curl` ile
indirilip `rg_ingest.py` ve `resolve_era1.py` ile kesinleştirilebilir.

---

*Bu proje resmî değildir; T.C. Cumhurbaşkanlığı İdari İşler Başkanlığı Hukuk ve Mevzuat Genel Müdürlüğü ile ilgisi yoktur.
Resmî Gazete'nin kendisi için [resmigazete.gov.tr](https://www.resmigazete.gov.tr) adresine başvurun.*
