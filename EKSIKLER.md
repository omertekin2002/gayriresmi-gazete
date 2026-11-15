# Eksikler ve açık sorular

*Durum: 15 Kasım 2026 · Liste: 35.420 yayın (33.417 asıl + 2.003 mükerrer) · Son sayı: 33417 (1 Kasım 2026)*

Asıl sayıların numaralandırması eksiksiz: 1'den 33417'ye kadar her numara listede ve her birinin bir tarihi var.
Bu belge, listenin **henüz kesinleşmemiş** kısımlarını, bunların nedenini ve nasıl tamamlanacağını anlatır.

Açık kalemlerin neredeyse hepsinin nedeni aynı: liste bulutta derlendi. Orada resmigazete.gov.tr yurt dışından
erişime kapalıydı ve kullanılabilen indirme aracı **10 MB'tan büyük dosyaları kabul etmiyordu**. Bu yüzden arşivdeki
418 büyük PDF hiç açılamadı. Siteye doğrudan erişebilen bir bilgisayardan (pratikte Türkiye'den)
[`scripts/yerel_tamamla.py`](scripts/yerel_tamamla.py) bu kalemleri kapatır. Kullanımı ve Claude Code için hazır devir
istemi [4. bölümde](#4-yerel-bilgisayarda-tamamlama) ve [5. bölümde](#5-claude-code-için-devir-istemi).

## 1. Açık kalemler

| # | Konu | Adet | Bugünkü durum | Nasıl kapanır |
|---|---|---:|---|---|
| 1 | 2 Kasım 2026'dan sonraki sayılar | ~2 hafta | Listede yok | `yerel_tamamla.py yeni` |
| 2 | Tarihi tahmin olan asıl sayılar | **158** | Tarih ±1–3 gün belirsiz | `indir_oku` + görsel kontrol |
| 3 | Tarihi atıftan alınan asıl sayılar | **105** | Tarih büyük olasılıkla doğru, künyeden doğrulanmadı | `indir_oku` |
| 4 | İçeriği görülmemiş mükerrerler | **155** | Var oldukları kesin; tarih ve "mükerrer" olduğu varsayım | `indir_oku` |
| 5 | "17914 Mükerrer" sorusu | 1 | TBMM kaydı var, arşivde dosyası yok | `indir_oku` + `arsiv_mukerrer_tara` |
| 6a | 15164'ün tarihi | 1 | TBMM kaydı komşu sayılarla çelişiyor | `indir_oku` (zaten iş listesinde) |
| 6 | 2000–2013 mükerrerleri | 496 | Tek kaynaktan (resmî günlük sayfalar) | `mukerrer_tara` (isteğe bağlı) |
| 7 | 27 Haziran 2000 öncesi mükerrer yoklaması | 784 | Paralel indirmeyle tek kez yoklandı | `arsiv_mukerrer_tara` (isteğe bağlı) |

2–4. satırlardaki 418 kalemin her biri, olası tarih aralığıyla birlikte
[`data/acik_kalemler.csv`](data/acik_kalemler.csv) dosyasında. Bu dosya `yerel_tamamla.py` betiğinin iş listesidir.

### 1.1 Yeni sayılar

Liste, 1 Kasım 2026 tarihli 33417 sayıda bitiyor. Ondan sonraki günler taranmadı. `yeni` komutu listenin son
gününden bugüne kadar her günün `eskiler/YYYY/AA/YYYYAAGG.htm` sayfasını ve `M1`, `M2` … mükerrer sayfalarını okur.
Önce listede zaten olan son üç günü yeniden okuyup ayrıştırıcıyı sınar; sayı numarası beklenen sıradan saparsa durur.

### 1.2 Tarihi tahmin olan 158 asıl sayı

Arşiv PDF'leri 10 MB'tan büyük ve 157'si için başka hiçbir kaynakta tarihli bir atıf bulunamadı. Tarih, önceki ve
sonraki sayının tarihleri arasından tahmin edildi (`tarih_kaynagi = komşu sayılardan tahmin (kesin değil)`; olası en erken ve en
geç tarih `not` kolonunda).

- Belirsizlik küçük: 123 sayıda önceki ve sonraki sayı arasında yalnızca 2 gün var, 26'sında 3, 6'sında 4, 3'ünde 6.
- Dönemlere dağılım: 1930'lar 2, 1950'ler 1, 1960'lar 17, 1970'ler 53, 1980'ler 29, 1990'lar 53, 2000 3.
- Örnek: 15389 (komşu sayılara göre en erken 19, en geç 21 Ekim 1975; tahmin 20 Ekim).
- **15164 için çelişen bir atıf var.** TBMM kaydı 1867 sayılı Kanun'un (Karayolları 1975 bütçesi) 03.03.1975 tarihli
  15164 sayılı Resmî Gazete'de yayımlandığını söylüyor. Oysa 15163 28 Şubat, 15165 2 Mart, 15166 3 Mart tarihli (üçü de
  künyeden, gün adı kontrolüyle). 3 Mart, 15164 için mümkün değil; büyük olasılıkla TBMM kaydındaki tarih 15166'nınki
  ile karışmış. Bu yüzden atıf kullanılmadı, tarih tahmin olarak kaldı (1 Mart). Künye okununca kesinleşir.

### 1.3 Tarihi atıftan alınan 105 asıl sayı

Bunların da PDF'i 10 MB'tan büyük. Tarihleri başka kaynaklardan kesinleştirildi ama künyeleri hiç görülmedi:

| Kaynak | Adet |
|---|---:|
| TBMM "Kanunlar ve Kararlar" kaydındaki yayım tarihi ve sayısı | 61 |
| Sonraki Resmî Gazete metinlerindeki "… tarihli ve … sayılı Resmî Gazete" atfı | 22 |
| Aynı numaralı mükerrer nüshanın künyesi | 22 |

Atıf yalnızca komşu sayıların izin verdiği aralığa düşüyorsa kabul edildi. Hata olasılığı düşük, ama künyeyle
doğrulamak listeyi tek tip yapar ve TBMM kaydındaki olası yazım hatalarını yakalar.

### 1.4 İçeriği görülmemiş 155 mükerrer

Sunucu bu dosyaların var olduğunu bildirdi ama boyutları 10 MB'ı aştığı için indirilemedi (154 sayıya ait 155 dosya;
1960'lar 1, 1970'ler 9, 1980'ler 62, 1990'lar 75, 2000 8). Listeye "aynı gün çıkmış mükerrer" olarak eklendi. Görülmeyen
üç şey var:

- Künyesindeki tarih asıl sayınınkiyle aynı mı (mükerrerlerin çoğu aynı gün çıkar, ama ör. 588'inki üç gün sonra).
- Dosya gerçekten o sayının mükerreri mi (künyede "Mükerrer" ibaresi ve aynı sayı numarası).
- Dosya adındaki sıra (`_1`, `_2`) künyedeki mükerrer sırasıyla aynı mı.

### 1.5 "17914 Mükerrer" sorusu

TBMM kaydına göre 2766 sayılı Kanun (13.5.1971 tarihli Sıkıyönetim Kanunu'nda değişiklik), 30.12.1982 tarihli
**17914 sayılı Resmî Gazete'nin mükerrerinde** yayımlandı. Ancak arşivde `17914_1.pdf` yok (404). Bir sonraki sayının
(17915, 31.12.1982) mükerrerlerinden `17915_1.pdf` 10 MB'tan büyük olduğu için açılamadı, `17915_2.pdf` ise gerçekten
17915'in mükerreri. Üç olasılık var:

1. `17915_1.pdf` aslında "17914 Mükerrer" (arşivde yanlış adlandırılmış),
2. 17914'ün mükerreri arşive hiç yüklenmemiş,
3. TBMM kaydındaki "Mükerrer" ibaresi hatalı (TBMM aynı kanun için ibaresiz bir kayıt da tutuyor).

Arşivdeki asıl 17914 sayısının ilk sayfası (`kanit/arsiv_pdf_ilk_sayfa.jsonl.gz`, anahtar `17914`) zaten "Kanun No.
2766, Kabul Tarihi: 28/12/1982" metniyle başlıyor ve künyesinde "Mükerrer" ibaresi yok. Yani kanun asıl sayıda
yayımlanmış; en olası açıklama 3. seçenek (TBMM'nin ikinci kaydındaki "Mükerrer" ibaresi hatalı). Yine de
`17915_1.pdf`'in künyesine bakmak soruyu kapatır. `indir_oku` bu dosyayı zaten indirir: künyede 17914
yazıyorsa sayı uyuşmazlığı nedeniyle kalemi otomatik uygulamaz ve karar için ayırır.

### 1.6 2000–2013 mükerrerleri

27 Haziran 2000 – 31 Aralık 2013 arasındaki 496 mükerrer yalnızca resmî günlük sayfalardan (`…M1.htm`, `…M2.htm`)
bulundu. 2014'ten sonrası Lexpera'nın günlük listesiyle karşılaştırıldı: asıl sayılar aynı (Lexpera'nın 31.10.2026
sayfasında 33416 henüz yoktu; 04.08.2016 sayfasındaki "2016084" kaydı bir ayrıştırma hatası); resmî sitede Lexpera'da
olmayan 20 mükerrer nüsha (18 güne ait) var, tersi yalnızca bir hatalı kayıt (bkz. 3. bölüm). 2000–2013 için böyle ikinci bir kaynak kullanılmadı. Bulutta mükerrer sayfaları bir yapay zekâ ajanı aracılığıyla yoklandı. `mukerrer_tara` her günün
mükerrer sayfalarını doğrudan yeniden yoklar ve listeyle karşılaştırır. Listeyi değiştirmez, yalnızca uyuşmayan
günleri raporlar. 4.936 günün her biri için en az bir istek atar (toplam ~5.400; saniyede bir istekle ~1,5–2 saat).

### 1.7 2000 öncesi mükerrer yoklaması

27 Haziran 2000'den önceki 784 mükerrer, arşivde her sayı için `_1`, `_2` … dosyalarının denenmesiyle bulundu. Bu
yoklama bulutta paralel indirmeyle tek kez yapıldı. Bazı dosyaların yanlış numarayla eşleştirildiği anlaşılınca şüpheli
106 dosya tek tek yeniden indirildi: 73'ü açıldı ve künyeleri dosya adlarıyla tuttu, 32'si 404 döndü (o adla dosya yok),
15389 ise 10 MB'ı aştı. Geri kalan 404 yanıtları ayrıca yeniden yoklanmadı. TBMM kayıtları dolaylı bir kontrol sağlıyor:
`ek` alanında "mükerrer" geçen 364 TBMM kaydının (yalnızca "Mükerrer" yazan 332 kaydın 329'u dahil) 361'i, aynı
numaralı sayının listede en az bir mükerreri olduğunu doğruluyor. Kalan üçünden ikisi TBMM kaydındaki sayı yazım hatası (19237 → 19327, 23792 → 23729;
ikisinin de o tarihte mükerreri var), üçüncüsü yukarıdaki 17914 sorusu.

`arsiv_mukerrer_tara` her sayı için `_1.pdf`'i (ve varsa devamını) dosyanın yalnızca ilk kilobaytını okuyarak yoklar.
Yaklaşık 25.000 istek atar (saniyede bir istekle ~7–8 saat), uyuşmayanları raporlar.

## 2. Araçla kapanmayan, bilinen belirsizlikler

- **Görüntüden okunan tarihler.** 1.828 tarih, künye görüntüsünün Claude modelleriyle (Opus ve Haiku) okunmasından
  geliyor. Hepsi künyedeki gün adı ve sayı sırasıyla tutuyor. Basılı sayı numarası 1.807'sinde de doğrulandı. 20'sinde
  numaranın bir hanesi okunamadı ya da farklı okundu. Bunlara 400 dpi'da yeniden bakıldı: 9345 ve 9792'nin numarası
  doğru çıktı; 11487'nin künyesinde "14487", 8865'inkinde "8365" basılı (baskı hatası); kalan 16'sında hane baskıda
  kırık ya da silik (çoğu 3/8, 5/3, 0/6 karışıklığı). 9870'te gün adı silik. Her birinin açıklaması `not` kolonunda.
  OCR ile tarihlendirilmiş 210 rastgele sayıda yapılan görsel denetimde 209'u birebir tuttu, biri düşük güvenle
  okunduğu için kabul edilmedi.
- **Arşive hiç yüklenmemiş mükerrerler.** 2000 öncesi için tek kaynak arşiv. Arşivde dosyası olmayan bir mükerrer
  listede de yok. Yalnızca TBMM kayıtlarındaki kanun ve kararlar için dolaylı kontrol var (1.7).
- **2000–2013 asıl sayıları tek kaynaklı.** 27.06.2000–31.12.2013 arasındaki 4.777 asıl sayının tarihi resmî günlük
  sayfadan geliyor; bunlardan yalnızca 24092–24095 (27–30 Haziran 2000) arşiv PDF'leriyle de karşılaştırıldı. Sayı sırası
  kesintisiz ve TBMM kayıtları ile Resmî Gazete atıflarıyla genel uyum çok yüksek (aşağıda), ama 2014 sonrasındaki
  gibi gün gün ikinci bir kaynak yok.
- **Ayrı numaralı ekler listede yok.** Liste numaralı sayıları ve mükerrerleri kapsar. "İlk 100 Sayı" derlemesinde,
  10–27 Eylül 1923 arasında çıkan ve kendi numarası (1–6) olan 6 "Gayr-ı Resmî Kısım (Resmî Ceride'nin İlavesi)" var;
  bunlar arşivde ayrı dosya olarak bulunmadı ve listeye alınmadı. Sonraki yıllarda başka ayrı numaralı ek olup
  olmadığı araştırılmadı.
- **Yayımlanmayan günler.** Gazetenin çıkmadığı günler listede yer almaz. 2000 sonrası için resmî sayfa "yayımlanmamaktadır"
  diyor; daha öncesi için yalnızca sayı numarasının kesintisiz olması, hiçbir asıl sayının eksik olmadığını gösteriyor.
- **Basılı bilgisi eksik ya da hatalı künyeler** (tarihleri gerekçeleriyle `not` kolonunda):
  - 293 (Şubat 1926): künyede gün sayısı yok, yalnızca "Salı, Şubat 1926" (`kanit/gorsel_okumalar.json.gz`). Tarih
    (9 Şubat 1926) üç TBMM kanun kaydından (727, 728, 729).
  - 588'in mükerreri: Osmanlıca künyede yalnızca "Pazar, Mayıs 1927". 589 sayı 3 Mayıs'ta çıktığından tek olasılık 1 Mayıs.
  - 8489: gün rakamının ikinci hanesi baskıda kırık. Künyedeki "Pazartesi" ve komşu sayılar 24 Ağustos 1953'ü verir.
  - 14490: künyede "23 Mart 1973 Çarşamba" basılı, ama sayı sırası ve gün adı 28 Mart 1973'ü gösteriyor (baskı hatası).

## 3. Kapatılanlar ve sorun olmadığı anlaşılanlar

- **1921–1923 arasındaki yaklaşık 26 aylık (784 günlük) boşluk gerçek.** 21. sayı 18 Temmuz 1921, 22. sayı 10 Eylül 1923
  tarihli; "İlk 100 Sayı" derlemesi de aynı numaralandırmayı veriyor. Yayının bu dönemde savaş nedeniyle durduğu
  ([Vikipedi: Resmî Gazete](https://tr.wikipedia.org/wiki/Resm%C3%AE_Gazete_(T%C3%BCrkiye))) genel kabul görüyor.
- **İlk 100 sayı resmî derlemeyle birebir aynı.** Cumhurbaşkanlığı İdari İşler Başkanlığı'nın *T.C. Resmî Gazete İlk 100
  Sayı* (Cilt I–II) derlemesinin içindekiler bölümündeki 100 tarihin 100'ü listeyle aynı
  ([`data/ilk100_fihrist.json`](data/ilk100_fihrist.json)). Derlemede bu dönem için mükerrer yok, listede de yok.
- **"Arşivde yanlış adlandırılmış dosyalar" iddiası geri çekildi.** Bulutta dosyalar paralel indirilirken bazıları yanlış
  sayı numarasıyla eşleştirilmişti. Şüpheli 106 dosya tek tek yeniden indirildi; açılabilenlerin hepsinin adı doğru
  çıktı. Bu yüzden 22494 ve 23942'nin var sanılan mükerrerleri listeden çıkarıldı, 17 satırın bağlantısı doğru dosyaya
  döndü (commit `88fbd6b`).
- **Künyesinde gün adı tarihle tutmayan 7 sayı:** hepsinde basılı tarih doğru çıktı.
  - 54 ve 77: İlk 100 Sayı derlemesiyle doğrulandı.
  - 259 ve 635: TBMM kayıtlarıyla doğrulandı.
  - 494 ve 18223: gün adı bir önceki sayınınki olarak kalmış (önceki ve sonraki sayıların künyeleri doğru).
  - 207: gün adının gösterdiği gün (2 Kasım 1925), bir sonraki sayının tarihinden (1 Kasım) sonraya düşüyor.
- **OCR'ın haftanın gününü okuyamadığı 5 sayı** (8244, 8257, 8266, 8290, 8291): künye görüntülerine bakıldı, basılı gün
  adları tarihlerle tutuyor (okunan gün adları `not` kolonunda ve `kanit/kunye_duzeltmeleri.json.gz`'de).
- **Resmî sitedeki hatalar** düzeltildi ve açıklandı (ör. 18.11.2000 sayfasında 24334 yazıyor, doğrusu 24234). Liste
  için [README](README.md#resmî-kaynaktaki-tutarsızlıklar).
- **Lexpera'daki tek fazlalık** (15.03.2018, "30363 1. Mükerrer") resmî günlük sayfada olmadığı için listeye alınmadı.
- **Bağımsız atıflarla genel uyum** (`scripts/adjudicate.py`; atıflar `kanit/atiflar.json.gz`'de): tarihi künyeden
  ya da günlük sayfadan gelen ve TBMM kaydı bulunan 5.115 sayının 5.020'sinde tarih aynı. Farklı 95 sayının 83'ünde TBMM
  kaydında tek haneli bir yazım hatası var, 12'si sayı sırasıyla bağdaşmıyor. Ayrıca PDF'i okunamayan ama TBMM kaydı bulunan 63
  sayının 62'sinin tarihi bu kayıttan kesinleşti, biri (15164) çelişiyor (1.2). Resmî Gazete metinlerindeki atıflarda 4.215 sayının
  4.180'i aynı.

## 4. Yerel bilgisayarda tamamlama

Gerekenler:

- resmigazete.gov.tr'ye doğrudan erişim (yurt dışından site açılmıyor),
- Python 3.9+,
- poppler (`pdftotext`, `pdftoppm`, `pdfinfo`; macOS'ta `brew install poppler`, Debian/Ubuntu'da
  `apt install poppler-utils`) **ya da** `pip install pymupdf`,
- indirilecek veri birkaç GB (418 PDF'in her biri 10 MB'tan büyük). PDF'ler okunduktan sonra silinir (`--sakla`
  verilmezse), diskte yalnızca künye görüntüleri ve metinler kalır.
- Windows'ta `python3` yerine `py` yazın.

```bash
git checkout claude/resmi-gazete-tum-sayilar && git pull
python3 scripts/yerel_tamamla.py baglanti        # erişim ve araç kontrolü, "TAMAM" demeli
python3 scripts/yerel_tamamla.py indir_oku       # 418 PDF'i sırayla indirir ve okur; kesilirse kaldığı yerden devam eder
python3 scripts/yerel_tamamla.py durum           # otomatik karar verilemeyenleri yerel/gorsel_gerekli.txt'ye yazar
#   → yerel/kunye/<anahtar>.png görüntülerine bakıp yerel/gorsel.json'u doldurun (biçimi betiğin başında)
python3 scripts/yerel_tamamla.py uygula --kuru   # neyin değişeceğini gösterir, hiçbir şey yazmaz
python3 scripts/yerel_tamamla.py uygula          # listeyi, JSON'u, yıllık özeti, raporu, README'yi ve açık kalemleri günceller
python3 scripts/yerel_tamamla.py yeni            # 2 Kasım 2026'dan bugüne yeni sayılar
# isteğe bağlı yoklamalar (yalnızca rapor üretir):
python3 scripts/yerel_tamamla.py arsiv_mukerrer_tara --bas 17914 --son 17915
python3 scripts/yerel_tamamla.py mukerrer_tara --bas 2000-06-27 --son 2013-12-31
python3 scripts/yerel_tamamla.py arsiv_mukerrer_tara --bas 1 --son 24095
```

Otomatik karar kuralı: künye metninden çıkan tarih adaylarından **tam biri** komşu sayıların verdiği aralığa düşüyor ve
künyedeki gün adıyla tutuyorsa, künyede okunan sayı numarası doğruysa ve (mükerrerlerde) "Mükerrer" ibaresi varsa, tarih
kendiliğinden kabul edilir. Atıftan tarihlendirilmiş bir sayıda künye farklı bir tarih verirse kalem `celiski` olarak
ayrılır. Diğer her durumda kalem görsel kontrole kalır. `uygula`, görsel okumaları da aynı kurallarla denetler.
Aralık dışı bir tarih, tutmayan bir gün adı ya da farklı bir sayı numarası, açıkça `"zorla": true` ve gerekçe yazılmadıkça
reddedilir; "zorla" ile verilen tarih (basılı tarih bir baskı hatasıysa doğru tarih) gerekçesiyle birlikte nota
yazılır. Yazmadan önce listenin bütünlüğü denetlenir: numaralar kesintisiz olmalı, tarih geriye gitmemeli, her
mükerrerin asıl sayısı bulunmalı.

Bütünlük denetimi başarısız olursa hiçbir dosya (kanıt dosyası dahil) yazılmaz; `gorsel.json`'u düzeltip `uygula`'yı
yeniden çalıştırın.

Siteye karşı nazik olun: betik istekleri sırayla ve aralarında bekleyerek gönderir (`--bekle`, varsayılan 1–1,5 saniye).
Birden çok kopyayı aynı anda çalıştırmayın.

Bittiğinde bu belgedeki sayıları ve tabloları güncelleyin; kapanan kalemleri 3. bölüme taşıyın.

## 5. Claude Code için devir istemi

Aşağıdaki metin, depoyu Türkiye'deki bir bilgisayarda açan bir Claude Code oturumuna olduğu gibi verilebilir.

```text
You are continuing work on the dataset in this repository (GitHub: omertekin2002/gayriresmi-gazete, branch
claude/resmi-gazete-tum-sayilar). It is a complete chronological list of every issue of the Turkish Official Gazette
(T.C. Resmî Gazete), 1921 → 2026: data/resmi_gazete_sayilari.csv (+ .json), with evidence in kanit/ and scripts in
scripts/. Everything user-facing in the repo is written in Turkish; keep it that way (notes, docs, commit messages).

The list was built in a cloud sandbox where resmigazete.gov.tr was geo-blocked and the only usable fetch tool refused
files over 10 MB, so 418 archive PDFs larger than 10 MB were never opened, and nothing after 2026-11-01 was collected.
Your job is to close those gaps from this computer, which can reach resmigazete.gov.tr directly with no size limit.

Read first: EKSIKLER.md (what is open and why), the docstring at the top of scripts/yerel_tamamla.py (commands, the
yerel/gorsel.json format), and data/acik_kalemler.csv (the work list: 158 "tahmin", 105 "atif", 155 "buyuk_mukerrer").

Steps:
1. Clone the repo if it is not here yet, then: git checkout claude/resmi-gazete-tum-sayilar && git pull (on Windows
   use `py` instead of `python3` in the commands below). Make sure poppler (pdftotext/pdftoppm/pdfinfo) or PyMuPDF
   is installed. Run `python3 scripts/yerel_tamamla.py baglanti`. It must print TAMAM. If the site is unreachable,
   stop and tell me. Do not use proxies, VPNs or mirror sites to get around it.
2. Run `python3 scripts/yerel_tamamla.py indir_oku` in the background. It downloads the 418 PDFs one at a time with a
   delay, extracts page-1 text, decides automatically where the masthead is unambiguous, renders masthead images
   for the rest, and deletes each PDF after reading. It is resumable: just rerun it after an interruption. Never run
   two copies or add parallelism; keep the delay at ≥1 s. Expect several GB of transfer and a few hours.
3. Run `python3 scripts/yerel_tamamla.py durum`. For every line in yerel/gorsel_gerekli.txt, look at
   yerel/kunye/<key>.png (and yerel/sayfa1/<key>.png if the masthead is not in the crop) and add an entry to
   yerel/gorsel.json. Record what is PRINTED: date (YYYY-MM-DD, Gregorian; Rumi years 1336–1341 = +584), weekday name,
   issue number, and whether "Mükerrer" is printed. The date must fall within the row's en_erken…en_gec window, which
   comes from the neighbouring issues. If the printed date is clearly a misprint (the printed weekday and the
   neighbouring issues point to another day), put the CORRECTED date in "tarih" with "zorla": true and a Turkish
   "not" giving the evidence. The script rejects "zorla" without a "not". If there are more than ~40 images, use
   subagents in batches of ~20 that return JSON entries, then look at a random 10% of their images yourself and
   re-check any batch with a mismatch.
   Rule for surprises: if a file is not what its name says (a different issue number, a "mükerrer" file without the
   Mükerrer marker, a mükerrer that belongs to another issue), never "zorla" it and do not edit anything for it; leave
   it out of gorsel.json. List it for me with the evidence and wait for my decision. After I approve a hand edit to data/resmi_gazete_sayilari.csv, run
   `python3 scripts/yerel_tamamla.py yeniden_yaz`, which validates, re-sorts and rewrites every output.
   Special cases: (a) 17915_1. TBMM says Law 2766 was published in "17914 Mükerrer" on 1982-12-30, the archive has
   no 17914_1.pdf, and the main 17914 issue already carries Law 2766 with no Mükerrer marker. Check whether the
   17915_1 masthead says 17914 or 17915 Mükerrer, run
   `python3 scripts/yerel_tamamla.py arsiv_mukerrer_tara --bas 17914 --son 17915`, and report. (b) 15164. TBMM gives
   1975-03-03, which is impossible between 15163 (28 Feb) and 15165 (2 Mar). Report what its masthead says.
4. Run `python3 scripts/yerel_tamamla.py uygula --kuru`, review the planned changes and the REDDEDİLDİ (rejected) lines,
   fix gorsel.json where needed, then run `python3 scripts/yerel_tamamla.py uygula`. If validation fails (numbers 1..N
   with no gaps, dates never going backwards, every mükerrer has its main issue), nothing is written, not even the
   evidence file. Fix the offending gorsel.json entry and run it again.
5. Run `python3 scripts/yerel_tamamla.py yeni` to add issues from 2026-11-02 up to today. It first re-reads the last
   three known days as a self-test. If that fails, the daily page HTML has changed: fix gunluk_oku() in the script
   (pages may be UTF-8 or Windows-1254) and rerun. It also stops, writing nothing, if a mükerrer page returns an
   error or does not match the day. Rerun later or inspect that page. Never invent rows.
6. Optional, if I agree (long-running, report-only): `mukerrer_tara --bas 2000-06-27 --son 2013-12-31` (~1.5 h) and
   `arsiv_mukerrer_tara --bas 1 --son 24095` (~7 h). Investigate every mismatch by opening the page or PDF before
   changing the list.
7. Update EKSIKLER.md: new numbers, closed items moved to section 3, anything still unresolved with the reason. Then
   rebuild the HTML view: `python3 scripts/build_artifact.py data/resmi_gazete_sayilari.csv site`. Its outputs
   site/data.json and site/gayriresmi-gazete.html are gitignored; site/head.html, body.html and app.js are tracked.
   Tell me if the published page should be updated. Commit in small logical commits with Turkish
   messages. Never commit yerel/ or any PDFs. Push to claude/resmi-gazete-tum-sayilar. Do not open a pull request
   unless I ask.

Done means: data/acik_kalemler.csv contains only items that are genuinely unresolvable, each explained in EKSIKLER.md;
the list runs to the latest published issue; validation passes; everything is pushed. Finish with a short summary:
how many dates changed (and by how much), any rejected or surprising items, and the 17914 answer.
```
