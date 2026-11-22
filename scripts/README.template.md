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
| [`data/resmi_gazete_sayilari.json`](data/resmi_gazete_sayilari.json) | Aynı liste, JSON (`gun` alanı yoktur; `tarih_kaynagi` aşağıdaki tabloda verilen kısa kodlarla yazılır, boş not `null`) |
| [`data/yillik_ozet.csv`](data/yillik_ozet.csv) | Yıl başına asıl/mükerrer sayısı, yılın ilk ve son sayı numarası |
| [`data/dogrulama_raporu.json`](data/dogrulama_raporu.json) | Tutarlılık kontrollerinin sonuçları ve atıf istatistikleri. Liste sayılarını, kontrolleri, `tarih_kaynagi` dağılımını ve atıf istatistiklerini `scripts/yerel_tamamla.py` listeyi her yazışında yeniden hesaplar (mükerrer yoklamalarının özetini `yoklama_ozeti` yazar); `kaynaklar_arasi_celiski` ve `yalnizca_lexperada_olup_cikarilan` ise ilk derlemenin son birleştirmesinden (`kanit/birlestirme_raporu.json.gz`) kalmadır, yeniden hesaplanmaz |
| [`data/resmi_site_duzeltmeleri.json`](data/resmi_site_duzeltmeleri.json) | Resmî sitenin günlük sayfalarında ve mükerrer sayfalarında bulunup düzeltilen sayı numarası hataları |
| [`data/tbmm_rg_atiflari.csv`](data/tbmm_rg_atiflari.csv) | TBMM kayıtlarındaki kanun ve Meclis kararlarının yayımlandığı Resmî Gazete tarihi ve sayısı (karşılaştırmada kullanıldı): ham kayıtlardan bu bilgiyi «tarih No: sayı» biçiminde taşıyan 19.070 kayıt, en yenisi 28 Temmuz 2021. 767 satır, TBMM'nin aynı sorgu yanıtında aynı kaydı birden çok kez vermesinden gelen birebir tekrar; Resmî Gazete bilgisi olmayan kanun ve kararlar dosyada yok (aşağıda «Bağımsız atıflarla doğrulama») |
| [`EKSIKLER.md`](EKSIKLER.md) | **Kapatılan açık kalemler, kalan belirsizlikler** ve listenin nasıl güncel tutulacağı |
| [`data/acik_kalemler.csv`](data/acik_kalemler.csv) | Künyesi henüz görülmemiş kalemlerin iş listesi (`scripts/yerel_tamamla.py` üretir; Kasım 2026'daki yerel tamamlamadan sonra boş) |
| [`data/ilk100_fihrist.json`](data/ilk100_fihrist.json) | Resmî "İlk 100 Sayı" derlemesindeki sayı–tarih eşleşmeleri (karşılaştırmada kullanıldı) |
| [`kanit/`](kanit/) | Her tarihin dayandığı ham veriler (OCR metinleri, görsel okumalar, günlük sayfalar, atıflar, yerel tamamlama kayıtları) |
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

`yayin_adi` sayı numarası aralığına göre atanır. Resmî çevriyazılarda 27, 28, 32–39 ve 46 numaralı sayıların (27 Eylül –
6 Aralık 1923) künyesinde hâlâ «Ceride-i Resmiy(y)e» yazar.

## Yöntem

Tüm sayılar **resmigazete.gov.tr** üzerinden tek tek tarandı. İlk derleme (Ekim–Kasım 2026) bulutta yapıldı: site Türkiye
dışından doğrudan erişime kapalı olduğu için indirmeler bir web-getirme aracı üzerinden yapıldı ve bu araç 10 MB'tan büyük
dosyaları kabul etmedi. Bu yüzden açılamayan 420 arşiv PDF'i ve 1 Kasım 2026'dan sonraki sayılar, 17–18 Kasım 2026'da siteye
doğrudan erişebilen bir bilgisayardan [`scripts/yerel_tamamla.py`](scripts/yerel_tamamla.py) ile tamamlandı (aşağıda
«Yerel tamamlama»).

**1921 – Haziran 2000 (Sayı 1 – 24095): arşiv PDF'leri.** Her sayı numarası için `arsiv/<sayı>.pdf` indirildi
(ilk 1053 sayı için günümüz Türkçesine aktarılmış `arsiv/<sayı>T.pdf`), ardından `arsiv/<sayı>_1.pdf`, `_2.pdf` …
denenerek mükerrer nüshalar arandı. Tarih, PDF'in ilk sayfasındaki künyeden okundu:

- OCR metninden tarih adayları çıkarıldı (eski ay adları — *Teşrinievvel, Kânunusani, Birincikânun* … — ve 1336–1341
  Rumi yılları dahil). Künyedeki **haftanın günü** ile tutan ve sayı sırasıyla çelişmeyen aday seçildi
  (sayı numarası arttıkça tarih geriye gidemez).
- İlk derlemede OCR'ın kesin bir tarih vermediği 1.828 künye görüntü olarak (Claude modelleriyle) okundu. Okunan tarih,
  künyedeki haftanın günü ve sayı sırasıyla tutuyorsa kabul edildi. Basılı sayı numarası bunların 1.808'inde okunan değerle
  aynı; 2'sinde (9345, 9792) görüntüye yeniden bakılınca doğru çıktı; 18'inde numaranın bir hanesi baskıda kırık, silik ya da
  yanlış basılmış; ayrıca 9870'te gün adı silik (hepsinin açıklaması `not` kolonunda). Bugün `tarih_kaynagi` değeri görsel
  okuma olan {GORSEL} satırın geri kalanı, yerel tamamlamada görüntüden okunan künyelerdir.
- **Bağımsız denetim:** OCR ile tarihlendirilmiş sayılardan rastgele seçilen 210 sayı ayrıca görsel olarak okundu;
  209'u birebir tuttu, 1'i düşük güvenle okunduğu için kabul edilmedi (hatalı tarih çıkmadı).
- **Yerel tamamlama (17–18 Kasım 2026).** Bulutta açılamayan 420 büyük PDF (263 asıl sayı, 157 mükerrer) siteden sırayla
  indirildi ve künyeleri okundu. 418'i iş listesindeydi: 384'ünde tarih PDF'in metin katmanından otomatik çıktı (komşu
  sayıların izin verdiği aralıkta, künyedeki gün adıyla tutan tek tarih adayı; sayı numarası ve mükerrer ibaresi de
  tutuyor), 34'ü görüntüden okundu. Bu 418 künyenin hepsi ayrıca, dosya adını ve beklenen tarihi bilmeyen bağımsız okuyuculara (Claude)
  **kör** olarak okutuldu (556 okuma, `kanit/yerel_kor_okumalar.json.gz`); 15873'ün künyesinde yanlış basılmış numara (15973,
  aşağıda) dışında listeyle çelişen tek bir tarih, sayı numarası ya da mükerrer ibaresi çıkmadı. Sonuç:
  - tarihi komşu sayılardan **tahmin** edilmiş 158 sayıdan {TAHMIN_KUNYE_AYNI} tanesinde tahmin doğru çıktı; {TAHMIN_KUNYE_FARKLI} tanesinde künye
    1–2 gün farklı bir tarih verdi (2900, 12791, 13373, 13503, 16641, 21683, 22266, 23321, 23995) ve liste düzeltildi;
  - tarihi **atıftan** alınmış 105 sayıdan {ATIF_KUNYE_AYNI} tanesinde künye, atıfla aynı tarihi verdi;
  - içeriği görülmemiş 155 **mükerrer** dosyasının hepsinin künyesinde dosya adındaki sayı numarası, «Mükerrer» ibaresi ve
    asıl sayıyla aynı tarih var (23923'ün ikinci mükerrerinde «2. Mükerrer»); günlük sayfadan tarihlenen iki mükerrerin
    (24273, 24281) büyük arşiv PDF'leri de günlük sayfayla aynı sonucu verdi.
- **İlk derlemenin üç tarih hatası düzeltildi.** 6126, 10908 ve 11979'da OCR metninin gövdesinde geçen başka bir tarih,
  künyedeki tarihin yerine seçilmişti (liste tarihi künyede basılı gün adıyla tutmuyordu; üçü de bir gün kaydı). Bu hata
  türü için arşivdeki bütün asıl sayıların OCR metni (23.828 kayıt) yeniden tarandı: künyedeki gün adı liste tarihiyle
  tutmayan başka sayı çıkmadı (gün adı künyede yanlış basılmış 7 sayı aşağıda).
- **Künyelerdeki yıl ayrıca denetlendi (18 Kasım 2026).** İlk derleme, OCR'ın okuduğu gün ve aya yılı komşu sayılardan da
  verebiliyordu; künyesi görüntüden okunan sayılarda da okuyucu beklenen tarihi biliyordu. Bu yüzden künyesinde yılı yanlış
  basılmış, hiç basılmamış ya da kırık çıkmış sayılar, açıklama düşülmeden (doğru) tarihlenmişti. Arşivdeki 24.091 asıl
  sayının 22.652'sinde liste tarihi, yılıyla birlikte, beklenen tarihi bilmeyen bir okumada geçiyor (PDF'in metin katmanı ya
  da yerel tamamlamanın okumaları). Kalan 1.439 sayıdan görüntüsü olan 1.435'inin künye görüntüsü ikinci kez
  OCR'landı; 873'ünde aynı tarih yılıyla çıktı.
  Son 566 künye gözle okundu: 251'i ilk derlemenin künye görüntüsünden, rastgele adlarla ve beklenen tarih verilmeden;
  görüntüsü olmayan 4'ü PDF'ten; ilk derlemede görüntüden okunmuş 311'i, yeniden indirilen PDF'in künye görüntüsünden, yine
  beklenen tarih verilmeden (307'si ikinci turda 2600 piksel genişlikte, 4'ü — 4946, 11004, 11007, 11049 — birinci turda
  yüksek çözünürlükte). İlk okumada yılı «şüpheli» bulunanlarla birlikte toplam 408 künyenin
  PDF'i yeniden indirilip yüksek çözünürlükte okundu (`kanit/yerel_yil_okumalari.json.gz`). Kırık, silik ya da mürekkeple
  dolmuş bir hane için ölçüt: beklenen tarihi bilmeyen üç okuyucudan en az ikisi yılı listedeki gibi okuyamadıysa (yıl olarak
  ya da kendi yazdığı tarih satırında başka bir şey kaydettiyse) satıra açıklama düşüldü. Sonuç: {YIL_NOT_N} künyede yıl sorunlu ({YIL_YANLIS_N} künyede yanlış basılmış, {YIL_YOK_N} künyede hiç
  basılı değil, {YIL_KIRIK_N} künyede bir ya da iki hanesi başka bir rakam gibi görünüyor ya da okunamıyor; aşağıda). Hepsinde
  gün, ay ve gün adı listeyle aynı; hiçbir liste tarihi değişmedi, satırlara açıklama eklendi. Sınırı: yılı OCR'da ya da yerel
  tamamlamanın okumalarında doğru çıkan 23.525 künyeye, tek tek ele alınan birkaçı dışında, yıl denetiminde topluca bakılmadı
  (baskısı kusurlu olup OCR'ın ya da okuyucunun yine de doğru okuduğu künyeler, 5180 ve 23494 dışında, bu listede yoktur) ve
  hanesi kusurlu olduğu hâlde okuyucuların çoğunun doğru okuduğu künyelere açıklama düşülmedi (ayrıntı [`EKSIKLER.md`](EKSIKLER.md)'de).

**Haziran 2000 – bugün (Sayı 24092 → {SON_SAYI}): günlük sayfalar.** {GUN_SAYISI} günün her biri için
`eskiler/YYYY/AA/YYYYAAGG.htm` sayfası ve `...M1.htm`, `M2.htm` … mükerrer sayfaları kontrol edildi.

**Çapraz kontrol.** 1 Ocak 2014 – 31 Ekim 2026 için Lexpera'nın günlük Resmî Gazete listesi ayrıca tarandı: asıl sayıların
tarih ve numaraları resmî siteyle aynı çıktı (Lexpera'nın 31.10.2026 sayfasında 33416 henüz yoktu; 04.08.2016 sayfasındaki
"2016084" kaydı bir ayrıştırma hatası). Lexpera taraması 31.10.2026'da biter; 33416 ve sonraki sayılar bu karşılaştırmanın
dışındadır. Resmî sitede Lexpera'da hiç olmayan 19 mükerrer nüsha (19 güne ait) bulundu.
Lexpera'nın 15.03.2018 tarihli "30363 1. Mükerrer" kaydı yanlış numaralı: o günün resmî mükerrer sayfası 30361'e ait
ve listede 30361'in mükerreri olarak yer alıyor. 2000 yılındaki örtüşme
aralığında (24092–24095 ve mükerrerleri) arşiv PDF'lerinden okunan tarihler günlük sayfalarla aynı.

**Bağımsız atıflarla doğrulama.** Liste, sayıların tarihini taşıyan iki bağımsız kaynakla karşılaştırıldı:

- **TBMM kanun ve karar kayıtları.** TBMM'nin eski "Kanunlar ve Kararlar Erişim" veritabanında kanunların ve Meclis
  kararlarının hangi tarih ve sayılı Resmî Gazete'de yayımlandığı yazılı. Depodaki kayıtlar (`kanit/tbmm_*.jsonl.gz`)
  hepsini kapsamıyor: en yeni atıf 28 Temmuz 2021 tarihli 31551 sayıya yapılmış (kararlarda 19 Temmuz 2021 tarihli 31546),
  sonraki sayılar için TBMM atfı yok; karar sorguları 1600 numarada bitiyor ve 28 Nisan 1948'den Eylül 1960'a kadar kabul
  edilmiş hiçbir karar kayıtlarda yok; kayıtlardaki 15.292 kanunun 658'inde, 4.499 kararın 2.914'ünde de «tarih No: sayı»
  biçiminde bir Resmî Gazete bilgisi yok (çoğunda yalnızca «Kanun Metni» ya da «Karar Metni» yazıyor; 84 kanunda «geri gönderme»).
  Tarihi künyeden ya da günlük sayfadan gelen {TBMM_SAYI} sayı numarası için bu kayıtlar var. Bunların {TBMM_AYNI} tanesinde tarih bizimkiyle birebir aynı.
  Farklı görünen {TBMM_FARK} sayının {TBMM_TYPO} tanesi TBMM kaydındaki tek haneli yazım hatası (sayı ya da tarih), {TBMM_IMKANSIZ} tanesi
  sayı sırasıyla bağdaşmayan tarih veriyor{TBMM_DIGER_CUMLE}.
  {TBMM_SIRAYA_SIGAN_CUMLE}
  Bir sayı, TBMM atıflarından en az birinin tarihi listedeki tarihle aynıysa «aynı» sayılır
  ([`scripts/atif_dogrula.py`](scripts/atif_dogrula.py)); «aynı» sayılan {TBMM_GIZLI_SAYI} sayıda listedeki tarihle çelişen
  {TBMM_GIZLI} TBMM kaydı daha var ({TBMM_GIZLI_SINIF}). Tarihi ayrıştırılamayan {TBMM_TARIHSIZ} kayıt (çoğu «22-25.09.1962»
  gibi birden çok sayıya yapılmış atıf) ile numarası son sayıdan büyük {TBMM_LISTEDISI} kayıt ({TBMM_LISTEDISI_NUMARALAR})
  karşılaştırmaya girmedi.
- **Resmî Gazete'nin kendi metinlerindeki atıflar.** "… tarihli ve … sayılı Resmî Gazete'de yayımlanan" kalıbındaki
  atıflar iki derlemden çıkarıldı. 2019–2026 Resmî Gazete tam metin derleminde
  ([moganai/turkish-resmi-gazete](https://huggingface.co/datasets/moganai/turkish-resmi-gazete)) {HF_SAYI} sayıya yapılan
  atıfların {HF_AYNI} tanesi bizim tarihimizle aynı; kalan {HF_FARK} uyuşmazlığın {HF_IMKANSIZ} tanesi sayı sırasıyla bağdaşmayan bir tarih
  veriyor (atıf metnindeki yazım hatası ya da başka bir belgeye ait numara), {HF_SIRAYA_SIGAN} tanesi ise resmî günlük sayfanın tarihiyle
  çelişen bir yazım hatası. Arşiv PDF'lerinin ilk sayfalarındaki atıflarda {ERA1_SAYI} sayının {ERA1_AYNI} tanesi aynı; kalan {ERA1_FARK}
  uyuşmazlığın {ERA1_IMKANSIZ} tanesi sayı sırasıyla bağdaşmıyor. Aynı tanımla «aynı» sayılan sayılarda da listedeki tarihle
  çelişen atıflar var: derlemde {HF_GIZLI_SAYI} sayıda {HF_GIZLI} atıf ({HF_GIZLI_SINIF}), arşiv sayfalarında {ERA1_GIZLI} atıf
  ({ERA1_GIZLI_SINIF}). Derlemdeki numarası son sayıdan büyük {HF_LISTEDISI} atıf ({HF_LISTEDISI_NUMARALAR}) karşılaştırmaya girmedi.

- **Resmî "İlk 100 Sayı" derlemesi.** Cumhurbaşkanlığı İdari İşler Başkanlığı'nın yayımladığı *T.C. Resmî Gazete İlk 100
  Sayı* (Cilt I–II, [mevzuat.gov.tr](https://www.mevzuat.gov.tr)) içindekiler bölümünde her sayının tarihi yazılı. İlk 100
  sayının 100'ünün tarihi de listeyle birebir aynı (`data/ilk100_fihrist.json`). 21. sayıdan (18 Temmuz 1921) sonraki
  26 aylık boşluk gerçek: gazete Kurtuluş Savaşı sırasında 10 Eylül 1923'teki 22. sayıya kadar çıkmadı.

İlk derlemede PDF'i açılamayan 105 sayının tarihi bu atıflardan (61 TBMM kaydı, 22 Resmî Gazete atfı) ve aynı numaralı
mükerrerin künyesinden (22) alınmıştı; yerel tamamlamada hepsinin künyesi okundu ve {ATIF_KUNYE_AYNI} tanesinde aynı tarih çıktı.
Bugün tarihi atıfa dayanan {TBMM_COZ} sayı var: 293. Künyesinde (çevriyazıda da Osmanlıca aslında da) gün rakamı basılı değil;
9 Şubat 1926 tarihi üç TBMM kaydından geliyor, künyedeki «Salı» ve komşu sayılar (292: 8 Şubat, 294: 10 Şubat) aynı günü veriyor.

### `tarih_kaynagi` değerleri

| Değer | JSON kodu | Adet | Anlamı |
|---|---|---:|---|
{KAYNAK_TABLO}

Künyesinde gün, ay ya da yıl eksik, kırık ya da yanlış basılmış {KUNYE_NOT_N} yayının (aşağıda «Bilinen sınırlamalar») tarihi
künyedeki gün adı ve komşu sayılarla tamamlandı. {KUNYE_ETIKET_CUMLESI}

## Resmî kaynaktaki tutarsızlıklar

Tarama sırasında resmî sitenin kendisinde bazı hatalar bulundu; listede doğru değerler kullanıldı ve `not` kolonunda
açıklandı:

- **Günlük sayfalarda yanlış sayı numarası:** ör. 18.11.2000 sayfasında *24334* yazıyor (doğrusu 24234, çünkü önceki gün
  24233, sonraki gün 24235); 22.01.2001 sayfasında *29425* (doğrusu 24295); 30.12.2000 ve 04.05.2001'de bir önceki sayının
  numarası tekrarlanmış; 28.11.2003 sayfasında *25298* yazıyor (doğrusu 25300). 29.10.2002 sayfasında bir numara görünse de
  o gün gazete yayımlanmamış. İki mükerrer sayfasında da numara yanlış: 29.12.2001 mükerrerinde *27625* (doğrusu 24625),
  08.03.2003 mükerrerinde *25034* (doğrusu 25042). 30.12.2000'in doğru numarası (24273) o günün mükerrerinin arşiv PDF'indeki
  künyeyle de doğrulandı.
- **Karşılığı bulunmayan mükerrer duyurusu:** 12.06.2010 günlük sayfasında «27609 Sayılı Mükerrer Resmî Gazete'de 5996 sayılı Kanun
  yayımlanmıştır» notu ve eski sunucuya (rega.basbakanlik.gov.tr) giden bir bağlantı var. Resmî sitede böyle bir mükerrer
  sayfası yok; 5996 sayılı Kanun 13.06.2010 tarihli 27610 sayıda yayımlandı (günlük sayfa ve TBMM kaydı). Listeye mükerrer
  eklenmedi.
- **Künyede yanlış basılmış sayı numarası:** 15873 sayılı gazetenin (9 Mart 1977) künyesinde «Sayı: 15973» basılı; TBMM
  kayıtları da (2039–2066 arasındaki 17 kanun) bu yanlış numarayı taşıyor. Gerçek 15973, 21 Haziran 1977 tarihlidir. İlk derlemede bulunan
  benzer iki örnek: 11487'nin künyesinde 14487, 8865'inkinde 8365 basılı.
- **Künyede yanlış basılmış ay, eksik gün rakamı:** 244'ün künyesinde (Osmanlıca aslında da) «Pazartesi, 14 Teşrinievvel
  1341 / 27 Rebiülahir 1344» basılı; iki ay adı da yanlış, doğrusu 14 Kânunuevvel 1341 / 27 Cemaziyelevvel 1344'tür (243: 13 Aralık, 245: 15 Aralık 1925; 14 Aralık pazartesi). 293 (Şubat 1926) ile
  Latin harfli ilk sayılardan 1054 ve 1056'nın (Aralık 1928) künyesinde gün rakamı hiç basılı değil, yalnızca ay ve gün adı
  var; tarihleri künyedeki gün adı ve komşu sayılardan (293 için ayrıca TBMM kayıtlarından) geliyor.
- **Künyede kırık gün rakamı:** 14490 sayılı gazetenin künyesi «23 Mart 1973 Çarşamba» gibi okunuyor (PDF'in metin katmanı da
  23 okuyor); ancak 23 Mart 1973 cumadır, 14486 sayı zaten 24 Mart tarihlidir ve 14489 (27 Mart) ile 14491 (29 Mart) arasında
  tek gün kalır: sayı 28 Mart 1973 çarşamba günü çıkmıştır. Künyeye yüksek çözünürlükte bakıldı: gün rakamının ikinci hanesi
  aynı satırdaki 1973'ün 3'üne benzemiyor, üst yarısı kapalı bir halka (alt yarısının solu çıkmamış bir 8); ilk derlemede bu
  bir baskı hatası sayılmıştı. 8489 sayının künyesindeki gün rakamı da baskıda kırık ("21" gibi görünüyor);
  künyedeki "Pazartesi" ve komşu sayılar 24 Ağustos 1953'ü verir. Yıl denetimi sırasında başka künyelerde de kırık ya da
  mürekkeple dolmuş gün rakamına rastlandı; okuyucuların çoğunun okuyamadığı üçü: 10480'in künyesi «11 Nisan 1960» gibi
  okunuyor (14'ün 4'ünden yalnızca dikey çizgi çıkmış; künyede Perşembe yazıyor, 14 Nisan 1960 perşembe), 15890'ınkinde gün
  rakamının ikinci hanesi okunamıyor («2. Mart 1977»; künyede Cumartesi yazıyor, 15889 25 Mart, 15891 27 Mart tarihli),
  16168'inkinde de öyle («1. Ocak 1978»; künyede Cuma yazıyor, 16167 12 Ocak, 16169 14 Ocak tarihli). Gün rakamları ayrıca
  taranmadı.
- **Künyede yanlış basılmış, eksik ya da kırık yıl** ({YIL_NOT_N} sayı). {YIL_YANLIS_N} sayının künyesinde gün, ay ve gün adı
  doğru, yıl yanlış: 81'de (7 Ocak 1925) «7 Kânunusani 1340» (doğrusu 1341; Osmanlıca aslının arşivdeki nüshasında basılı yıl
  elle çizilip yanına 1341 yazılmış, çizilen yılın son hanesi mürekkep lekesinin altında; 1340 resmî çevriyazıdaki okuma),
  8530'da «10 Ekim 1952» (doğrusu 1953), 8585'te «17 Aralık 1593» (1953), 12830'da «19 Şubat 1969» (1968), 13823'te
  «30 Nisan 1970» (1971). {YIL_YOK_N} sayının künyesinde yıl hiç basılı değil: 3319 («2 Haziran, Salı»; 1936), art arda beş
  sayı, 8099–8103 (2–7 Mayıs 1952) ve 23494 («15 Ekim, Perşembe»; 1998). {YIL_KIRIK_N} sayıda yılın bir ya da iki hanesi
  kırık, aşınmış ya da mürekkeple dolmuş; yıl başka bir yıl gibi okunuyor ya da okunamıyor: {YIL_KIRIK_LISTE}. En sık
  görüleni, 1940–1943 arasındaki künyelerde 4 rakamının ince çizgilerinin çıkmaması (yıl «1910», «1911», «1912», «1913» gibi
  okunuyor); 1962 ve 1964'teki dört künyede 6 rakamı 5 gibi görünüyor («1952», «1954»); 1943'teki üç künyede ve 1978–1982
  arasındaki dokuz künyede hane mürekkeple dolmuş. Her künyede ne okunduğu `not` kolonunda. Hepsinde yıl, önceki ve sonraki sayının
  tarihlerinden kesin (81 için: 80 16 Aralık 1924, 82 14 Ocak 1925) ve künyedeki gün adı o yılda tutuyor.
- **Künyede yanlış gün adı:** 7 sayının künyesinde basılı tarih ile gün adı birbirini tutmuyor (54, 77, 207, 259, 494,
  635, 18223). Hepsinde basılı tarih doğru çıktı: 54 ve 77 «İlk 100 Sayı» derlemesiyle, 259 ve 635 TBMM kayıtlarıyla
  doğrulandı; 494 ve 18223'te gün adı bir önceki sayınınki olarak kalmış (önceki ve sonraki sayıların künyeleri doğru);
  207'de gün adının gösterdiği gün bir sonraki sayının tarihinden sonraya düşüyor.
- **Künyesinde gün rakamı olmayan mükerrer:** 588 sayının mükerrerinin Osmanlıca künyesinde gün sayısı yok, yalnızca "Pazar,
  Mayıs 1927" yazıyor; 589 sayı 3 Mayıs'ta çıktığından tarih 1 Mayıs 1927 (resmî çeviri de "[1] Mayıs" diyor).

Resmî arşivde (`arsiv/*.pdf`), künyede basılı numarası okunan dosyalar arasında yanlış adlandırılmış dosya bulunmadı. İlk
derlemede 2.531 asıl sayı dosyasında (578'i çevriyazı) künyedeki numara ne OCR'dan ne görsel okumadan dosya adındaki numara
olarak çıktı; bunlar dosya adıyla eşleştirildi (`scripts/identity.py`). Yaklaşık 500'ünün basılı numarası depodaki hiçbir
okumada geçmiyor: bunlar için yalnızca tarih sırası ve kopya dosya kontrolleri var (`scripts/resolve_era1.py`). Taramanın ilk aşamasında aynı anda birden çok
dosya indirildiği için bazı dosyalar yanlış sayı numarasıyla eşleştirilmişti. Bundan şüphelenilen her dosya (106 dosya)
sonradan tek tek yeniden indirildi ve listede yalnızca bu doğrulanmış dosyalar kullanıldı. Yerel tamamlamada indirilen 420
büyük dosyanın da hepsinin künyesi dosya adındaki sayıyı taşıyor (15873'teki baskı hatası dışında). TBMM kaydındaki
«17914 Mükerrer» (2766 sayılı Kanun) ise bir kayıt hatası: kanun 30.12.1982 tarihli asıl 17914 sayıda yayımlanmış, arşivde
17914'ün mükerreri yok ve `17915_1.pdf` gerçekten 17915'in mükerreri.

## Bilinen sınırlamalar

- **Tahminî tarih kalmadı** ({TAHMIN} satır). İlk derlemede 158 sayının tarihi komşu sayılardan tahmin edilmişti; hepsinin künyesi
  Kasım 2026'da okundu (yukarıda «Yerel tamamlama»). Künyesinde tam tarih basılı olmayan, kırık çıkmış ya da yanlış basılmış {KUNYE_NOT_N} yayın
  (gün ya da ay: {GUN_AY_LISTE}; yıl: {YIL_NOT_LISTE})
  künyedeki gün adı ve komşu sayılarla tarihlendi; gerekçeleri `not` kolonunda. Kalan belirsizlikler ve kapatılan kalemler [`EKSIKLER.md`](EKSIKLER.md)'de.
- 1921–2000 dönemindeki mükerrerler arşivdeki `_1`, `_2` … dosyalarından bulundu; arşive hiç yüklenmemiş bir mükerrer
  varsa listede yoktur. TBMM kayıtlarındaki mükerrer işaretleriyle yapılan dolaylı kontrol ([`EKSIKLER.md`](EKSIKLER.md))
  1951'den önce hiçbir şeyi doğrulamıyor (işaretli ilk TBMM atfı 28 Şubat 1951 tarihli 7746 sayıya); 1921–1950 mükerrerleri
  için dayanak yalnızca arşiv yoklaması, 1–100 arası sayılar için ayrıca «İlk 100 Sayı» derlemesi. {MUKERRER_YOKLAMA}
- Resmî Gazete'nin yayımlanmadığı günler (hafta tatili, bayramlar, bazı resmî tatiller) listede doğal olarak yer almaz:
  7 Haziran 1935'ten önce hiçbir cuma günü, 26 Mayıs 1935 ile 21 Haziran 1970 arasında da hiçbir pazar günü sayı çıkmadı.

## Yeniden üretme

`scripts/` dizinindeki betikler bu listeyi üretmek için kullanıldı:

| Betik | Görev |
|---|---|
| `rg_ingest.py` | İndirilen arşiv PDF'inden ilk sayfa metnini ve künye görüntüsünü çıkarır |
| `era1_remaining.py` | Arşiv taramasında sonucu henüz alınmamış sayı numaralarını bulur ve paralel indirme için gruplara böler |
| `find_masthead.py` | İndirilen bir PDF'in ilk sayfalarının üst kısmını görsel okuma için PNG'ye çevirir |
| `rgdate.py` | Gürültülü OCR metninden tarih, haftanın günü ve sayı adaylarını çıkarır |
| `resolve_era1.py` | Arşiv sayılarına, sıralama ve haftanın günü kısıtlarıyla tarih atar |
| `collect_visual.py` | Görsel okuma sonuçlarını iş günlüklerinden (`journal.jsonl`) toplar; basılı sayı ve haftanın günüyle tutan tarihleri kabul eder |
| `identity.py` | Dosyaları künyede basılı sayıya göre eşleştirir (indirme sırasında yanlış numarayla eşleşen dosyaları yakalamak için) |
| `collect_era2.py` | Günlük sayfa taramasının sonuçlarını iş günlüklerinden (`journal.jsonl`) tek dosyada toplar |
| `parse_era2.py` | Günlük sayfa sonuçlarını normalize eder, ardışıklık kontrolü yapar |
| `lexpera_scrape.py`, `parse_era3.py` | Lexpera çapraz kontrolü |
| `tbmm_citations.py`, `mine_citations.py`, `citations.py`, `adjudicate.py` | TBMM kayıtlarından ve metinlerden tarih–sayı atıflarını toplar, listeyle karşılaştırır (`kanit/tbmm_*.jsonl.gz`'deki ham kayıtları `tbmm_citations.py` indirir) |
| `merge.py`, `build_outputs.py` | Yalnızca ilk derlemede: kaynakları birleştirir, doğrular ve `data/` dosyalarını yazar. Girdileri depoda yok ve yerel tamamlamanın okumalarını bilmezler; bugünkü listeyi üretmezler, listeyi artık `yerel_tamamla.py` yazar |
| `yerel_tamamla.py` | Siteye doğrudan erişilebilen bir bilgisayardan çalışır: yeni sayıları ekler (`yeni`), büyük PDF'leri indirip künyelerini okur, okumaları listeye işler, mükerrer yoklamaları yapar. Kasım 2026'daki tamamlama bununla yapıldı |
| `atif_dogrula.py` | TBMM ve Resmî Gazete metni karşılaştırmasının dokuz sayısını (`--detail` ile ayrıntı listelerini de) depodaki kanıt dosyalarından yeniden hesaplar; hiçbir dosyaya yazmaz. `data/dogrulama_raporu.json` → `atif_dogrulama` bloğunu `yerel_tamamla.py` listeyi her yazışında bu betiğin sonucuyla ve kendi hesapladığı sayılarla (atıftan ya da tahminden künyeye geçen tarihler, `tarih_kaynagi` dağılımı) yeniden yazar |
| `render_readme.py`, `build_artifact.py` | Bu README'yi ve tek sayfalık HTML görünümünü üretir |

Listeyi güncel tutmak için siteye erişebilen bir bilgisayarda `python3 scripts/yerel_tamamla.py yeni` çalıştırmak yeterlidir
(bkz. [`EKSIKLER.md`](EKSIKLER.md)); ilk derleme hattının ara dosyaları depoda değil, ham kanıtları `kanit/` dizininde.
Kasım 2026'daki kör okumaların (`kanit/yerel_kor_okumalar.json.gz`), ikinci OCR'ın (tesseract) ve yıl denetiminin
(`kanit/yerel_yil_okumalari.json.gz`) araçları da depoda yok, yalnızca sonuçları var; yıl denetiminden ve Kasım 2026'daki
öbür incelemelerden çıkan `not` değişiklikleri CSV elle düzenlenip `python3 scripts/yerel_tamamla.py yeniden_yaz` çalıştırılarak işlendi (raporda
`yerel_tamamlama` → `elle_duzeltme`). `data/tbmm_rg_atiflari.csv`, `data/ilk100_fihrist.json` ve
`data/resmi_site_duzeltmeleri.json`'u üreten betik de depoda yok.

---

*Bu proje resmî değildir; T.C. Cumhurbaşkanlığı İdari İşler Başkanlığı Hukuk ve Mevzuat Genel Müdürlüğü ile ilgisi yoktur.
Resmî Gazete'nin kendisi için [resmigazete.gov.tr](https://www.resmigazete.gov.tr) adresine başvurun.*
