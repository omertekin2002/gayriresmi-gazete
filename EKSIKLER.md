# Eksikler ve açık sorular

*Durum: 18 Kasım 2026 · Liste: 35.437 yayın (33.434 asıl + 2.003 mükerrer) · Son sayı: 33434 (18 Kasım 2026)*

Asıl sayıların numaralandırması eksiksiz: 1'den son sayıya kadar her numara listede ve her birinin bir tarihi var.
İlk derlemeden (15 Kasım 2026) kalan açık kalemlerin hepsi 17–18 Kasım 2026'da, resmigazete.gov.tr'ye doğrudan erişebilen
bir bilgisayardan [`scripts/yerel_tamamla.py`](scripts/yerel_tamamla.py) ile kapatıldı: **listede tahminî tarih kalmadı**,
iş listesi ([`data/acik_kalemler.csv`](data/acik_kalemler.csv)) boş. Bu belge neyin nasıl kapatıldığını
([1.](#1-açık-kalemlerin-durumu) ve [3. bölüm](#3-kapatılanlar-ve-sorun-olmadığı-anlaşılanlar)), araçla kapanmayan
belirsizlikleri ([2. bölüm](#2-araçla-kapanmayan-bilinen-belirsizlikler)) ve listenin nasıl güncel tutulacağını
([4. bölüm](#4-listeyi-güncel-tutma-ve-araç)) anlatır.

Açık kalemlerin neredeyse hepsinin nedeni aynıydı: liste bulutta derlendi. Orada resmigazete.gov.tr yurt dışından erişime
kapalıydı ve kullanılabilen indirme aracı **10 MB'tan büyük dosyaları kabul etmiyordu**. Bu yüzden arşivdeki 420 büyük PDF
(263 asıl sayı, 157 mükerrer) hiç açılamamıştı.

## 1. Açık kalemlerin durumu

| # | Konu | Adet | 15 Kasım 2026'daki durum | Bugün |
|---|---|---:|---|---|
| 1 | 1 Kasım 2026'dan sonraki sayılar | — | Listede yoktu | **Kapandı.** 33418–33434 (2–18 Kasım 2026) eklendi. Güncel tutmak için: `yerel_tamamla.py yeni` |
| 2 | Tarihi tahmin olan asıl sayılar | 158 | Tarih ±1–3 gün belirsiz | **Kapandı.** Hepsinin künyesi okundu: 149 tahmin doğru, 9'u 1–2 gün düzeltildi |
| 3 | Tarihi atıftan alınan asıl sayılar | 105 | Künyeden doğrulanmamıştı | **Kapandı.** 105'inin 105'inde künye atıfla aynı tarihi verdi |
| 4 | İçeriği görülmemiş mükerrerler | 155 | Tarih ve "mükerrer" olduğu varsayımdı | **Kapandı.** Hepsi künyesinde aynı sayı, «Mükerrer» ibaresi ve asıl sayıyla aynı tarihi taşıyor |
| 5 | "17914 Mükerrer" sorusu | 1 | TBMM kaydı var, arşivde dosyası yok | **Kapandı.** TBMM kaydındaki «Mükerrer» ibaresi hatalı (3.1) |
| 6a | 15164'ün tarihi | 1 | TBMM kaydı komşu sayılarla çelişiyordu | **Kapandı.** Künye: 1 Mart 1975 Cumartesi; TBMM kaydı hatalı |
| 6 | 2000–2013 mükerrerleri | 496 | Tek kaynaktan, bir yapay zekâ ajanı aracılığıyla yoklanmıştı | **Kapandı** (ajan aracılığı kalktı; ikinci bir kaynak hâlâ yok, 2. bölüm). 27.06.2000 → 17.11.2026 arasındaki 9.640 günün mükerrer sayfaları doğrudan siteden yeniden yoklandı: sitede 1.219, listede 1.219 mükerrer; hiçbir günde fark yok (3.1) |
| 7 | 27 Haziran 2000 öncesi mükerrer yoklaması | 784 | Paralel indirmeyle tek kez yoklanmıştı | **Kapandı.** 1–24095 arasındaki 24.095 sayı numarasının arşivdeki mükerrer dosyaları doğrudan siteden, sırayla yeniden yoklandı: arşivde 786, listede 786 mükerrer (784'ü 27.06.2000 öncesi; 24093 ve 24095'in mükerrerleri 6. kalemdeki 1.219'un da içinde); hiçbir sayıda fark yok (3.1) |

Ayrıca belgede açık kalem olarak yer almayan şu sorunlar bulundu ve giderildi (ayrıntı 3.1'de):

- İlk derlemenin **üç tarihi yanlıştı** (6126, 10908, 11979; üçü de bir gün).
- 15873'ün künyesinde sayı numarası **yanlış basılmış** (15973).
- 49 künyede **yıl** yanlış basılmış, hiç basılmamış ya da bir ya da iki hanesi kırık, aşınmış ya da mürekkeple dolmuş
  çıkmış (liste 2. bölümde). Liste tarihleri doğruydu ama satırlarda açıklama yoktu.
- 14490'ın künyesindeki «23 Mart» bir baskı hatası değil, kırık bir 8 («28»); açıklaması düzeltildi. 10480, 15890 ve
  16168'in künyelerinde de gün rakamı kırık ya da mürekkeple dolmuş; açıklamaları eklendi.
- 12 Haziran 2010 günlük sayfasındaki «27609 Sayılı Mükerrer» duyurusunun karşılığı yok.
- Resmî sitenin iki mükerrer sayfasında sayı numarası yanlış yazılmış (29.12.2001, 08.03.2003); listede zaten doğruydu,
  açıklaması eklendi.
- Tamamlama aracının kendisinde, yanlış bir tarihin fark edilmeden kabul edilmesine yol açabilecek zayıflıklar vardı (4.3).

## 2. Araçla kapanmayan, bilinen belirsizlikler

- **Görüntüden okunan tarihler.** İlk derlemede 1.828 tarih, künye görüntüsünün Claude modelleriyle (Opus ve Haiku)
  okunmasından geldi. Hepsi künyedeki gün adı ve sayı sırasıyla tutuyor. Basılı sayı numarası 1.808'inde okunan değerle aynı.
  20'sinde numaranın bir hanesi okunamadı ya da farklı okundu; bunlara 400 dpi'da yeniden bakıldı: 9345 ve 9792'nin numarası
  doğru çıktı (Kasım 2026'da görüntülerine bir kez daha bakıldı: künyelerde 9345 ve 9792 basılı); 11487'nin künyesinde
  "14487", 8865'inkinde "8365" basılı (baskı hatası); kalan 16'sında hane baskıda kırık ya da silik (çoğu 3/8, 5/3, 0/6
  karışıklığı). 9870'te gün adı silik. Her birinin açıklaması `not` kolonunda. OCR ile tarihlendirilmiş 210 rastgele sayıda
  yapılan görsel denetimde 209'u birebir tuttu, biri düşük güvenle okunduğu için kabul edilmedi. Yerel tamamlamada görüntüden
  okunan 37 künye (34 büyük PDF + düzeltilen 3 tarih) ile birlikte bugün 1.865 satırın kaynağı görsel okumadır.
- **Arşive hiç yüklenmemiş mükerrerler.** 2000 öncesi için tek kaynak arşiv. Arşivde dosyası olmayan bir mükerrer listede
  de yok. Yoklamalar (ilk derlemedeki ve Kasım 2026'daki) yalnızca `arsiv/N_1.pdf`, `N_2.pdf` … adlarını, ilk 404'e kadar
  dener: sırası atlanarak (`N_1.pdf` yokken `N_2.pdf`) ya da başka bir adla (ör. yalnızca `N_1T.pdf`; 588'in mükerrerinin
  çevriyazısı bu adla duruyor) yüklenmiş bir mükerrer de bulunamaz. Yalnızca TBMM kayıtlarındaki kanun ve kararlar için dolaylı kontrol var: `ek` alanında mükerrer işareti olan 496
  TBMM kaydının («Mükerrer», «2. Mükerrer», «(mük.)» gibi yazılmış 364'ü ve «M.», «M», «2.M» gibi kısaltılmış 132'si) 485'i,
  aynı numaralı sayının listede en az bir mükerreri olduğunu doğruluyor (sayılar `python3 scripts/atif_dogrula.py . --detail`
  çıktısında `TBMM_MUKERRER_ISARETI` altında yeniden hesaplanır). Bunlar ham kayıt adetleri: TBMM verisi aynı kanun ya da
  karar için kimi zaman birden fazla kayıt veriyor (birebir aynı ya da başlığı, tarihinin yazımı farklı). Sayı numarası ve
  kanun/karar numarası birlikte sayılınca işaretli 428 ayrı yayım var (296'sı açık yazılmış, 132'si kısaltılmış; 66'sının
  birden fazla kaydı var); bunların 417'si doğruluyor ve 173 sayı numarasına düşüyor (listede mükerreri olan sayı numarası 1.788). İşaretler 1951'de başlıyor
  (en eskisi 7746, 28 Şubat 1951); 1951 öncesine tarihli 6.052 TBMM atfının hiçbirinde işaret yok. Yani 1921–1950 için bu
  kontrol hiçbir şeyi doğrulamıyor: o dönemde (588'inki dışında) mükerrer bulunmadığının dayanağı yalnızca arşiv yoklaması,
  1–100 arası sayılar için ayrıca İlk 100 Sayı derlemesi (3.2). Kalan 11 kaydın hepsi açıklandı. 7'sinde TBMM
  kaydındaki sayı ya da tarih yanlış yazılmış ve doğru sayının mükerreri listede var: 19237 → 19327, 23792 → 23729,
  274168 → 27418, 30386 → 30836, 21471 ve 21417 → 23417; 7259 sayılı Kanunun kaydındaki «31.10.2020, 31321» ise 31.12.2020
  tarihli 31351'in 2. mükerreri (resmî sitenin `20201231M2.htm` sayfası). 4'ünde mükerrer işareti hatalı, kanun ya da karar
  asıl sayıda yayımlanmış: 17914 (3.1), 23920 (658 sayılı TBMM Kararı asıl sayının ilk sayfasında), 27470 (5946 sayılı
  Kanun) ve 27533 (5957 sayılı Kanun); son ikisi resmî sitenin 22.01.2010 ve 26.03.2010 günlük sayfalarında asıl sayının
  içindekiler listesinde, o günlerin mükerrer sayfası yok.
- **2000–2013 asıl sayıları ve mükerrerleri tek kaynaklı.** 27.06.2000–31.12.2013 arasındaki 4.777 asıl sayının tarihi ve
  aynı dönemin 496 mükerreri (432 sayıya ait) resmî günlük sayfalardan geliyor; asıl sayılardan yalnızca 24092–24095
  (27–30 Haziran 2000), mükerrerlerden yalnızca dördü (24093, 24095, 24273 ve 24281'inkiler) arşiv PDF'lerinin künyesiyle de
  karşılaştırıldı. Sayı sırası kesintisiz ve TBMM kayıtları ile Resmî Gazete atıflarıyla genel uyum çok yüksek (3.2), ama
  2014 sonrasındaki gibi gün gün ikinci bir kaynak yok; TBMM kayıtlarındaki mükerrer işaretleri de bu 432 sayının yalnızca
  41'ine denk geliyor. Kasım 2026'daki `mukerrer_tara` yoklaması (3.1) ikinci bir kaynak değildir: aynı sitenin `M1`, `M2` …
  adreslerinin var olup olmadığına bakar, sayfa içeriğini okumaz. Asıl sayıların 27.06.2000–01.11.2026 günlük sayfaları da
  yerel tamamlamada toplu olarak yeniden okunmadı; künyeleri ilk derlemede bir web-getirme aracı üzerinden yapılan okumaya
  dayanıyor (`kanit/gunluk_sayfalar.json.gz`). Doğrudan okunup kaydı tutulan ana sayfalar 2–18 Kasım 2026'nınkilerdir
  (`kanit/yerel_gunluk.jsonl.gz`).
- **Lexpera karşılaştırması 31 Ekim 2026'da bitiyor.** 33416 ve sonraki sayılar yalnızca resmî günlük sayfaya dayanıyor.
- **Ayrı numaralı ekler listede yok.** Liste numaralı sayıları ve mükerrerleri kapsar. "İlk 100 Sayı" derlemesinde,
  10–27 Eylül 1923 arasında çıkan ve kendi numarası (1–6) olan 6 "Gayr-ı Resmî Kısım (Resmî Ceride'nin İlavesi)" var;
  bunlar arşivde ayrı dosya olarak bulunmadı ve listeye alınmadı. Sonraki yıllarda başka ayrı numaralı ek olup
  olmadığı araştırılmadı.
- **Yayımlanmayan günler.** Gazetenin çıkmadığı günler listede yer almaz. 2000 sonrası için resmî sayfa "yayımlanmamaktadır"
  diyor; daha öncesi için yalnızca sayı numarasının kesintisiz olması, hiçbir asıl sayının eksik olmadığını gösteriyor.
- **Basılı bilgisi eksik ya da hatalı künyeler** (tarihleri gerekçeleriyle `not` kolonunda). Bunlarda tarih künyedeki
  basılı tarihten değil, künyedeki gün adı ile komşu sayılardan çıkıyor; hepsinde tek bir gün mümkün:
  - 244 (14 Aralık 1925): künyede, Osmanlıca aslında da, «Pazartesi, 14 Teşrinievvel 1341 / 27 Rebiülahir 1344» basılı;
    iki ay adı da baskı hatası (doğrusu 14 Kânunuevvel 1341 / 27 Cemaziyelevvel 1344; 243 ve 245'in künyelerinde 26 ve 28
    Cemaziyelevvel 1344 basılı). 243 13 Aralık, 245 15 Aralık tarihli; 14 Aralık 1925 pazartesi.
  - 293 (9 Şubat 1926): künyede gün rakamı yok, yalnızca «Salı, Şubat 1926»; Osmanlıca aslında da (`arsiv/293.pdf`) öyle.
    292 8 Şubat, 294 10 Şubat tarihli; üç TBMM kanun kaydı (727, 728, 729) da 9 Şubat 1926 diyor. `tarih_kaynagi` TBMM
    kaydı olarak kalan tek satır bu.
  - 588'in mükerreri: Osmanlıca künyede yalnızca «Pazar, Mayıs 1927». 589 sayı 3 Mayıs'ta çıktığından tek olasılık 1 Mayıs.
  - 1054 ve 1056 (1 ve 3 Aralık 1928, Latin harfli ilk sayılar): künyede gün rakamı basılı değil, yalnızca
    «Kânunievel 1928, Cumartesi» ve «Kânunievel 1928, Pazartesi». Komşu sayılar arasında bu gün adlarına uyan tek gün var.
  - 8489: gün rakamının ikinci hanesi baskıda kırık. Künyedeki «Pazartesi» ve komşu sayılar 24 Ağustos 1953'ü verir.
  - 14490: künye «23 Mart 1973 Çarşamba» gibi okunuyor, ama sayı sırası ve gün adı 28 Mart 1973'ü gösteriyor. İlk derlemede
    baskı hatası sayılmıştı; yüksek çözünürlükte bakınca gün rakamının ikinci hanesi kırık bir 8 çıktı (üst yarısı kapalı bir
    halka, alt yarısının solu çıkmamış; aynı satırdaki 1973'ün 3'üne benzemiyor).
  - 10480, 15890 ve 16168 (yıl denetimi sırasında rastlandı): 10480'in künyesi «11 Nisan 1960» gibi okunuyor (14'ün
    4'ünden yalnızca dikey çizgi çıkmış), 15890'ınkinde gün rakamının ikinci hanesi okunamıyor («2. Mart 1977»),
    16168'inkinde de («1. Ocak 1978»; hane mürekkeple dolmuş). Künyelerdeki gün adları (Perşembe, Cumartesi, Cuma) ve komşu
    sayılar 14 Nisan 1960, 26 Mart 1977 ve 13 Ocak 1978'i veriyor. İlk derlemenin görsel okuması da günü gün adına göre
    seçmişti; bu üç satırın `tarih_kaynagi` değeri ilk derlemedeki gibi «arşiv PDF künyesi (görsel okuma)» olarak kaldı (8489
    ve 14490'ınki «künyedeki haftanın günü + komşu sayılar»). Gün rakamları ayrıca taranmadı: liste tarihi, künyesinde gün
    adı yanlış basılmış 7 sayı (3.2) dışında, künyedeki gün adıyla tutuyor, ama gün rakamı kırık olup açıklaması düşülmemiş
    başka künyeler olabilir. İkinci turda rastlanıp açıklama düşülmeyenler: 14118'de gün rakamı kırık ama üç okuyucu da doğru
    okudu; 17738'de beş okuyucudan ikisi, 16740, 16758, 17253 ve 17739'da okuyuculardan biri gün rakamını okuyamadı
    (`gun_rakami`; 17738'in satırındaki yıl açıklaması, gün rakamının ikinci hanesinin de büyük ölçüde dolu olduğunu
    geçerken belirtiyor, ama gün için ayrı bir açıklama yok). İlk derlemenin okuyucu notları
    (`kanit/gorsel_okumalar.json.gz`) bunlardan başkalarını da gösteriyor: tarihi görsel okumadan gelen ve `not`u boş 41
    künyede okuyucu, gün rakamının baskısı ya da okunuşu için bir çekince yazmış (silik, lekeli, kırık, bulanık; bazılarında
    iki rakam arasında gün adına göre seçim: ör. 15900 «3 ya da 5», 16470 «5 ya da 6», 9330 «42 gibi»). Tarih kaynağı
    olan 1.828 okumanın 46'sı da «medium» (orta) güvenle verilmiş; 33'ünün `not`u boş. Bu 41 ve 33 künyenin hepsinde komşu
    sayılar arasında basılı gün adına uyan tek bir gün var ve liste o günü veriyor. İlk derlemenin görsel okumalarından,
    geçersiz 24 kayıt (`kanit/README.md`) dışında, satırının `not`u boş üç okuma da listeyle tutmuyor: 6149'un
    okuması «3 Kasım 1945» (okuyucu, basılı PAZARTESİ'nin 5 Kasım'a uyduğunu not etmiş), 12853'ünkü «20 Mart 1963»
    (okuyucu, yılın sayı sırasıyla çeliştiğini not etmiş), 18056'nın mükerrerininki sayı numarası olarak «18356».
    Üçünde de liste doğru: PDF'in metin katmanında «5 K A S I M 1945 PAZARTESİ», «20 MART (1968» ve «Sayı : 18056» var;
    12853'ün künyesini ikinci turdaki kör okuma da «20 MART 1968» okudu (aşağıda).
  - Yılı yanlış basılmış beş sayı: 81 («7 Kânunusani 1340», doğrusu 1341 = 1925; Osmanlıca aslının arşiv nüshasında basılı
    yıl elle çizilip yanına 1341 yazılmış, çizilen yılın son hanesi mürekkep lekesinin altında, «1340» resmî çevriyazıdaki
    okuma), 8530 («10 Ekim 1952», doğrusu 1953), 8585 («17 Aralık 1593», doğrusu 1953), 12830 («19 Şubat 1969», doğrusu
    1968), 13823 («30 Nisan 1970», doğrusu 1971). Gün, ay ve gün adı künyeden; yıl önceki ve sonraki sayıların
    tarihlerinden kesin, gün adı da yalnızca o yılda tutuyor.
  - Yılı hiç basılmamış yedi sayı: 3319 («2 Haziran, Salı»; 1936), 8099–8103 (2, 3, 5, 6, 7 Mayıs 1952; art arda beş sayı)
    ve 23494 («15 Ekim, Perşembe»; 1998).
  - Yılın bir ya da iki hanesi kırık, aşınmış ya da mürekkeple dolmuş otuz yedi sayı; yıl başka bir yıl gibi okunuyor ya
    da okunamıyor. 1940–1943 arasındaki on dört künyede 4 rakamının ince çizgileri çıkmamış (çoğunda yalnızca dikey çizgi),
    yıl «1910», «1911», «1912», «1913» gibi okunuyor: 4658, 4676, 4705, 4784, 4932, 4933, 4946, 4973, 5012, 5180, 5248, 5267,
    5377, 5408. 1943'teki üç künyede son hane (3) mürekkeple dolmuş, «1948» gibi okunuyor: 5303, 5310, 5551. On bir künyede
    bir ya da iki hane okunamıyor: 5470, 5590, 6608, 6631 (hane kırık) ve 17060, 17224, 17253, 17724, 17738, 17739, 17826
    (1980–1982; hane mürekkeple dolmuş). 1962 ve 1964'teki dört künyede 6 rakamı aşınmış, 5 gibi görünüyor («1952»,
    «1954»): 11004, 11049, 11851, 11892. Tek tek: 2002 («1532» gibi; 9 kırık), 3933 («1933» gibi; 8'in ince çizgileri
    çıkmamış), 11786 («1961» gibi; 4 kırık), 16296 («1976» gibi; 8 mürekkeple dolmuş), 16758 («1879» gibi; 9 mürekkeple
    dolmuş).
  - **Bu listenin ölçütü ve sınırı.** Kırık ya da dolmuş bir hane için açıklama, beklenen tarihi bilmeyen üç okuyucudan en
    az ikisi künyeyi (2600 piksel genişlikteki görüntünün %100 boyutunda) listedeki yıl olarak okuyamadıysa düşüldü (3.1).
    Bir okuma, yıl alanına ya da okuyucunun kendi yazdığı tarih satırına listedeki yıl yazılmadıysa «okuyamadı» sayıldı
    (on iki künyede en az bir okuyucu tarih satırına «19.2» gibi okunamayan bir hane yazıp yıl alanına listedeki yılı
    girmişti; son bağımsız denetim bunu yakaladı, ölçüt iki alana birden uygulandı ve 11004, 17060, 17224, 17253, 17724 ile
    17739 bu yüzden açıklama aldı). Hanesi kusurlu olduğu hâlde okuyucuların çoğunun
    doğru okuduğu künyelere açıklama düşülmedi. İkinci turda en az üç okumayla böyle kalan 50 künye var: ikinci okuyucunun açıklama
    önerdiği 34'ü (ör. 1954'te 4 rakamı zayıf çıkmış 8604, 8839, 8856; 1973'te 3 rakamı dolmuş 14528, 14574, 14633;
    1979–1982 arasında 9 ya da 8 rakamı mürekkeple dolmuş dokuz künye; yerel tamamlamada düşük çözünürlükte «19?4» okunan
    11865) ile kör okuyucunun yılı belirsiz bulup ikinci okuyucunun açıklama önermediği 16'sı (ör. 4853, 16740). Kör
    okuyucunun «hasarlı ama okunuyor» dediği 113 künye tek okumada kaldı. İlk turda açıklama düşülüp bu ölçütle kaldırılan
    bir künye var (11007: yıl alanına üç okuyucu da «1962» yazdı; tarih satırına yalnızca son incelemenin kör okuyucusu «19?2»
    yazdı, yani okuyamayan üçte bir). Hepsinin okumaları `kanit/yerel_yil_okumalari.json.gz` dosyasında
    (`karar`, `ikinci_tur`, `ek_kor_okumalar`); başka bir eşik uygulamak isteyen oradan yeniden sayabilir. Liste tarihi
    yılıyla birlikte OCR'da ya da yerel tamamlamanın okumalarında çıkan 23.525 künyeye ise yıl denetiminde topluca bakılmadı;
    yalnızca tek tek ele alınanlara bakıldı: okuma kayıtlarında yıl için kuşku belirtilmiş 7 künye (4107, 5180, 5476, 6657,
    11865, 12853, 16112) ikinci turda, 14490, 23494 ve liste tarihinin gövde metninde geçtiği 14 sayı birinci turda (3.1).
    Bunlardan 5180 (kırık hane) ve 23494 (yıl basılı değil) yukarıdaki listede; baskısı kusurlu olup OCR'ın ya da okuyucunun
    yine de doğru okuduğu öbür künyeler bu listede yoktur.
- **Künye görüntüleri depoda değil.** İlk derlemenin 24.450 künye görüntüsü (~910 MB) ve yerel tamamlamada üretilen 427
  künye görüntüsü (420 büyük dosya + yeniden bakılan 7 küçük dosya), boyutları nedeniyle depoya konmadı (bkz. [`kanit/README.md`](kanit/README.md)). Her biri ilgili arşiv PDF'inin
  ilk sayfasından yeniden üretilebilir.

## 3. Kapatılanlar ve sorun olmadığı anlaşılanlar

### 3.1 Yerel tamamlama (17–18 Kasım 2026)

**Yöntem.** `yerel_tamamla.py indir_oku` 418 büyük PDF'i (toplam 8,6 GB) saniyede bir istekten seyrek olacak şekilde
sırayla indirdi, ilk sayfanın metnini ve künye görüntüsünü çıkardı. 384 künyede karar otomatik verildi (kural 4.2'de),
34'ü görüntüden okundu. Bundan bağımsız olarak 418 künyenin hepsi, dosya adını, sayı numarasını ve beklenen tarihi
bilmeyen okuyuculara (Claude) rastgele adlarla **kör** olarak okutuldu: 290 künye bir, 118'i iki, 10'u üç okuyucu
tarafından (556 okuma). Tam okunabilen bütün tarihler, bütün sayı numaraları ve bütün mükerrer ibareleri listeyle aynı;
tek istisna 15873'ün yanlış basılmış numarası (aşağıda). İki künyede hiçbir okuyucu bir alanı tam okuyamadı: 11865'te üç
okuyucu da yılın bir hanesini («25 KASIM 19?4, ÇARŞAMBA»), 17654'ün mükerrerinde üç okuyucu da sayı numarasının iki hanesini
(«17??4»). 11865'in tarihi metin katmanından ve sayı sırasından kesin (25 Kasım 1964; yıl denetiminin ikinci turunda
PDF'in 2600 piksel genişlikteki görüntüsünü okuyan üç okuyucu yılı «1964» okudu); 17654'ün mükerrerinin numarası PDF'in
metin katmanında («Sayı : 17654») ve dosya adında. Okumalar
[`kanit/yerel_okumalar.jsonl.gz`](kanit/) ve [`kanit/yerel_kor_okumalar.json.gz`](kanit/) dosyalarında.

- **Tahminî 158 tarih.** 149'unda komşu sayılardan yapılan tahmin künyeyle aynı çıktı. 9'unda künye farklı bir tarih verdi
  ve liste düzeltildi:

  | Sayı | Tahmin | Künyedeki tarih |
  |---:|---|---|
  | 2900 | 11 Ocak 1935 | 10 Ocak 1935 Perşembe |
  | 12791 | 2 Ocak 1968 | 4 Ocak 1968 Perşembe |
  | 13373 | 12 Aralık 1969 | 10 Aralık 1969 Çarşamba |
  | 13503 | 27 Mayıs 1970 | 26 Mayıs 1970 Salı |
  | 16641 | 19 Mayıs 1979 | 18 Mayıs 1979 Cuma |
  | 21683 | 30 Ağustos 1993 | 29 Ağustos 1993 Pazar |
  | 22266 | 23 Nisan 1995 | 22 Nisan 1995 Cumartesi |
  | 23321 | 23 Nisan 1998 | 22 Nisan 1998 Çarşamba |
  | 23995 | 18 Mart 2000 | 20 Mart 2000 Pazartesi |

- **Atıftan tarihlenen 105 sayı.** 61'i TBMM kaydından, 22'si sonraki Resmî Gazete metinlerindeki atıftan, 22'si aynı
  numaralı mükerrerin künyesinden tarihlenmişti. 105'inin de künyesi aynı tarihi verdi; atıf kaynaklı hiçbir tarih değişmedi.
- **155 mükerrer.** Hepsinin künyesinde dosya adındaki sayı numarası ve kendi satırında «Mükerrer» ibaresi var, tarihleri
  asıl sayınınkiyle aynı. Künyede basılı sıra dosya adındaki sırayla tutuyor: `_1` dosyalarında yalnızca «Mükerrer», tek `_2`
  dosyasında (23923, 31 Aralık 1999) «2. Mükerrer».
- **İş listesinde olmayan iki büyük dosya.** `arsiv/24273_1.pdf` ve `arsiv/24281_1.pdf` de 10 MB'tan büyüktü, ama bu iki
  mükerrer günlük sayfadan tarihlendiği için iş listesine girmemişti. İkisi de indirildi: künyeleri «30 Aralık 2000
  Cumartesi, Sayı: 24273, Mükerrer» ve «8 Ocak 2001 Pazartesi, Sayı: 24281, Mükerrer». İlki, günlük ana sayfada yanlış
  yazılan 24272 yerine 24273 numarasını da doğruluyor.
- **"17914 Mükerrer" sorusu.** TBMM kaydına göre 2766 sayılı Kanun 30.12.1982 tarihli 17914 sayılı Resmî Gazete'nin
  mükerrerinde yayımlandı. Arşivin yeniden yoklanması `17914_1.pdf` olmadığını (404), 17915'in ise tam iki mükerreri
  olduğunu gösterdi. `17915_1.pdf`'in künyesi «31 Aralık 1982 Cuma, Sayı: 17915, Mükerrer»; yani yanlış adlandırılmış bir
  "17914 Mükerrer" değil. Asıl 17914 sayısının ilk sayfası "Kanun No. 2766, Kabul Tarihi: 28/12/1982" metniyle başlıyor ve
  künyesinde mükerrer ibaresi yok. Sonuç: kanun asıl sayıda yayımlandı, TBMM'nin ikinci kaydındaki «Mükerrer» ibaresi hatalı.
- **15164.** Künye: «1 Mart 1975 Cumartesi, Sayı: 15164» (ilk sayfa: 1975 Bütçe Kanunu, Kanun No. 1868). TBMM kaydındaki
  03.03.1975 tarihi 15166'ya ait.
- **15873'ün künyesinde yanlış basılmış numara.** `arsiv/15873.pdf`'in künyesinde «9 Mart 1977 Çarşamba, Sayı: 15973»
  basılı. Tarih, 15872 (8 Mart) ile 15874 (10 Mart) arasındaki tek güne düşüyor; gerçek 15973 sayı 21 Haziran 1977 tarihli ve
  kendi künyesi var. TBMM'nin 2039–2066 arasındaki 17 kanun için verdiği "09.03.1977 No: 15973" kayıtları da bu yanlış basılı
  numarayı taşıyor. Listeye 15873 olarak, açıklamasıyla işlendi.
- **İlk derlemenin üç tarih hatası.** 6126, 10908 ve 11979'da OCR metninin gövdesinde geçen başka bir tarih, künyedeki
  tarihin yerine seçilmişti; liste tarihi künyede basılı gün adıyla tutmuyordu (10908 ve 11979 ayrıca komşu sayıyla aynı
  güne düşüyordu). Dosyalar yeniden indirildi, künyeler okundu:

  | Sayı | Eski | Künyedeki tarih |
  |---:|---|---|
  | 6126 | 7 Ekim 1945 | 6 Ekim 1945 Cumartesi |
  | 10908 | 15 Eylül 1961 | 16 Eylül 1961 Cumartesi |
  | 11979 | 20 Nisan 1965 | 19 Nisan 1965 Pazartesi |

  Bu hata türü için arşivdeki bütün asıl sayıların OCR metni (23.828 kayıt) yeniden tarandı: künye metnindeki ilk gün adı
  liste tarihiyle tutmayan, bu üçünden başka yalnızca bilinen 7 sayı (54, 77, 207, 259, 494, 635, 18223: künyede gün adı
  yanlış basılmış) ve 15303 çıktı (gün adı harf aralıklı dizildiği için OCR gövdedeki bir gün adını okumuş; künyede
  «22 Temmuz 1975 Salı», liste doğru). Artık art arda gelen hiçbir iki asıl sayı aynı tarihi taşımıyor; araç da bunu
  listeyi yazmadan önce denetliyor (4.2).
- **Künyesinde gün rakamı olmayan / ay adı yanlış basılmış dört sayı** (244, 293, 1054, 1056) yeniden indirildi ve
  künyelerine bakıldı; 244 ve 293'ün Osmanlıca asılları da (`arsiv/244.pdf`, `arsiv/293.pdf`) görüldü. Tarihleri değişmedi;
  ne basılı olduğu 2. bölümde ve `not` kolonunda.
- **Görsel okuması olmayan 11 küçük mükerrer** (8123, 14003, 16344, 16402, 16409, 16427, 17551, 17631, 23004, 23384,
  24022'nin mükerrerleri): 10'unun OCR metni asıl sayıyla aynı tarihi, gün adını, sayı numarasını ve «Mükerrer» ibaresini
  veriyor; 16409'unkinin görüntüsüne bakıldı («19 Eylül 1978 Salı, Sayı: 16409, Mükerrer»). Böylece kaynağı "asıl sayının
  tarihi" olan 628 mükerrerin hepsinin kendi künyesi de asıl sayıyla aynı günü gösteriyor.
- **Künyelerdeki yıl denetimi.** İlk derleme, OCR'ın okuduğu gün ve aya yılı komşu sayılardan da verebiliyordu; künyesi
  görüntüden okunan sayılarda da okuyucu dosya adını ve beklenen tarihi biliyordu. Bu yüzden künyesinde yılı yanlış basılmış,
  basılmamış ya da kırık çıkmış sayılar açıklama düşülmeden (doğru) tarihlenmişti. Bağımsız incelemelerden biri dördünü buldu
  (81, 8530, 12830, 13823); bunun üzerine arşivdeki 24.091 asıl sayının hepsi için künyedeki yılın, beklenen tarihi bilmeyen
  bir okumayla doğrulanıp doğrulanmadığına bakıldı. İki turda yapıldı:
  1. 22.652 sayıda liste tarihi, yılıyla birlikte, beklenen tarihi bilmeyen bir okumada geçiyor: PDF'in metin katmanı (OCR)
     ya da yerel tamamlamanın okumaları. Kalan 1.439 sayının 662'sinde yıl komşu sayılardan verilmişti; 777'sinde liste
     tarihinin tek dayanağı ilk derlemenin görsel okumasıydı (o okuma kör değildi ve tarih gün adıyla tutarsa kabul
     ediliyordu). İlk turda bu 777 sayı doğrulanmış sayılmıştı; üçüncü bağımsız inceleme bunun bir kör nokta olduğunu
     gösterdi, ikinci tur bunun için yapıldı.
  2. Bu 1.439 sayıdan görüntüsü olan 1.435'inin künye görüntüsü ikinci kez OCR'landı (tesseract): 662'den 407'sinde,
     777'den 466'sında liste tarihi yılıyla çıktı (873).
  3. Kalan 566 künye gözle okundu. Birinci tur (255 künye): 251'i rastgele adlarla, dosya adı ve beklenen tarih verilmeden
     okutuldu; görüntüsü olmayan 4'üne (7550–7553) PDF'ten bakıldı. 255'inde de gün, ay ve gün adı listeyle aynı; 239'unda
     okunan yıl da aynı (71'inde bir hane şüpheli), 5'inde yıl açıkça farklı, 8'inde yıl yok ya da okunamadı, 3'ünde kırık
     hane yüzünden farklı okundu. İkinci bir bağımsız denetim iki künye daha buldu: 23494'te liste tarihi künyede değil ilk
     sayfadaki bir yazının cümlesinde geçiyordu (künyede yıl yok); 11049'da ilk derlemenin okuyucusu künyede «1952» okuyup
     yılı gün adına göre düzeltmişti. Liste tarihinin gövde metninde geçtiği saptanan öbür 14 sayının künye görüntüsüne
     bakıldı (hepsinde yıl basılı; bu 14 sayının numaraları kayda geçirilmedi). Birinci turda toplam 34 künyenin PDF'i
     yeniden indirilip yüksek çözünürlükte bakıldı.
  4. İkinci tur (374 künye): ikinci OCR'ın doğrulamadığı 311 görsel okumanın birinci turda bakılmamış 307'si, birinci turda
     yılı «bir hane şüpheli» okunup yüksek çözünürlükte bakılmamış 60 künye ve okuma kayıtlarında yıl için kuşku belirtilmiş
     7 künye (4107, 5180, 5476, 6657, 11865, 12853, 16112). Hepsinin PDF'i tek tek yeniden indirildi; 2600 piksel
     genişlikteki künye görüntüsünü önce yalnızca görüntüyü gören bir okuyucu okudu (kör), sonra liste tarihini bilen ikinci
     bir okuyucu görüntüye bakarak karar verdi. Hiçbir künye liste tarihiyle çelişmedi (birkaç künyede gün rakamı kırık ya da
     mürekkeple dolmuş; okuyucuların çoğunun okuyamadığı üçüne, 10480, 15890 ve 16168'e, açıklama düşüldü). İkinci okuyucu
     54 künye için yıl açıklaması önerdi; 30 künyede iki okuyucu ayrıştı.
  5. Eşik okuyucudan okuyucuya değiştiği için (özellikle mürekkeple dolmuş 1973–1986 künyelerinde) tek bir ölçüt uygulandı:
     açıklama önerilen ya da okuyucuların ayrıştığı bütün künyeler ile birinci turda «kırık hane» açıklaması düşülmüş 18
     künye, yalnızca görüntüyü gören iki okuyucuya daha okutuldu; **beklenen tarihi bilmeyen üç okuyucudan en az ikisi
     künyeyi okuma boyutunda listedeki yıl olarak okuyamadıysa** satıra açıklama düşüldü. Bir okuma, yıl alanına ya da
     okuyucunun kendi yazdığı tarih satırına listedeki yıl yazılmadıysa «okuyamadı» sayıldı. Buna göre ikinci turun 54
     önerisinden 20'si kaldı; okuyucuların ayrıştığı 30 künyeden yalnızca birine (17060) açıklama düşüldü; birinci turun 18
     açıklamasından 17'si kaldı, biri (11007) kaldırıldı, 11004'ünki «kesin okunamıyor» diye yeniden yazıldı.
  Sonuç 2. bölümdeki 49 sayı: 5'inde yıl yanlış basılmış, 7'sinde hiç basılı değil, 37'sinde bir ya da iki hane başka bir
  rakam gibi görünüyor ya da okunamıyor. 81'in Osmanlıca aslında basılı yıl elle çizilip yanına «1341» yazılmış (çizilen
  yılın son hanesi mürekkep lekesinin altında); resmî çevriyazıda yıl «1340». Aynı çalışmada 14490'ın künyesindeki gün
  rakamının kırık bir 8 olduğu görüldü (ikinci OCR «28» okumuştu), 10480, 15890 ve 16168'de kırık ya da mürekkeple dolmuş gün
  rakamına rastlandı (aynı ölçütle açıklama düşüldü). Hiçbir liste tarihi değişmedi; yalnızca `not` kolonu değişti. Bütün okumalar ve her künye için
  kaç okuyucunun yılı okuyamadığı [`kanit/yerel_yil_okumalari.json.gz`](kanit/) dosyasında. Sınırları 2. bölümde: yılı
  OCR'da ya da yerel tamamlamanın okumalarında doğru çıkan 23.525 künyeye, tek tek ele alınan birkaçı (5180 ve 23494 dahil)
  dışında, yıl denetiminde topluca bakılmadı. Kör okumaların (yukarıdaki 418 künye) ve yıl denetiminin araçları depoda
  yok: okuyucu oturumları (Claude), ikinci OCR (tesseract), 2600 piksellik künye görüntülerinin üretimi ve hakemlerin
  gerekçelerinde andığı türetilmiş karşılaştırma görüntüleri (kırpıntı, büyütme) `scripts/` altında bulunmaz; depoda
  yalnızca sonuçlar (`kanit/`) var. Yıl denetiminden çıkan `not` değişiklikleri CSV elle düzenlenip `yeniden_yaz`
  çalıştırılarak işlendi.
- **TBMM kayıtlarındaki «M.» kısaltmalı mükerrer işaretleri.** İlk derlemenin mükerrer karşılaştırması yalnızca açık yazılmış
  «Mükerrer» işaretlerine bakmıştı; kısaltılmış 132 kayıt da eklenince karşılığı listede olmayan 8 kayıt daha çıktı. Beşi
  sayı ya da tarih yazım hatası; üçünde (23920, 27470, 27533) işaret hatalı: karar ve kanunlar asıl sayıda (2. bölüm).
  5946 ve 5957 sayılı Kanunlar için resmî sitenin 22.01.2010 ve 26.03.2010 günlük sayfalarına, 7259 sayılı Kanun için
  31.12.2020'nin mükerrer sayfalarına 18 Kasım 2026'da bakıldı. Bu bakışların kaydı (indirilen sayfalar ve HTTP
  durumları: iki günün ana sayfası 200, `M1` sayfaları 404; 31.12.2020'nin `M1`–`M5` sayfaları ve 31.10.2020 ana sayfası
  200) yalnızca git'e girmeyen `yerel/ek_inceleme/` klasöründe; depoda yok.
- **12 Haziran 2010'daki "27609 Mükerrer" duyurusu.** O günün ana sayfasında «12/6/2010 Tarihli ve 27609 Sayılı Mükerrer
  Resmi Gazete'de, 5996 Sayılı … Kanunu Yayımlanmıştır» notu ve eski sunucuya (rega.basbakanlik.gov.tr) giden bir bağlantı
  var. Resmî sitede `20100612M1.htm` yok (404). 5996 sayılı Kanun, 13 Haziran 2010 tarihli 27610 sayıda yayımlandı (o günün
  resmî sayfası ve TBMM kaydı). Listeye mükerrer eklenmedi. Eski sunucudaki bağlantı ilk derlemede açılmamıştı
  (`kanit/gunluk_sayfalar.json.gz`: «other host, not fetched»); 18 Kasım 2026'da denendi: `rega.basbakanlik.gov.tr` adı artık
  çözülmüyor, Internet Archive'da da bu adresin kaydı yok. Böyle bir mükerrerin hiç çıkmadığı, doğrudan görülmüş bir şey
  değil, duyurduğu kanunun ertesi günkü 27610 sayıda yayımlanmış olmasından çıkarılan bir sonuçtur. İlk derlemenin aynı
  kaydının `error` alanı ise tersini söylüyor («A mukerrer for this date likely exists but was not reachable»); listedeki
  karar o kayda değil, bu çıkarıma dayanıyor.
- **Mükerrer sayfalarındaki iki yanlış numara.** 29.12.2001 mükerrer sayfasında sayı 27625 (doğrusu 24625), 08.03.2003
  mükerrer sayfasında 25034 (doğrusu 25042) yazıyor. Liste doğruydu; açıklamalar `not` kolonuna ve
  [`data/resmi_site_duzeltmeleri.json`](data/resmi_site_duzeltmeleri.json) dosyasına eklendi.
- **Yeni sayılar.** 2–18 Kasım 2026 arasındaki 17 sayı (33418–33434) günlük sayfalardan eklendi; yoklandıkları anda bu
  günlerin hiçbirinde mükerrer sayfası yoktu. 2–17 Kasım günleri `mukerrer_tara` yoklamasının da içinde; 18 Kasım'ın
  sayfaları ise o gün içinde yoklandı (ilk kez 01.08'de, son kez 14.23'te; yalnızca ilki `kanit/yerel_gunluk.jsonl.gz` dosyasında
  kayıtlı) ve günlük yoklama 17 Kasım'da bitiyor: 18 Kasım'da daha geç
  yayımlanabilecek bir mükerrer listede yoktur, bir sonraki `yeni` çalıştırması ekler. `yeni` komutunun siteden okuduğu künyeler ve mükerrer yoklamaları artık
  `kanit/yerel_gunluk.jsonl.gz` dosyasına kaydediliyor.
- **Günlük mükerrer sayfalarının yeniden yoklanması.** `mukerrer_tara` 27 Haziran 2000'den 17 Kasım 2026'ya her günün
  `M1`, `M2` … sayfalarını doğrudan siteden yokladı (yalnızca 2000–2013 değil, bütün günlük sayfa dönemi; yapay zekâ
  ajanı ya da ara katman olmadan, her gün için ilk 404'e kadar). 18 Kasım 2026'da tamamlandı: 9.640 günün 9.640'ı yoklandı,
  hata kalmadı; sitede 1.219 mükerrer sayfası var, listede bu dönemin günlük sayfalarına dayanan mükerrer de 1.219 ve her
  günün adedi listedekiyle aynı. Yoklamanın tek uyarısı, yukarıda açıklanan 12 Haziran 2010 duyurusu (ana sayfada bağlantı
  var, `M1` sayfası yok). Özet `data/dogrulama_raporu.json` içinde (`mukerrer_yoklama`); ham sonuç
  (her gün için sitede bulunan mükerrer sayfası adedi) `kanit/yerel_mukerrer_yoklama.json.gz` dosyasında.
- **Arşiv mükerrer dosyalarının yeniden yoklanması.** `arsiv_mukerrer_tara` 1–24095 arasındaki her sayı numarası için
  `arsiv/N_1.pdf`, `N_2.pdf` … adreslerini ilk 404'e kadar doğrudan siteden yokladı (tek tek, saniyede bir istekle; ilk
  derlemedeki gibi paralel değil). 18 Kasım 2026'da tamamlandı: 24.095 sayı numarasının 24.095'i yoklandı, hata kalmadı;
  arşivde 786 mükerrer dosyası var, listede bu sayı aralığındaki mükerrer de 786 ve her sayının adedi listedekiyle aynı.
  17914 ve 23920 için arşivde mükerrer dosyası yok (TBMM kayıtlarındaki işaretler hatalı, 2. bölüm); 17915'in iki
  mükerreri var. Bu 786'nın 784'ü 27 Haziran 2000'den önceki tarihli; kalan ikisi (24093 ve 24095'in mükerrerleri, 28 ve
  30 Haziran 2000) günlük sayfa dönemine düştüğü için yukarıdaki 1.219'un da içinde. İki yoklama birlikte listedeki 2.003
  mükerrerin hepsini kapsıyor (784 + 1.219). Özet ve ham sonuç (her sayı numarası için arşivde bulunan mükerrer dosyası
  adedi) günlük yoklamayla aynı yerde: `data/dogrulama_raporu.json` ve `kanit/yerel_mukerrer_yoklama.json.gz`.
  Yoklama yalnızca dosya adedini karşılaştırır: arşive hiç yüklenmemiş bir mükerrer varsa bununla da bulunamaz.

### 3.2 Daha önce kapatılanlar

- **1921–1923 arasındaki yaklaşık 26 aylık (784 günlük) boşluk gerçek.** 21. sayı 18 Temmuz 1921, 22. sayı 10 Eylül 1923
  tarihli; "İlk 100 Sayı" derlemesi de aynı numaralandırmayı veriyor. Yayının bu dönemde savaş nedeniyle durduğu
  ([Vikipedi: Resmî Gazete](https://tr.wikipedia.org/wiki/Resm%C3%AE_Gazete_(T%C3%BCrkiye))) genel kabul görüyor.
- **İlk 100 sayı resmî derlemeyle birebir aynı.** Cumhurbaşkanlığı İdari İşler Başkanlığı'nın *T.C. Resmî Gazete İlk 100
  Sayı* (Cilt I–II) derlemesinin içindekiler bölümündeki 100 tarihin 100'ü listeyle aynı
  ([`data/ilk100_fihrist.json`](data/ilk100_fihrist.json)). Derlemede bu dönem için mükerrer yok, listede de yok.
- **"Arşivde yanlış adlandırılmış dosyalar" iddiası geri çekildi.** Bulutta dosyalar paralel indirilirken bazıları yanlış
  sayı numarasıyla eşleştirilmişti. Şüpheli 106 dosya tek tek yeniden indirildi: 73'ü açıldı ve künyeleri dosya adlarıyla
  tuttu, 32'si 404 döndü (o adla dosya yok), 15389 ise 10 MB'ı aştı (yerel tamamlamada okundu). Bu yüzden 22494 ve 23942'nin
  var sanılan mükerrerleri listeden çıkarıldı, başka bir sayının dosyasına bağlanmış 17 satırın bağlantısı doğru dosyaya
  döndü (commit `88fbd6b`; iletisinde «19 satır» yazıyor, CSV farkı 17 veriyor). Aynı commit'te, `_1` dosyası 10 MB'ı aşan
  10 sayının (17915, 17949, 18112, 18237, 18267, 21400, 22096, 22880, 24004, 24030; bu dosyalar yeniden indirilen 106
  dosyanın arasında değil) iki mükerrerinin (20 satır) `_1` ve `_2` bağlantıları da dosya adındaki sıraya göre yer
  değiştirdi. Yerel tamamlamada indirilen 420 büyük dosyanın künyeleri de dosya adlarıyla tutuyor (15873'teki baskı hatası dışında).
- **Künyesinde gün adı tarihle tutmayan 7 sayı:** hepsinde basılı tarih doğru çıktı.
  - 54 ve 77: İlk 100 Sayı derlemesiyle doğrulandı.
  - 259 ve 635: TBMM kayıtlarıyla doğrulandı.
  - 494 ve 18223: gün adı bir önceki sayınınki olarak kalmış (önceki ve sonraki sayıların künyeleri doğru).
  - 207: gün adının gösterdiği gün (2 Kasım 1925), bir sonraki sayının tarihinden (1 Kasım) sonraya düşüyor.
- **OCR'ın haftanın gününü okuyamadığı 5 sayı** (8244, 8257, 8266, 8290, 8291): künye görüntülerine bakıldı, basılı gün
  adları tarihlerle tutuyor (okunan gün adları `not` kolonunda ve `kanit/kunye_duzeltmeleri.json.gz`'de).
- **Resmî sitedeki hatalar** düzeltildi ve açıklandı (ör. 18.11.2000 sayfasında 24334 yazıyor, doğrusu 24234). Liste
  için [README](README.md#resmî-kaynaktaki-tutarsızlıklar).
- **İlk derlemenin günlük sayfa kayıtlarındaki hata notları.** `kanit/gunluk_sayfalar.json.gz`'de altı günün kaydında
  `error` alanı var. Üçü bu belgede ya da README'de anlatılıyor (30.12.2000 ve 22.01.2001'deki yanlış numaralar, 12.06.2010
  duyurusu). Öbür üçü listeyi etkilemiyor: 26.10.2001'de mükerrerin üç parçalı PDF'inden `20011026M1-2.pdf` 10 MB'ı aştığı
  için açılamadı (mükerrer `M1` sayfasından okundu); 16.06.2009 ve 25.08.2009 günlük sayfalarının mükerrer satırında, başka
  bir güne ait `20090506M1.htm`'ye giden ve yerel bir diske (`file:///E:/…`) işaret eden bozuk bir bağlantı var (06.05.2009
  sayfasında da, `error` notu olmadan). Bu dört günün `M1` sayfası okundu ve asıl sayının numarasını taşıyor; listede her
  birinin bir mükerreri var, Kasım 2026'daki `mukerrer_tara` yoklaması da her birinde bir mükerrer sayfası buldu.
- **Lexpera'daki tek fazlalık** (15.03.2018, "30363 1. Mükerrer") yanlış numaralı bir kayıt: o günün resmî mükerrer sayfası
  30361'e ait ve listede öyle yer alıyor.
  2014'ten 31 Ekim 2026'ya asıl sayılar Lexpera'yla aynı (Lexpera'nın 31.10.2026 sayfasında 33416 henüz yoktu; 04.08.2016
  sayfasındaki "2016084" kaydı bir ayrıştırma hatası); resmî sitede Lexpera'da hiç olmayan 19 mükerrer nüsha (19 güne ait) var.
- **Bağımsız atıflarla genel uyum** (`scripts/atif_dogrula.py`; atıflar `kanit/atiflar.json.gz`'de). Bu sayılar liste her
  yazıldığında yeniden hesaplanır ve [README](README.md#yöntem)'de güncel hâliyle yer alır. Yerel tamamlamadan sonra: tarihi
  künyeden ya da günlük sayfadan gelen ve TBMM kaydı bulunan 5.177 sayının 5.081'inde tarih aynı; farklı 96 sayının 84'ünde
  TBMM kaydında tek haneli bir yazım hatası var (15164 ve künyesinde numarası yanlış basılmış 15873 bunların içinde; TBMM
  ikincisini künyedeki yanlış numarayla, 15973 diye anıyor), 12'si
  sayı sırasıyla bağdaşmıyor. Resmî Gazete metinlerindeki atıflarda (2019–2026 derlemi) 4.234 sayının 4.199'u aynı; kalan
  35'in 34'ü sayı sırasıyla bağdaşmıyor, biri (28441) sıraya sığıyor ama resmî günlük sayfanın tarihiyle çelişen bir yazım
  hatası. Arşiv
  PDF'lerinin ilk sayfalarındaki atıflarda 442 sayının 419'u aynı, kalan 23'ü sayı sırasıyla bağdaşmıyor.

## 4. Listeyi güncel tutma ve araç

### 4.1 Gerekenler ve komutlar

- resmigazete.gov.tr'ye doğrudan erişim (yurt dışından site açılmıyor),
- Python 3.9+,
- yalnızca arşiv PDF'i okunacaksa (`indir_oku`) poppler (`pdftotext`, `pdftoppm`, `pdfinfo`; macOS'ta `brew install poppler`,
  Debian/Ubuntu'da `apt install poppler-utils`) **ya da** `pip install pymupdf`; `yeni` için gerekmez,
- Windows'ta `python3` yerine `py` yazın.

```bash
git checkout main && git pull
python3 scripts/yerel_tamamla.py baglanti        # erişim ve araç kontrolü, "TAMAM" demeli
python3 scripts/yerel_tamamla.py yeni --kuru     # listenin son gününden bugüne ne eklenecek, hiçbir şey yazmaz
python3 scripts/yerel_tamamla.py yeni            # yeni sayıları ve son 10 sayının geç yayımlanmış mükerrerlerini ekler
python3 scripts/build_artifact.py data/resmi_gazete_sayilari.csv site    # tek sayfalık HTML görünümünü yeniden üretir
```

`yeni` önce listede zaten olan son günü yeniden okuyup ayrıştırıcıyı sınar (o günün künyesi sitede hatalıysa geriye doğru en
çok 8 güne bakar); sayı numarası beklenen sıradan saparsa ya da bir sayfa hata döndürürse hiçbir şey yazmadan durur. Her
çalıştırmada listedeki son 10 sayının mükerrer sayfalarını da yeniden yoklar: bir günün mükerreri, o gün listeye
eklendikten sonra yayımlanmış olabilir. Listeye eklediği her günün (ve kanıt kaydı olmayan, listede zaten bulunan günlerin)
künyesini `kanit/yerel_gunluk.jsonl.gz` dosyasına kaydeder; öz-sınama için yeniden okuduğu günü ve yeni mükerrer çıkmayan
yoklamaları kaydetmez.
Gazetenin yayımlanmadığı bir günü ("bugün yayımlanmamaktadır" sayfası) atlar, o günün de mükerrer sayfalarını yoklar ve günü
kanıta bir kez yazar. Geçmiş bir günün ana sayfası sitede hiç yoksa (404; 27 Haziran 2000'den beri hiç olmadı) okunabilen
günleri işler ama uyarıyla ve sıfırdan farklı çıkış koduyla biter. Listeyi değiştirmediği çalıştırmalarda, önceki bir
çalışma çıktıları yazarken kesilmişse JSON'u, raporu ve README'yi onarır.

Güncellemeden sonra kendiliğinden değişmeyen, elle yazılmış sayıları yeniden üretilen README.md ile karşılaştırın:
`site/body.html`'deki elle yazılmış rakamlar (hangileri olduğu dosyanın başındaki HTML yorumunda yazılı; yıl aralığının
sonu, son sayı ve tarihi, üstteki adetler ve grafiğin y ekseni `site/app.js`'te veriden dolar) ve bu belgedeki o günün
hâlini veren sayılar (durum satırı ve 2. ile 3. bölümdeki sayımlar). README'nin üretiminde de elle tutulan kısımlar var:
künyesinde gün ya da ay kusurlu yayınların listesi (`scripts/render_readme.py` → `GUN_AY`; `not` kolonuyla tutmazsa betik
«UYARI:» yazar) ve yılı yanlış basılmış ya da hiç basılmamış sayıların tek tek anlatımı (`scripts/README.template.md`).

Diğer komutlar (gerekirse):

```bash
python3 scripts/yerel_tamamla.py liste           # iş listesini (data/acik_kalemler.csv) yeniden üretir
python3 scripts/yerel_tamamla.py indir_oku       # iş listesindeki PDF'leri sırayla indirir ve okur; kesilirse kaldığı yerden devam eder
python3 scripts/yerel_tamamla.py yeniden_karar   # okunmuş künyelerin kararını güncel kural ve aralıklarla yeniden verir (ağa çıkmaz)
python3 scripts/yerel_tamamla.py durum           # otomatik karar verilemeyenleri yerel/gorsel_gerekli.txt'ye yazar
python3 scripts/yerel_tamamla.py uygula --kuru   # neyin değişeceğini gösterir, hiçbir şey yazmaz
python3 scripts/yerel_tamamla.py uygula          # listeyi, JSON'u, yıllık özeti, raporu, README'yi ve iş listesini günceller
python3 scripts/yerel_tamamla.py yeniden_yaz     # CSV elle düzeltildiyse: sıralar, doğrular, bütün çıktıları yeniden yazar
python3 scripts/yerel_tamamla.py mukerrer_tara --bas 2000-06-27 --son 2026-11-17   # günlük mükerrer sayfalarını yoklar (rapor)
python3 scripts/yerel_tamamla.py arsiv_mukerrer_tara --bas 1 --son 24095           # arsiv/N_k.pdf adreslerini yoklar (rapor)
python3 scripts/yerel_tamamla.py yoklama_ozeti   # yoklama sonuçlarını güncel listeyle karşılaştırıp rapora ve README'ye yazar
```

Yeni bir şüpheli künye bulunursa anahtarı betiğin başındaki `KONTROL` sözlüğüne eklenir; `liste` + `indir_oku --tur kontrol`
dosyayı yeniden indirir, künyeye bakılıp `yerel/gorsel.json` doldurulur ve `uygula` çalıştırılır (kontrol kalemlerinde
otomatik karar verilmez). Kalem kapanınca anahtar `KONTROL_KAPATILAN`'a taşınır; daha önce bu yolla kapatılmış bir anahtar,
kanıt kaydındakinden farklı bir gerekçe metniyle eklendiğinde yeniden açılır. Yeniden açılan kalemde `yerel/gorsel.json`'da
duran eski okuma yeniden uygulanmaz: dosya yeniden indirilir, künyeye yeniden bakılır ve kayıt güncellenir. `KONTROL`'e
yazılan anahtar listede hiçbir satırla eşleşmiyorsa (yazım hatası) araç bunu söyler. Kasım 2026'da 6126, 10908, 11979, 244,
293, 1054, 1056 ve iki büyük mükerrer bu yolla işlendi. Bu dokuz kalemin kanıt kayıtları (`kanit/yerel_okumalar.jsonl.gz`)
gerekçe alanı (`kontrol_gerekcesi`) olmadan yazıldı: bu anahtarlardan biri `KONTROL`'e hangi metinle eklenirse eklensin
(`KONTROL_KAPATILAN`'daki metinle de) kalem yeniden açılır.

`kanit/yerel_okumalar.jsonl.gz` yerinde olmalıdır: kapanan kalemler ve README'deki "künye aynı / farklı" sayıları oradan
okunur. Dosya eksikse `uygula`, `yeni` ve `yeniden_yaz` hiçbir şey yazmadan durur.

Yoklama komutları: `mukerrer_tara` yalnızca bitmiş günleri yoklar (`--son` bugünden önce olmalı; son günler için `yeni`),
`arsiv_mukerrer_tara` 1–24095 arasını. İkisi de kaldığı yerden devam eder; kaydı güncel listeyle tutmayan bir günü ya da
sayıyı yeniden yoklar. `yoklama_ozeti` yalnızca tamamlanmış yoklamaları özetler, ham sonuçları
`kanit/yerel_mukerrer_yoklama.json.gz` dosyasına yazar ve `yerel/` altındaki dosyalar rapordaki özetin kapsadığı aralığı
karşılamıyorsa (dosya yok ya da yarım) hiçbir şey yazmadan durur. Yoklama dosyası `yerel/` altında hiç yoksa (başka bir
bilgisayar, silinmiş klasör) ve depoda ham sonuç varsa, yoklama komutları (ve sonradan yayımlanmış bir mükerrer bulduğunda
`yeni`) dosyayı önce o ham sonuçtan yeniden kurar: özeti yenilemek için yoklamayı baştan yapmak gerekmez. `yeni`, günlük
yoklamanın kapsadığı bir güne sonradan yayımlanmış bir mükerrer eklediğinde yoklama özetini de kendisi yeniler
(`data/dogrulama_raporu.json`, README ve gerekiyorsa `kanit/yerel_mukerrer_yoklama.json.gz`); değişen dosyaların hepsi
listeyle birlikte commit edilmelidir.

Kaydı listeyle tutan bir gün ya da sayı bir daha yoklanmaz; `yerel/` altındaki yoklama dosyasını silmek de bunu değiştirmez
(dosya depodaki ham sonuçtan yeniden kurulur) ve komut siteye hiç gitmeden «uyuşmayan/hatalı 0» yazar (çıktıdaki «bu
çalıştırmada siteye sorulan» adedine bakın). Bu yüzden `yeni`'nin baktığı son 10 sayıdan eski bir güne sonradan konmuş bir
mükerrer kendiliğinden bulunmaz. Bir aralığı baştan yoklamak için `--yeniden` verin, ör.
`python3 scripts/yerel_tamamla.py mukerrer_tara --bas 2026-01-01 --son 2026-11-17 --yeniden`; bu kipte yoklama kaldığı yerden
devam etmez: kesilirse `--bas` değerini çıktıdaki ilk «hata» satırının gününe (arşiv yoklamasında sayısına) çekip yine
`--yeniden` ile çalıştırın (durma iletisindeki «son:», art arda hataların yalnızca sonuncusudur). Çıkan fark sayfa açılıp incelenir; eksik mükerrerin satırı CSV'ye
`sira` ve `gun` boş bırakılarak eklenir, ardından `yeniden_yaz` ve `yoklama_ozeti` çalıştırılır.

Siteye karşı nazik olun: betik istekleri sırayla ve aralarında bekleyerek gönderir (`--bekle`, varsayılan 1–1,5 saniye).
Birden çok kopyayı aynı anda çalıştırmayın.

### 4.2 Otomatik karar ve görsel okuma kuralları

**Otomatik karar** (yalnızca arşiv PDF'i okunan kalemlerde; `indir_oku` verir, `yeniden_karar`, `durum` ve `uygula` güncel
kural ve aralıkla yeniden verir): aşağıdakilerin hepsi tutuyorsa tarih kendiliğinden kabul edilir,
aksi hâlde kalem görsel kontrole kalır.

- Künye metninden çıkan tarih adaylarından **tam biri** komşu sayıların verdiği aralığa düşüyor ve metindeki **ilk** gün
  adıyla (künyedeki) tutuyor (aralık tek gün değilse gün adı okunmuş olmalı). Gövdede geçen başka bir tarih kendi gün
  adıyla birlikte aralığa düşse bile kabul edilmez; 10908'deki hata buydu.
- Sayı numarası künyede doğrulanıyor: okunan numara beklenenle aynı ya da beklenen numara künye metninde ayrı bir sözcük
  olarak geçiyor. Farklı bir numara okunursa ya da numara hiç bulunamazsa otomatik karar verilmez.
- Mükerrer dosyasında «Mükerrer» ibaresi künyede **kendi satırında** duruyor (gövdedeki "… 17914 mükerrer sayılı Resmî
  Gazete" gibi atıflar sayılmaz) ve basılı sıra dosya adındaki sırayla tutuyor; asıl sayı dosyasında ibare yok.
- Karar metni ilk sayfadan geliyor (ilk sayfası metinsiz, taranmış PDF'lerde otomatik karar verilmez).

Atıftan tarihlendirilmiş bir sayıda künye farklı bir tarih verirse kalem `celiski` olarak ayrılır. `uygula` saklanan kararı
kullanmaz; kararı her seferinde güncel aralık ve güncel kuralla yeniden verir.

**Görsel okuma** (`yerel/gorsel.json`, biçimi betiğin başında): her kayıtta `tarih`, `kunyedeki_gun`, `kunyedeki_sayi` ve
`mukerrer` zorunludur; bilinmeyen alan adı, tanınmayan gün adı ya da eksik alan kaydı reddettirir. `uygula` tarihi aralıkla,
gün adıyla, sayı numarasıyla ve (mükerrerlerde) ibare ve sırayla denetler; otomatik kararla çelişen görsel okumayı da
reddeder. Basılı tarih bir baskı hatasıysa doğru tarih `"zorla": true` ve gerekçeyle, yanlış basılmış ya da kırık bir sayı
numarası `"sayi_baski_hatasi": true` ve gerekçeyle girilir; gerekçe nota yazılır. Asıl sayı / mükerrer uyuşmazlığı hiçbir
biçimde aşılamaz: dosya adının söylediği şey değilse kalem elle incelenmelidir.

Yazmadan önce listenin bütünlüğü denetlenir: her tarih geçerli bir YYYY-AA-GG tarihi olmalı, numaralar kesintisiz olmalı,
tarih geriye gitmemeli, art arda iki asıl sayı aynı tarihi taşımamalı, her mükerrerin asıl sayısı bulunmalı ve tarihi asıl
sayısının tarihi ile bir sonraki asıl sayının tarihi arasında olmalı, aynı sayı ve mükerrer sırası iki kez geçmemeli,
`tarih_kaynagi` betiğin `ETIKET` sözlüğündeki 12 etiketten biri olmalı. Denetim başarısız olursa hiçbir dosya (kanıt
dosyası dahil) yazılmaz.

### 4.3 Kasım 2026'da araçta düzeltilenler

Tamamlama sırasında aracın kendisi de denetlendi (bağımsız inceleme + her bulgunun çürütülmeye çalışılması). Düzeltilenler:

- Otomatik karar, sayı numarası hiç okunamadığında da veriliyordu; «Mükerrer» ibaresi gövde metnindeki bir atıftan da
  kabul ediliyordu; basılı mükerrer sırası dosya adıyla karşılaştırılmıyordu; künyedeki tarih okunamadığında gövdedeki
  başka bir tarih (kendi gün adıyla) kabul edilebiliyordu.
- `uygula`, `gorsel.json`'daki yanlış adlı ya da eksik alanları sessizce atlıyordu (gün adı / sayı denetimi yapılmadan
  kabul); tanınmayan bir `karar` değeri yok sayılıp otomatik karar uygulanıyordu; yanlış basılmış sayı numarası için temiz
  bir yol yoktu; reddedilen kayıtlar kanıt dosyasına her çalıştırmada yeniden ekleniyordu.
- README'deki bağımsız atıf istatistikleri ilk derlemeden kalma sabit sayılardı; artık her yazışta yeniden hesaplanıyor.
- `yeni`, listeye eklenmiş günlerin mükerrer sayfalarına bir daha bakmıyordu: aynı gün içinde eklenen bir sayının sonradan
  yayımlanan mükerreri kaçabiliyordu. Ana sayfadaki geçici bir sunucu hatasını "o gün sayı yok" sayıyordu; künyesi sitede
  hatalı bir gün elle eklendikten sonra öz-sınama her çalıştırmayı durduruyordu; okuduğu sayfaların kaydını tutmuyordu.
- Günlük sayfa ayrıştırıcısı 2000–2006 künye biçiminde gövdedeki bir atfı künye sanabiliyordu; gün rakamı iki ayrı HTML
  öğesine bölünmüş künyeleri yanlış okuyordu.
- Yoklama komutları geçici hataları "yapıldı" sayıp bir daha denemiyordu; liste tarafı dosyaya yazıldığı için liste
  değişince rapor eskiyordu; `arsiv_mukerrer_tara` 24093 ve 24095'in mükerrerlerini tarih sınırı yüzünden sayamıyordu.

Son bir bağımsız inceleme turunda (18 Kasım 2026) bulunup düzeltilenler:

- Yoklamaların ham sonucu yalnızca git'e girmeyen `yerel/` klasöründeydi ve `yoklama_ozeti`, o klasörde o an ne varsa onu
  yazarak rapordaki özeti daraltabiliyor ya da silebiliyordu. Ham sonuç artık `kanit/`'ta; özet daralmıyor. Yoklanmış bir
  gün, listeyle tutmasa bile bir daha yoklanmıyordu; `mukerrer_tara` henüz bitmemiş günleri "mükerrer yok" diye
  kaydedebiliyordu; özetin tarihi yoklamanın değil özetin yazıldığı gündü.
- `yeni` sonradan yayımlanmış bir mükerrer eklediğinde günlük yoklama dosyası eski adette kalıyor, sonraki `yoklama_ozeti`
  olmayan bir uyuşmazlık bildiriyordu. Gazetenin yayımlanmadığı günün kaydı her çalıştırmada yeniden ekleniyor, o günün
  mükerrer sayfaları yoklanmıyordu. Geçmiş bir günün sayfası 404 dönerse "yeni sayı yok" deyip sessizce bitiyordu. Künyesi
  tanınmayan biçimde olan (elle eklenmiş) bir günün kanıt kaydında sayfada ne yazdığı görünmüyordu.
- Çıktılar yerinde yazıldığı için yarıda kesilen bir çalışma boş ya da yarım bir JSON, rapor ya da liste bırakabiliyor,
  sonraki çalıştırma bunu fark etmiyordu. Dosyalar artık önce geçici ada yazılıp yerine konuyor; kesilmiş bir yazım bir
  sonraki `uygula` ya da `yeni` çalıştırmasında onarılıyor.
- Yeniden açılan bir `KONTROL` kalemi, hiçbir şey yeniden indirilmeden `gorsel.json`'daki eski okumayla kapanabiliyordu.
  Bütünlük denetimi, tarihi asıl sayısından çok uzağa yazılmış bir mükerreri yakalamıyordu. Listede karşılığı olmayan bir
  `KONTROL` anahtarı sessizce yok sayılıyordu; `listede_birak` kaydı kalem yeniden işlendiğinde kanıttan siliniyordu.
- `render_readme.py` raporu varsayılan kodlamayla okuyordu: varsayılanı UTF-8 olmayan sistemlerde (ör. Windows) README
  üretilemiyordu.
- Bu düzeltmelerin ardından yapılan ikinci denetimde: yoklamaların depodaki ham sonucu (`kanit/`) geri okunmuyordu, yani
  `yerel/` klasörü olmayan bir bilgisayarda özet yenilenemiyordu (artık yoklama dosyası yoksa ham sonuçtan kuruluyor);
  yeniden açılan bir `KONTROL` kaleminde `--sakla` ile saklanmış eski PDF okunuyor, dosya yeniden indirilmiyordu.
- Son hâlin üçüncü bir bağımsız okumasında: `yeni` sonradan yayımlanmış bir mükerreri eklediğinde güncel adet yalnızca
  `yerel/` altında kalıyor, depodaki ham sonuç ve rapordaki özet eskiyordu (artık özeti kendisi yeniliyor); yoklanmış bir
  aralığı baştan yoklamanın yolu yoktu (`--yeniden` eklendi, çıktı o çalıştırmada siteye kaç kez sorulduğunu da yazıyor);
  bozuk bir ham sonuç dosyası `yeni`'yi kanıt yazıldıktan sonra durdurabiliyordu; `yoklama_ozeti` özetin tarihini dosya
  zamanından aldığı için kopyalanmış bir klasörde tarih değişebiliyordu; hiçbir şeyi değiştirmeyen bir `yeniden_yaz` başka
  bir gün çalıştırıldığında «Liste tarihi»ni ilerletiyordu; yanlış yazılmış bir tarih bağımsız değişkeni Python hata
  dökümüyle bitiyordu; Windows'ta README ve JSON dosyaları CRLF satır sonuyla yazılırdı; README, yoklamada çıkan her
  farkın bu belgede açıklandığını söylüyordu (artık farkın raporun neresinde olduğunu söylüyor).

Belgelerin veriyle karşılaştırıldığı bir denetimde (22 Kasım 2026) bulunup düzeltilenler:

- Bütünlük denetimi, art arda iki asıl sayının aynı tarihi taşımasını (ilk derlemenin 10908 ve 11979 hatalarının izi,
  3.1) ve tanınmayan bir `tarih_kaynagi` etiketini yakalamıyordu: elle düzeltmedeki bir etiket yazım hatası JSON'a
  geçiyor, `build_artifact.py` de Python hata dökümüyle duruyordu. İkisi de artık yazmadan önce reddediliyor (4.2).
- `build_artifact.py` ve `site/app.js`, listede bugün kullanılmayan iki geçerli etiketi («Lexpera günlük listesi»,
  «başka resmî metinlerde geçen tarih–sayı atfı») tanımıyordu; tanınmayan bir etikette `build_artifact.py` artık satırı
  söyleyen bir iletiyle duruyor. Sayfa başlığındaki yıl aralığının sonu ve grafiğin üst sınırı elle yazılıydı, artık veriden; giriş metni son
  sayıyı ve tarihini de veriden gösteriyor. Sayfa karakter kodlamasını (`<meta charset="utf-8">`) belirtmiyordu.
- README'de TBMM kayıtlarıyla sıraya sığan vakalar için «künye yeniden okundu ya da resmî günlük sayfa kontrol edildi»
  cümlesi sabit metindi ve depoda bunun kaydı yok; `render_readme.py` artık bu vakaların hangi tek haneli yazım hatasından
  olduğunu, tarihin nereden geldiğini ve depoda yeniden okuma kaydı olup olmadığını veriden yazıyor. «Aynı» sayılan sayılarda listeyle çelişen atıflar ve karşılaştırmaya girmeyen atıflar da
  hesaplanıp README'ye yazılıyor. Künyesinde gün ya da ay kusurlu yayınların adedi koda gömülü bir 10'du; artık `GUN_AY`
  listesinden sayılıyor ve liste `not` kolonuyla tutmazsa betik uyarıyor.
- İlk derlemenin `build_outputs.py`'si, girdilerinden biri eksik ya da bozuksa `data/`'yı yarı yazılmış bırakabiliyordu;
  artık bütün girdileri okuyup çıktıları bellekte hesaplamadan hiçbir şey yazmıyor (bir girdi eksik, okunamaz ya da beklenen
  bir alandan yoksunsa durur). İlk derleme betiklerinin (`adjudicate.py`, `citations.py`, `collect_era2.py`,
  `collect_visual.py`, `era1_remaining.py`, `find_masthead.py`, `identity.py`, `resolve_era1.py`, `tbmm_citations.py`) belge
  dizeleri, girdilerinin depoda olmadığını ve `kanit/`'teki karşılıklarını söylüyor; `atif_dogrula.py`'deki, arşiv ilk
  sayfa atıflarının README'ye girmediğini söyleyen yanlış yorum düzeltildi.

## 5. Claude Code için bakım istemi

Aşağıdaki metin, depoyu siteye erişebilen bir bilgisayarda açan bir Claude Code oturumuna olduğu gibi verilebilir.

```text
You are maintaining the dataset in this repository (GitHub: omertekin2002/gayriresmi-gazete, branch main): a complete
chronological list of every issue of the Turkish Official Gazette (T.C. Resmî Gazete), 1921 → today:
data/resmi_gazete_sayilari.csv (+ .json), with evidence in kanit/ and scripts in scripts/. Everything user-facing in
the repo is written in Turkish; keep it that way (notes, docs, commit messages).

The list has no open items and no estimated dates: every date comes from a masthead or an official daily page, except
the few mastheads with a missing or misprinted date listed in EKSIKLER.md section 2 (293 keeps its TBMM-record date).
Your job is to bring the list up to date from this computer, which must be able to reach resmigazete.gov.tr directly.

Read first: EKSIKLER.md section 4 and the docstring at the top of scripts/yerel_tamamla.py.

Steps:
1. git checkout main && git pull (on Windows use `py` instead of `python3`). Run
   `python3 scripts/yerel_tamamla.py baglanti`. It must print TAMAM. If the site is unreachable, stop and tell me. Do not
   use proxies, VPNs or mirror sites to get around it.
2. Run `python3 scripts/yerel_tamamla.py yeni --kuru`, look at what it would add, then run it without --kuru. It first
   re-reads the last listed day as a self-test (walking back up to 8 issues if that day's masthead is faulty on the
   site) and re-probes the mükerrer pages of the last ten listed issues.
   If the self-test fails, the daily page HTML has changed: fix gunluk_oku() in the script and rerun. If it stops because
   a page does not look like the expected day or a mükerrer page returns an error, inspect that page; rerun later if
   it was a server error. Days on which the gazette is not published are skipped and recorded; that is normal. If it
   ends with a warning that the page of a past day is missing (404), the rows it could read are written, but tell me
   about those days. Never invent rows and never add parallelism; keep the delay at ≥1 s.
3. If something in the list has to be corrected by hand, edit data/resmi_gazete_sayilari.csv (only `tarih`, `url`,
   `tarih_kaynagi`, `not`; a mükerrer page that exists on the site but that `yeni` no longer reaches is added as a new
   row with `sira` and `gun` left empty, after you have opened the page) and run
   `python3 scripts/yerel_tamamla.py yeniden_yaz`, which validates, re-sorts and rewrites every output. If you added or
   removed a mükerrer row for a day from 27.06.2000 up to the last probed day, re-probe that day with
   `python3 scripts/yerel_tamamla.py mukerrer_tara --bas YYYY-MM-DD --son YYYY-MM-DD --yeniden` (for an issue number
   1–24095: `arsiv_mukerrer_tara --bas N --son N --yeniden`) and then run `python3 scripts/yerel_tamamla.py yoklama_ozeti`;
   commit data/dogrulama_raporu.json, README.md and kanit/yerel_mukerrer_yoklama.json.gz with the list. Without the
   re-probe, yoklama_ozeti (here or in a later clone) reports that day as a mismatch, because the stored probe still has
   the old count. For a masthead that needs to be re-read, use the KONTROL mechanism described in EKSIKLER.md 4.1
   instead of a hand edit. If a file is not what its name says (a different issue number, a "mükerrer" file without the
   Mükerrer marker), change nothing: show me the evidence and wait for my decision.
4. Rebuild the HTML view: `python3 scripts/build_artifact.py data/resmi_gazete_sayilari.csv site`. Its outputs
   site/data.json and site/gayriresmi-gazete.html are gitignored; site/head.html, body.html and app.js are tracked.
   The year range end, the last issue and its date, the counts and the chart's y axis are filled from the data by
   site/app.js, but some figures in site/body.html are hand-written (the HTML comment at the top of that file lists
   them): compare them with the regenerated README.md and fix any that changed. If render_readme.py printed an
   "UYARI:" line, update GUN_AY in scripts/render_readme.py and the template text together. The HTML view is not
   published anywhere at the moment; it is only built locally.
5. Update the status line at the top of EKSIKLER.md and check its other snapshot counts (sections 2 and 3) against the
   regenerated README.md. Commit in small logical commits with Turkish messages. Never commit
   yerel/, PDFs or image archives. Ask me before pushing.

Finish with a short summary: how many rows were added, the last issue number and date, and anything surprising.
```
