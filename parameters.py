"""
Filtreleme parametreleri — Türkçe OSCAR için.

Her parametre ne işe yarar:

  cond_*                  : O filtreyi aç/kapat (True/False)
  number_words_min/max    : Belgede olması gereken min/max kelime sayısı
  length_word_max_cutoff  : Tek bir kelimenin max karakter uzunluğu
  character_repetition_*  : "aaaaaaa" gibi karakter tekrarı oranı
  word_repetition_*       : Aynı kelime dizisinin tekrar oranı
  special_characters_max  : Noktalama+rakam+sembol oranının üst sınırı
  stopwords_min_cutoff    : Belgede stopword oranının alt sınırı
  flagged_words_max_cutoff: Belgede flagged word oranının üst sınırı
"""

import string

# ---------------------------------------------------------------------------
# Özel karakter seti
# ---------------------------------------------------------------------------
# Türkçe harfler (ğ ü ş ı ö ç Ğ Ü Ş İ Ö Ç) burada YOK — normal harf sayılır.
# Sadece noktalama, rakam, boşluk ve yaygın semboller özel karakter sayılır.

main_special_characters = string.punctuation + string.digits + string.whitespace

other_special_characters = (
    "    　    ￼'""–ー一▬…✦�­£​•€«»°·═"
    "×士＾˘⇓↓↑←→（）§″′´¿−±∈﻿¢ø‚„½¼¾¹²³―⁃，ˌ¸‹›ʺˈʻ¦‐⠀‰‑≤≥‖"
    "◆●■►▼▲▴∆▻¡★☆✱ːº。¯˜¥ɪ≈†上ン：∼⁄・♡✓⊕․．⋅÷１‟；،、¨ाাी्े◦˚"
    "゜ʼ≖ʼ¤ッツシ℃√！【】‿∞➤～πه۩☛₨➩☻๑٪♥ıॽ《'©﴿٬？▷Г♫∟™ª₪®「—❖」﴾》"
)

special_characters_tr = set(main_special_characters + other_special_characters)

# ---------------------------------------------------------------------------
# Filtreleme parametreleri — Türkçe
# ---------------------------------------------------------------------------

parameters_filtering_tr = {
    # Boşluk normalizasyonu (birden fazla boşluğu teke indir)
    "cond_uniform_whitespace": True,

    # URL / web içeriği temizliği
    "cond_remove_words_with_incorrect_substrings": True,
    "incorrect_word_substrings": ["http", "www", ".com", "href", "//"],

    # Kelime uzunluğu — Türkçe eklemeli dil, uzun kelimeler normal
    # ("Çekoslovakyalılaştıramadıklarımızdanmışsınızcasına" gibi uçlar var)
    "cond_remove_long_words": True,
    "length_word_max_cutoff": 40,

    # Kelime sayısı — çok kısa (başlık listesi) veya aşırı uzun belgeleri at
    "cond_check_number_words": True,
    "tokenization": False,              # Türkçe boşlukla tokenize edilebilir
    "strip_characters": special_characters_tr,
    "number_words_min_cutoff": 15,      # en az 15 kelime
    "number_words_max_cutoff": 100_000,

    # Karakter tekrarı — "hahahaha", "!!!!!!" gibi
    "cond_check_character_repetition_removal": True,
    "character_repetition_length": 10,  # 10+ tekrar eden karakter dizisi
    "character_repetition_max_cutoff": 0.20,

    # Kelime tekrarı — aynı 5-gram'ın tekrar oranı
    "cond_check_word_repetition_removal": True,
    "word_repetition_length": 5,
    "word_repetition_max_cutoff": 0.30,

    # Özel karakter oranı — sembol/rakam yoğun metinleri at
    "cond_check_special_characters": True,
    "special_characters": special_characters_tr,
    "special_characters_max_cutoff": 0.35,

    # Stopword oranı — çok düşükse Türkçe değil veya spam
    "cond_check_stopwords": True,
    "stopwords_min_cutoff": 0.10,

    # Flagged word oranı — çok yüksekse uygunsuz içerik
    "cond_check_flagged_words": True,
    "flagged_words_max_cutoff": 0.05,

    # Fasttext dil tespiti — Türkçe skoru 0.8'in altındaysa at
    # Model: https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
    # lang_id_label: modeli çalıştırıp gelen label'a göre güncelle
    #   lid.176.bin → genellikle "tr"
    #   diğer modeller → "tur" veya "Latn_tur" olabilir
    "cond_check_lang_id": True,
    "lang_id_label": "tr",
    "lang_id_min_cutoff": 0.80,
}
