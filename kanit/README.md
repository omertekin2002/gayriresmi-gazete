# Kanıt dosyaları

`data/resmi_gazete_sayilari.csv` listesindeki her tarihin dayandığı ham veriler. Hepsi gzip ile sıkıştırılmıştır
(`zcat dosya.gz | head` ya da Python'da `gzip.open(...)` ile okunur).

| Dosya | İçerik |
|---|---|
| `arsiv_pdf_ilk_sayfa.jsonl.gz` | 1921–2000 arşivinde denenen her dosya (`arsiv/<sayı>.pdf`, `<sayı>T.pdf`, `<sayı>_<k>.pdf`) için bir satır: `key`, `url`, `status` (`ok` / `404` / `error`), dosya boyutu, sayfa sayısı ve ilk sayfanın OCR metni (`text1`, metin kısaysa `text2`). 10 MB'ı aşan dosyalar `status: error` ve `maxContentLength` hatasıyla görünür. İlk taramada paralel indirme sırasında yanlış numarayla eşleşmiş olabilecek 106 dosya sonradan tek tek yeniden indirildi; bu kayıtlarda `sirali_yeniden_indirme: true` yazar ve eski kaydın yerini alır. |
| `gunluk_sayfalar.json.gz` | 2000–2026 arasındaki her gün için resmigazete.gov.tr günlük sayfasından okunan künye, sayı numarası, "bugün yayımlanmamaktadır" bilgisi ve mükerrer sayfa (M1, M2 …) denemeleri. |
| `gorsel_okumalar.json.gz` | Görüntü olarak okunan 2.486 künyenin sonucu: basılı tarih, haftanın günü, sayı numarası, mükerrer ibaresi, güven düzeyi. |
| `arsiv_tarih_cozumleme.json.gz` | Arşiv sayıları için OCR adaylarından seçilen tarih, seçim yöntemi ve haftanın günü kontrolü. |
| `arsiv_kimlik_eslestirme.json.gz` | Her sayının ve mükerrer nüshasının hangi arşiv dosyasından geldiği (dosyalar künyede basılı sayıyla karşılaştırıldı; yanlış adlandırılmış dosya bulunmadı). |
| `kunye_duzeltmeleri.json.gz` | Künyesi tek tek incelenen sayıların kararları: basılı gün rakamı hatalı ya da kırık 2 sayının (8489, 14490) tarihi ve gerekçesi; gün adı tarihle tutmayan 7 künyenin (54, 77, 207, 259, 494, 635, 18223) ve 588 sayının mükerrerinin açıklaması. |
| `atiflar.json.gz` | TBMM kayıtlarından ve Resmî Gazete metinlerinden çıkarılan "tarih ve sayı" atıfları ile bunların listeyle karşılaştırma kararları. |
| `tbmm_kanunlar.jsonl.gz`, `tbmm_kararlar.jsonl.gz` | TBMM "Kanunlar ve Kararlar Erişim" veritabanından alınan ham kayıtlar (her kanun/karar numarası için bir satır). |
| `lexpera_gunluk.jsonl.gz` | 2014–2026 için Lexpera günlük Resmî Gazete listesi (çapraz kontrol). |
| `yerel_okumalar.jsonl.gz` | (`scripts/yerel_tamamla.py uygula` çalıştırıldıktan sonra oluşur) 10 MB'tan büyük PDF'lerin yerel bilgisayarda okunan künyeleri, görsel okumalar ve her kalem için verilen karar. |
| `birlestirme_raporu.json.gz` | Son birleştirmenin raporu: eksik numara, sıra ihlali, kaynak çakışması kontrolleri ve tahmini tarihli sayıların olası aralıkları. |

Künye görüntüleri (her arşiv PDF'inin ilk sayfasının üst kısmı, ~24.500 PNG, ~915 MB) boyutları nedeniyle depoda yok;
her biri `https://www.resmigazete.gov.tr/arsiv/<sayı>.pdf` dosyasının ilk sayfasından yeniden üretilebilir.
