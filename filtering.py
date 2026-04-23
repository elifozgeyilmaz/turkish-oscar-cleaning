"""
Filtreleme fonksiyonları.

İki tür fonksiyon var:
  - modify_document : belgeyi atmak yerine düzeltir (whitespace, URL temizliği)
  - should_keep_document : tüm filtreleri uygular, True → tut / False → at
"""

from collections import Counter
from typing import List, Optional, Set

import fasttext

from stopwords_tr import stopwords_tr
from flagged_words_tr import flagged_words_tr

# Modül yüklendiğinde bir kere oluşturulur, her belgede yeniden kurulmaz.
_STOPWORDS_SET = frozenset(w.lower() for w in stopwords_tr)
_FLAGGED_SET   = frozenset(w.lower() for w in flagged_words_tr)


# ---------------------------------------------------------------------------
# Yardımcı
# ---------------------------------------------------------------------------

def get_words(text: str, strip_characters: Set[str]) -> List[str]:
    """Boşlukla böl, kelimelerin baş/sonundaki özel karakterleri temizle."""
    strip_str = "".join(strip_characters)
    words = [w.strip(strip_str) for w in text.split()]
    return [w for w in words if w]


# ---------------------------------------------------------------------------
# Belge düzeltme fonksiyonları
# ---------------------------------------------------------------------------

def normalize_whitespace(text: str) -> str:
    """Birden fazla boşluk/tab/newline'ı tek boşluğa indir."""
    return " ".join(text.split())


def remove_words_with_incorrect_substrings(
    text: str,
    incorrect_substrings: List[str],
    strip_characters: Set[str],
) -> str:
    """İçinde http, www, .com vb. geçen kelimeleri belgeden çıkar."""
    words = text.split()
    cleaned = [
        w for w in words
        if not any(sub in w for sub in incorrect_substrings)
    ]
    return " ".join(cleaned)


# ---------------------------------------------------------------------------
# Filtre fonksiyonları — True → belgeyi tut, False → at
# ---------------------------------------------------------------------------

def filter_by_word_count(
    text: str,
    min_cutoff: int,
    max_cutoff: int,
    strip_characters: Set[str],
) -> bool:
    """Kelime sayısı [min, max] aralığında değilse at."""
    words = get_words(text, strip_characters)
    return min_cutoff <= len(words) <= max_cutoff


def filter_by_long_words(
    text: str,
    max_length: int,
    strip_characters: Set[str],
) -> bool:
    """max_length karakterden uzun kelime içeren belgeyi at."""
    words = get_words(text, strip_characters)
    if not words:
        return False
    return all(len(w) <= max_length for w in words)


def filter_by_character_repetition(
    text: str,
    repetition_length: int,
    max_cutoff: float,
) -> bool:
    """
    Karakter n-gram tekrar oranı max_cutoff'u geçiyorsa at.
    Örnek: "aaaaaaaaaa" gibi metinleri yakalar.
    """
    chars = list(text)
    if len(chars) < repetition_length:
        return True
    ngrams = [
        "".join(chars[i : i + repetition_length])
        for i in range(len(chars) - repetition_length + 1)
    ]
    counts = Counter(ngrams)
    total = len(ngrams)
    repeated = sum(count for count in counts.values() if count > 1)
    return (repeated / total) <= max_cutoff


def filter_by_word_repetition(
    text: str,
    repetition_length: int,
    max_cutoff: float,
    strip_characters: Set[str],
) -> bool:
    """
    Kelime n-gram tekrar oranı max_cutoff'u geçiyorsa at.
    Örnek: aynı cümlenin tekrar tekrar yazıldığı metinleri yakalar.
    """
    words = get_words(text, strip_characters)
    if len(words) < repetition_length:
        return True
    ngrams = [
        " ".join(words[i : i + repetition_length])
        for i in range(len(words) - repetition_length + 1)
    ]
    counts = Counter(ngrams)
    total = len(ngrams)
    repeated = sum(count for count in counts.values() if count > 1)
    return (repeated / total) <= max_cutoff


def filter_by_special_characters(
    text: str,
    special_characters: Set[str],
    max_cutoff: float,
) -> bool:
    """Özel karakter oranı max_cutoff'u geçiyorsa at."""
    if not text:
        return False
    ratio = sum(1 for c in text if c in special_characters) / len(text)
    return ratio <= max_cutoff


def filter_by_stopwords(
    text: str,
    min_cutoff: float,
    strip_characters: Set[str],
) -> bool:
    """
    Stopword oranı min_cutoff'un altındaysa at.
    Düşük oran → spam, yabancı dil veya anlamsız metin.
    """
    words = get_words(text, strip_characters)
    if not words:
        return False
    ratio = sum(1 for w in words if w.lower() in _STOPWORDS_SET) / len(words)
    return ratio >= min_cutoff


def filter_by_flagged_words(
    text: str,
    max_cutoff: float,
    strip_characters: Set[str],
) -> bool:
    """
    Flagged word oranı max_cutoff'u geçiyorsa at.
    Yüksek oran → uygunsuz / müstehcen içerik.
    """
    words = get_words(text, strip_characters)
    if not words:
        return False
    ratio = sum(1 for w in words if w.lower() in _FLAGGED_SET) / len(words)
    return ratio <= max_cutoff


# ---------------------------------------------------------------------------
# Dil tespiti
# ---------------------------------------------------------------------------

def load_fasttext_model(model_path: str) -> fasttext.FastText._FastText:
    """
    Fasttext modelini yükle.
    Model: https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
    """
    fasttext.FastText.eprint = lambda x: None  # uyarıları sustur
    return fasttext.load_model(model_path)


def filter_by_language(
    text: str,
    model: fasttext.FastText._FastText,
    lang_id_label: str,
    min_cutoff: float = 0.8,
) -> bool:
    """
    Fasttext ile dil tespiti yap. Türkçe skoru min_cutoff'un altındaysa at.
    Fasttext çok satırlı metinlerde hata verir — newline'ları temizle.
    lang_id_label: modelin döndürdüğü label ("tr", "tur", "Latn_tur" vb.)
    """
    cleaned = text.replace("\n", " ")
    labels, scores = model.predict(cleaned, k=1)
    label = labels[0].replace("__label__", "")
    return label == lang_id_label and scores[0] >= min_cutoff


# ---------------------------------------------------------------------------
# Ana fonksiyonlar
# ---------------------------------------------------------------------------

def modify_document(text: str, params: dict) -> str:
    """Filtreleme öncesi belgeyi düzelt."""
    if params["cond_uniform_whitespace"]:
        text = normalize_whitespace(text)

    if params["cond_remove_words_with_incorrect_substrings"]:
        text = remove_words_with_incorrect_substrings(
            text,
            params["incorrect_word_substrings"],
            params["strip_characters"],
        )
    return text


def should_keep_document(
    text: str,
    params: dict,
    fasttext_model: Optional[fasttext.FastText._FastText] = None,
) -> bool:
    """
    Tüm filtreleri sırayla uygula.
    Herhangi biri False dönerse belge atılır.
    """
    if params["cond_check_number_words"]:
        if not filter_by_word_count(
            text,
            params["number_words_min_cutoff"],
            params["number_words_max_cutoff"],
            params["strip_characters"],
        ):
            return False

    if params["cond_remove_long_words"]:
        if not filter_by_long_words(
            text,
            params["length_word_max_cutoff"],
            params["strip_characters"],
        ):
            return False

    if params["cond_check_character_repetition_removal"]:
        if not filter_by_character_repetition(
            text,
            params["character_repetition_length"],
            params["character_repetition_max_cutoff"],
        ):
            return False

    if params["cond_check_word_repetition_removal"]:
        if not filter_by_word_repetition(
            text,
            params["word_repetition_length"],
            params["word_repetition_max_cutoff"],
            params["strip_characters"],
        ):
            return False

    if params["cond_check_special_characters"]:
        if not filter_by_special_characters(
            text,
            params["special_characters"],
            params["special_characters_max_cutoff"],
        ):
            return False

    if params["cond_check_stopwords"]:
        if not filter_by_stopwords(
            text,
            params["stopwords_min_cutoff"],
            params["strip_characters"],
        ):
            return False

    if params["cond_check_flagged_words"]:
        if not filter_by_flagged_words(
            text,
            params["flagged_words_max_cutoff"],
            params["strip_characters"],
        ):
            return False

    if params["cond_check_lang_id"] and fasttext_model is not None:
        if not filter_by_language(
            text,
            fasttext_model,
            params["lang_id_label"],
            params["lang_id_min_cutoff"],
        ):
            return False

    return True
