# Gayriresmî Gazete

T.C. Resmî Gazete'nin bugüne kadar yayımlanmış **bütün sayılarının** kronolojik listesi:
7 Şubat 1921'de *Ceride-i Resmiye* adıyla çıkan 1 numaralı sayıdan, {SON} tarihli {SON_SAYI} sayılı Resmî Gazete'ye kadar.

| | |
|---|---|
| Toplam yayın | **{TOPLAM}** |
| Asıl sayı (1 → {SON_SAYI}, numara atlanmadan) | **{ASIL}** |
| Mükerrer sayı | **{MUK}** |
| İlk sayı | 7 Şubat 1921 — *Ceride-i Resmiye*, Sayı 1 |
| Son sayı | {SON} — Sayı {SON_SAYI} |
| Liste tarihi | {OLUSTURMA} |

## Dosyalar

| Dosya | İçerik |
|---|---|
| [`data/resmi_gazete_sayilari.csv`](data/resmi_gazete_sayilari.csv) | Tüm yayınlar, tarih → sayı → mükerrer sırasıyla |
| [`data/resmi_gazete_sayilari.json`](data/resmi_gazete_sayilari.json) | Aynı liste, JSON |
| [`data/yillik_ozet.csv`](data/yillik_ozet.csv) | Yıl başına asıl/mükerrer sayısı, yılın ilk ve son sayı numarası |
| [`data/dogrulama_raporu.json`](data/dogrulama_raporu.json) | Tutarlılık kontrollerinin sonuçları |
| [`data/resmi_site_duzeltmeleri.json`](data/resmi_site_duzeltmeleri.json) | Resmî sitenin günlük sayfalarında bulunup düzeltilen sayı numarası hataları |
| [`data/tbmm_rg_atiflari.csv`](data/tbmm_rg_atiflari.csv) | TBMM kayıtlarındaki her kanun ve Meclis kararının yayımlandığı Resmî Gazete tarihi ve sayısı (karşılaştırmada kullanıldı) |
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
- OCR'ın kesin bir tarih vermediği {GORSEL} sayının künyesi görüntü olarak okundu. Okunan tarih, ancak basılı sayı
  numarası ve haftanın günü de tutuyorsa kabul edildi.
- **Bağımsız denetim:** OCR ile tarihlendirilmiş sayılardan rastgele seçilen 210 sayı ayrıca görsel olarak okundu;
  209'u birebir tuttu, 1'i düşük güvenle okunduğu için kabul edilmedi (hatalı tarih çıkmadı).

**Haziran 2000 – bugün (Sayı 24092 → {SON_SAYI}): günlük sayfalar.** {GUN_SAYISI} günün her biri için
`eskiler/YYYY/AA/YYYYAAGG.htm` sayfası ve `...M1.htm`, `M2.htm` … mükerrer sayfaları kontrol edildi.

**Çapraz kontrol.** 2014–2026 için Lexpera'nın günlük Resmî Gazete listesi ayrıca tarandı: asıl sayıların tarih ve
numaraları resmî siteyle birebir aynı çıktı; resmî sitede Lexpera'da olmayan 20 mükerrer bulundu, Lexpera'daki tek
fazlalık (15.03.2018 tarihli "30363 1. Mükerrer") hatalı kayıt olduğu için listeye alınmadı. 2000 yılındaki örtüşme
aralığında (24092–24095 ve mükerrerleri) arşiv PDF'lerinden okunan tarihler günlük sayfalarla aynı.

**Bağımsız atıflarla doğrulama.** Liste, sayıların tarihini taşıyan iki bağımsız kaynakla karşılaştırıldı:

- **TBMM kanun ve karar kayıtları.** TBMM'nin eski "Kanunlar ve Kararlar Erişim" veritabanında, 1920'den bu yana çıkan
  her kanunun ve Meclis kararının hangi tarih ve sayılı Resmî Gazete'de yayımlandığı yazılı.
  {TBMM_SAYI} sayı numarası için bu kayıtlar var. Bunların {TBMM_AYNI} tanesinde tarih bizimkiyle birebir aynı.
  Farklı görünen {TBMM_FARK} kaydın {TBMM_TYPO} tanesi TBMM kaydındaki tek haneli yazım hatası (sayı ya da tarih), {TBMM_IMKANSIZ} tanesi
  sayı sırasıyla bağdaşmayan tarih veriyor. Sıraya sığan 9 vakada künye yeniden okundu ya da resmî günlük sayfa
  kontrol edildi; hepsinde bizim tarihimiz doğru çıktı.
- **Resmî Gazete'nin kendi metinlerindeki atıflar.** "… tarihli ve … sayılı Resmî Gazete'de yayımlanan" kalıbındaki
  atıflar, 2019–2026 Resmî Gazete tam metin derleminden ([moganai/turkish-resmi-gazete](https://huggingface.co/datasets/moganai/turkish-resmi-gazete))
  ve arşiv PDF'lerinin ilk sayfalarından çıkarıldı: {HF_SAYI} sayıya yapılan atıfların {HF_AYNI} tanesi bizim tarihimizle aynı;
  kalan {HF_FARK} uyuşmazlığın {HF_IMKANSIZ} tanesi sayı sırasıyla bağdaşmayan bir tarih veriyor (atıf metnindeki yazım hatası
  ya da başka bir belgeye ait numara), biri ise resmî günlük sayfanın tarihiyle çelişen bir yazım hatası.

PDF'i indirilemeyen sayıların tarihi bu atıflardan kesinleştirildi: {TBMM_COZ} sayı TBMM kayıtlarından, {RG_COZ} sayı Resmî
Gazete metinlerindeki atıflardan (atıf yalnızca komşu sayıların izin verdiği tarih aralığına düşüyorsa kabul edildi).

### `tarih_kaynagi` değerleri

| Değer | Adet | Anlamı |
|---|---:|---|
{KAYNAK_TABLO}

## Resmî kaynaktaki tutarsızlıklar

Tarama sırasında resmî sitenin kendisinde bazı hatalar bulundu; listede doğru değerler kullanıldı ve `not` kolonunda
açıklandı:

- **Günlük sayfalarda yanlış sayı numarası:** ör. 18.11.2000 sayfasında *24334* yazıyor (doğrusu 24234, çünkü önceki gün
  24233, sonraki gün 24235); 22.01.2001 sayfasında *29425* (doğrusu 24295); 04.05.2001 ve 28.11.2003'te bir önceki sayının
  numarası tekrarlanmış. 29.10.2002 sayfasında bir numara görünse de o gün gazete yayımlanmamış.
- **Künyede basılı yanlış gün:** 14490 sayılı gazetenin künyesinde "23 Mart 1973 Çarşamba" basılı; ancak 23 Mart 1973
  cumadır, 14486 sayı zaten 24 Mart tarihlidir ve 14489 (27 Mart) ile 14491 (29 Mart) arasında tek gün kalır: sayı
  28 Mart 1973 çarşamba günü çıkmıştır. 8489 sayının künyesindeki gün rakamı baskıda kırık ("21" gibi görünüyor);
  künyedeki "Pazartesi" ve komşu sayılar 24 Ağustos 1953'ü verir.

Resmî arşivde (`arsiv/*.pdf`) yanlış adlandırılmış dosya bulunmadı. Taramanın ilk aşamasında aynı anda birden çok
dosya indirildiği için bazı dosyalar yanlış sayı numarasıyla eşleştirilmişti. Bundan şüphelenilen her dosya (106 dosya)
sonradan tek tek yeniden indirildi ve listede yalnızca bu doğrulanmış dosyalar kullanıldı.

## Bilinen sınırlamalar

- **{TAHMIN} sayının tarihi hâlâ tahminidir** (`tarih_kaynagi = komşu sayılardan tahmin`). Bunların arşivdeki PDF'i
  10 MB'tan büyük olduğu için indirilemedi ve başka bir kaynakta tarihli atıfları bulunamadı; tarih, önceki ve sonraki
  sayıların tarihleri arasında doğrusal olarak tahmin edildi ve `not` kolonunda en erken / en geç olası tarih verildi.
  Bunların {TAHMIN_2GUN} tanesinde önceki ve sonraki sayı arasında yalnızca tek bir gün boşluk var. Türkiye içinden
  `python3 scripts/kesinlestir_tahminler.py data/resmi_gazete_sayilari.csv kesinlesen.csv` komutu bu PDF'leri doğrudan
  indirip künyeden tarihlerini çıkarır.
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
| `identity.py` | Dosyaları künyede basılı sayıya göre eşleştirir (indirme sırasında yanlış numarayla eşleşen dosyaları yakalamak için) |
| `parse_era2.py` | Günlük sayfa sonuçlarını normalize eder, ardışıklık kontrolü yapar |
| `lexpera_scrape.py`, `parse_era3.py` | Lexpera çapraz kontrolü |
| `tbmm_citations.py`, `mine_citations.py`, `citations.py`, `adjudicate.py` | TBMM kayıtlarından ve metinlerden tarih–sayı atıflarını toplar, listeyle karşılaştırır |
| `merge.py`, `build_outputs.py` | Kaynakları birleştirir, doğrular ve `data/` dosyalarını yazar |
| `kesinlestir_tahminler.py` | Tahmini tarihli sayıların PDF'lerini (Türkiye içinden) indirip tarihlerini kesinleştirir |

Türkiye içinden resmigazete.gov.tr'ye doğrudan erişilebiliyorsa, tahmini tarihli sayıların PDF'leri `curl` ile
indirilip `rg_ingest.py` ve `resolve_era1.py` ile kesinleştirilebilir.

---

*Bu proje resmî değildir; T.C. Cumhurbaşkanlığı İdari İşler Başkanlığı Hukuk ve Mevzuat Genel Müdürlüğü ile ilgisi yoktur.
Resmî Gazete'nin kendisi için [resmigazete.gov.tr](https://www.resmigazete.gov.tr) adresine başvurun.*
