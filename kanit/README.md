# Kanıt dosyaları

`data/resmi_gazete_sayilari.csv` listesindeki her tarihin dayandığı ham veriler. Hepsi gzip ile sıkıştırılmıştır
(`zcat dosya.gz | head` ya da Python'da `gzip.open(...)` ile okunur).

| Dosya | İçerik |
|---|---|
| `arsiv_pdf_ilk_sayfa.jsonl.gz` | 1921–2000 arşivinde denenen her dosya (`arsiv/<sayı>.pdf`, `<sayı>T.pdf`, `<sayı>_<k>.pdf`) için bir satır: `key`, `url`, `status` (`ok` / `404` / `error`), dosya boyutu, sayfa sayısı ve ilk sayfanın OCR metni (`text1`, metin kısaysa `text2`). 10 MB'ı aşan dosyalar `status: error` ve `maxContentLength` hatasıyla görünür. |
| `gunluk_sayfalar.json.gz` | 2000–2026 arasındaki her gün için resmigazete.gov.tr günlük sayfasından okunan künye, sayı numarası, "bugün yayımlanmamaktadır" bilgisi ve mükerrer sayfa (M1, M2 …) denemeleri. |
| `gorsel_okumalar.json.gz` | Görüntü olarak okunan 2.481 künyenin sonucu: basılı tarih, haftanın günü, sayı numarası, mükerrer ibaresi, güven düzeyi. |
| `arsiv_tarih_cozumleme.json.gz` | Arşiv sayıları için OCR adaylarından seçilen tarih, seçim yöntemi ve haftanın günü kontrolü. |
| `arsiv_kimlik_eslestirme.json.gz` | Her sayının hangi arşiv dosyasından geldiği (yanlış adlandırılmış dosyalar dahil). |
| `atiflar.json.gz` | TBMM kayıtlarından ve Resmî Gazete metinlerinden çıkarılan "tarih ve sayı" atıfları ile bunların listeyle karşılaştırma kararları. |
| `tbmm_kanunlar.jsonl.gz`, `tbmm_kararlar.jsonl.gz` | TBMM "Kanunlar ve Kararlar Erişim" veritabanından alınan ham kayıtlar (her kanun/karar numarası için bir satır). |
| `lexpera_gunluk.jsonl.gz` | 2014–2026 için Lexpera günlük Resmî Gazete listesi (çapraz kontrol). |
| `birlestirme_raporu.json.gz` | Son birleştirmenin raporu: eksik numara, sıra ihlali, kaynak çakışması kontrolleri ve tahmini tarihli sayıların olası aralıkları. |

Künye görüntüleri (her arşiv PDF'inin ilk sayfasının üst kısmı, ~24.500 PNG, ~915 MB) boyutları nedeniyle depoda yok;
her biri `https://www.resmigazete.gov.tr/arsiv/<sayı>.pdf` dosyasının ilk sayfasından yeniden üretilebilir.
