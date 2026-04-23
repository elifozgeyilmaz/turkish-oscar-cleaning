"""
Her row'un hangi filtreden elendi bilgisini metadata olarak ekler.

Kullanım:
  python analyze_filtering.py \
    --data_files ./data/filtered_1pct.parquet \
    --output_path ./analysis_output

Çıktı sütunları:
  text          : orijinal metin
  kept          : True → kaldı, False → elendi
  failed_rules  : hangi filtreleri geçemedi (virgülle ayrılmış, boş = geçti hepsini)
  word_count    : belgедeki kelime sayısı
  stopword_ratio: stopword oranı
  special_char_ratio: özel karakter oranı
  flagged_ratio : flagged word oranı
"""

import argparse
from multiprocessing import cpu_count

from datasets import load_dataset

from filtering import (
    filter_by_word_count,
    filter_by_long_words,
    filter_by_character_repetition,
    filter_by_word_repetition,
    filter_by_special_characters,
    filter_by_stopwords,
    filter_by_flagged_words,
    get_words,
    modify_document,
)
from parameters import parameters_filtering_tr
from stopwords_tr import stopwords_tr
from flagged_words_tr import flagged_words_tr

_STOPWORDS_SET = frozenset(w.lower() for w in stopwords_tr)
_FLAGGED_SET   = frozenset(w.lower() for w in flagged_words_tr)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_files", type=str, required=True)
    parser.add_argument("--output_path", type=str, default="./analysis_output")
    parser.add_argument("--split", type=str, default="train")
    parser.add_argument("--num_proc", type=int, default=cpu_count())
    return parser.parse_args()


def analyze_row(example: dict, params: dict) -> dict:
    text = modify_document(example["text"], params)
    strip = params["strip_characters"]

    words = get_words(text, strip)
    word_count = len(words)

    stopword_ratio = (
        sum(1 for w in words if w.lower() in _STOPWORDS_SET) / word_count
        if word_count else 0.0
    )
    flagged_ratio = (
        sum(1 for w in words if w.lower() in _FLAGGED_SET) / word_count
        if word_count else 0.0
    )
    special_char_ratio = (
        sum(1 for c in text if c in params["special_characters"]) / len(text)
        if text else 0.0
    )

    failed = []

    if params["cond_check_number_words"]:
        if not filter_by_word_count(text, params["number_words_min_cutoff"], params["number_words_max_cutoff"], strip):
            failed.append("word_count")

    if params["cond_remove_long_words"]:
        if not filter_by_long_words(text, params["length_word_max_cutoff"], strip):
            failed.append("long_words")

    if params["cond_check_character_repetition_removal"]:
        if not filter_by_character_repetition(text, params["character_repetition_length"], params["character_repetition_max_cutoff"]):
            failed.append("char_repetition")

    if params["cond_check_word_repetition_removal"]:
        if not filter_by_word_repetition(text, params["word_repetition_length"], params["word_repetition_max_cutoff"], strip):
            failed.append("word_repetition")

    if params["cond_check_special_characters"]:
        if not filter_by_special_characters(text, params["special_characters"], params["special_characters_max_cutoff"]):
            failed.append("special_chars")

    if params["cond_check_stopwords"]:
        if not filter_by_stopwords(text, params["stopwords_min_cutoff"], strip):
            failed.append("stopwords")

    if params["cond_check_flagged_words"]:
        if not filter_by_flagged_words(text, params["flagged_words_max_cutoff"], strip):
            failed.append("flagged_words")

    return {
        "text": example["text"],
        "kept": len(failed) == 0,
        "failed_rules": ",".join(failed),
        "word_count": word_count,
        "stopword_ratio": round(stopword_ratio, 4),
        "special_char_ratio": round(special_char_ratio, 4),
        "flagged_ratio": round(flagged_ratio, 4),
    }


def main():
    args = parse_args()
    params = parameters_filtering_tr

    print("Veri yükleniyor...")
    dataset = load_dataset("parquet", data_files=args.data_files, split=args.split)
    print(f"Toplam row: {len(dataset):,}")

    print("\nHer row analiz ediliyor...")
    dataset = dataset.map(
        lambda x: analyze_row(x, params),
        num_proc=args.num_proc,
        desc="Analiz",
    )

    kept_count   = sum(1 for x in dataset if x["kept"])
    dropped_count = len(dataset) - kept_count

    print(f"\n--- Özet ---")
    print(f"Kalan : {kept_count:,}")
    print(f"Atılan: {dropped_count:,} (%{dropped_count/len(dataset)*100:.1f})")

    print("\n--- Kural bazlı eleme sayıları ---")
    rule_counts = {}
    for x in dataset:
        for rule in x["failed_rules"].split(","):
            if rule:
                rule_counts[rule] = rule_counts.get(rule, 0) + 1
    for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
        print(f"  {rule:<20}: {count:,}")

    print(f"\nKaydediliyor → {args.output_path}")
    dataset.save_to_disk(args.output_path)
    print("Tamamlandı.")


if __name__ == "__main__":
    main()
