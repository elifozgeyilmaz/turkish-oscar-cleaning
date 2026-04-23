# Türkçe OSCAR Veri Seti Temizleme — Filtreleme Özeti

**Veri kaynağı:** OSCAR (Open Super-large Crawled Aggregated coRpus) — Common Crawl tabanlı çok dilli web corpus  
**Amaç:** Türkçe web metinlerinden gürültülü, tekrarlı, uygunsuz ve Türkçe olmayan belgeleri temizlemek

---

## Pipeline Genel Akışı

Her belge için sırasıyla uygulanır:

```
Ham metin
   ↓
[1] Ön İşleme (düzeltme)
   ↓
[2–9] Filtreler (sıralı — biri başarısız olursa belge atılır)
   ↓
Temiz metin
```

---

## Aşama 1 — Ön İşleme (Belge Düzeltme)

Belgeyi atmadan önce düzeltilebilir sorunlar giderilir.

| İşlem | Açıklama |
|---|---|
| **Boşluk normalizasyonu** | Birden fazla boşluk / tab / satır sonu → tek boşluk |
| **URL temizliği** | `http`, `www`, `.com`, `href`, `//` içeren kelimeler belgeden çıkarılır |

---

## Aşama 2 — Filtreler

### Filtre 1: Kelime Sayısı
- **Eşik:** 15 – 100.000 kelime
- **Neden:** 15'ten az kelimeli belgeler genellikle başlık listesi, menü veya metadata; aşırı uzun belgeler ise birleşmiş/bozuk dosyalar.

---

### Filtre 2: Uzun Kelime
- **Eşik:** Maksimum 40 karakter / kelime
- **Neden:** Türkçe eklemeli bir dil olduğundan uzun kelimeler normaldir (ör. "Çekoslovakyalılaştıramadıklarımızdanmışsınızcasına" ~50 kar.). 40 karakter üzeri büyük ihtimalle tokenizasyon hatası ya da bozuk veri.

---

### Filtre 3: Karakter Tekrarı
- **Yöntem:** 10 karakterlik n-gram penceresi; tekrarlanan n-gramların oranı hesaplanır
- **Eşik:** Oran > %20 ise at
- **Neden:** `"hahahahaha"`, `"!!!!!!!!!!!"`, klavye ispatı (`"asdfasdfasdf"`) gibi anlamsız içerikleri yakalar.

---

### Filtre 4: Kelime Tekrarı
- **Yöntem:** 5 kelimelik n-gram penceresi; tekrarlanan n-gramların oranı hesaplanır
- **Eşik:** Oran > %30 ise at
- **Neden:** Copy-paste ile çoğaltılmış paragrafları, döngüsel şablon metinleri ve boilerplate içerikleri yakalar.
- **Örnek:** Aynı 3 paragrafın belgede iki kez arka arkaya yer alması → atılır.

---

### Filtre 5: Özel Karakter Oranı
- **Kapsam:** Noktalama, rakam, boşluk ve yaygın semboller (€, ★, ©, ™ vb.)
- **Eşik:** Oran > %35 ise at
- **Neden:** Sembol veya rakam yoğun metinler (fiyat listeleri, kaynak kodu, bozuk encoding) genellikle doğal dil içeriği taşımaz.

---

### Filtre 6: Stopword Oranı
- **Yöntem:** Türkçe stopword listesiyle eşleşen kelimelerin oranı
- **Eşik:** Oran < %10 ise at
- **Neden:** Türkçe doğal metinlerde "ve, bir, bu, için, ile..." gibi bağlaçlar / edatlar beklenen bir frekansta görünür. Çok düşük oran → yabancı dil, spam veya anlamsız kelime yığını.

---

### Filtre 7: Flagged Word Oranı
- **Yöntem:** Uygunsuz / müstehcen kelime listesiyle eşleşen kelimelerin oranı
- **Eşik:** Oran > %5 ise at
- **Neden:** Yüksek oranda küfür/uygunsuz içerik barındıran belgeleri eğitim verisinden çıkarmak için.

---

### Filtre 8: Dil Tespiti (FastText)
- **Model:** Facebook FastText `lid.176.bin` — 176 dili tanıyan denetimli model
- **Eşik:** Türkçe (`tr`) skoru < 0.80 ise at
- **Neden:** Önceki filtrelerden geçebilen Türkçe olmayan metinleri (Azerice, Özbekçe, karışık dil vb.) temizler.

---

## Özet Tablo

| # | Filtre | Eşik | Yakaladığı Sorun |
|---|---|---|---|
| 1 | Kelime sayısı | 15 – 100.000 | Çok kısa / aşırı uzun belgeler |
| 2 | Uzun kelime | maks. 40 kar. | Tokenizasyon hatası, bozuk veri |
| 3 | Karakter tekrarı | maks. %20 | `hahahaha`, `!!!!!` gibi gürültü |
| 4 | Kelime tekrarı | maks. %30 | Copy-paste / şablon tekrarı |
| 5 | Özel karakter oranı | maks. %35 | Sembol yoğun, bozuk encoding |
| 6 | Stopword oranı | min. %10 | Yabancı dil, spam, anlamsız metin |
| 7 | Flagged word oranı | maks. %5 | Uygunsuz / müstehcen içerik |
| 8 | Dil tespiti (FastText) | min. 0.80 Türkçe skoru | Türkçe olmayan belgeler |

---

## Teknik Notlar

- Filtreler **sıralı** çalışır; bir belge ilk başarısız filtreden sonra işlemi durdurur.
- Ön işleme (URL ve boşluk temizliği) filtreleme öncesi uygulanır; atılan kelimelerin oranı değiştirebileceğinden eşikler buna göre ayarlanmıştır.
- Türkçe karakterler (ğ, ü, ş, ı, ö, ç) özel karakter sayılmaz, normal harf olarak işlenir.
- FastText modeli `lid.176.bin` — newline karakterleri temizlenerek çalıştırılır (modelin çok satırlı metinde hata verme riski nedeniyle).
