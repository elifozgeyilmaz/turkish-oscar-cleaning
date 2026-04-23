"""
analyze_filtering.py çıktısını okunabilir biçimde gösterir.

Colab kullanımı:
  from datasets import load_from_disk
  import pandas as pd

  ds = load_from_disk("./analysis_output")
  df = ds.to_pandas()

  # Bu dosyayı çalıştır:
  exec(open("visualize_analysis.py").read())
  show_analysis(df)

Ya da doğrudan:
  python visualize_analysis.py --input ./analysis_output
"""

import argparse
from collections import Counter


def show_analysis(df):
    total = len(df)
    kept = df["kept"].sum()
    dropped = total - kept

    print("=" * 60)
    print("GENEL ÖZET")
    print("=" * 60)
    print(f"  Toplam belge : {total:>10,}")
    print(f"  Kalan        : {kept:>10,}  ({kept/total*100:.1f}%)")
    print(f"  Atılan       : {dropped:>10,}  ({dropped/total*100:.1f}%)")

    # ------------------------------------------------------------------
    # Kural bazlı eleme sayıları
    # ------------------------------------------------------------------
    rule_counts = Counter()
    for rules_str in df.loc[~df["kept"], "failed_rules"]:
        for rule in rules_str.split(","):
            if rule:
                rule_counts[rule] += 1

    print()
    print("=" * 60)
    print("KURAL BAZLI ELEME (atılan belgelerden kaç tanesi bu kuralı ihlal etti)")
    print("=" * 60)
    rule_labels = {
        "word_count":      "Kelime sayısı (çok az / çok fazla)",
        "long_words":      "Çok uzun kelime içeriyor",
        "char_repetition": "Karakter tekrarı fazla",
        "word_repetition": "Kelime/cümle tekrarı fazla",
        "special_chars":   "Özel karakter oranı yüksek",
        "stopwords":       "Stopword oranı çok düşük",
        "flagged_words":   "Uygunsuz kelime oranı yüksek",
    }
    for rule, count in sorted(rule_counts.items(), key=lambda x: -x[1]):
        label = rule_labels.get(rule, rule)
        bar = "█" * int(count / max(rule_counts.values()) * 30)
        print(f"  {label:<40} {count:>7,}  {bar}")

    # ------------------------------------------------------------------
    # İstatistikler
    # ------------------------------------------------------------------
    print()
    print("=" * 60)
    print("İSTATİSTİKLER")
    print("=" * 60)
    for col, label in [
        ("word_count",        "Kelime sayısı"),
        ("stopword_ratio",    "Stopword oranı"),
        ("special_char_ratio","Özel karakter oranı"),
        ("flagged_ratio",     "Uygunsuz kelime oranı"),
    ]:
        kept_vals   = df.loc[df["kept"],  col]
        dropped_vals = df.loc[~df["kept"], col]
        print(f"\n  {label}")
        print(f"    Kalan   → ortalama: {kept_vals.mean():.4f}  medyan: {kept_vals.median():.4f}")
        print(f"    Atılan  → ortalama: {dropped_vals.mean():.4f}  medyan: {dropped_vals.median():.4f}")

    # ------------------------------------------------------------------
    # Örnek atılmış belgeler (kural başına 2 tane)
    # ------------------------------------------------------------------
    print()
    print("=" * 60)
    print("ÖRNEK ATILAN BELGELER (kural başına 2 örnek)")
    print("=" * 60)
    dropped_df = df[~df["kept"]].copy()
    shown_rules = set()
    count = 0
    for _, row in dropped_df.iterrows():
        rules = [r for r in row["failed_rules"].split(",") if r]
        primary = rules[0] if rules else "?"
        if primary in shown_rules:
            continue
        shown_rules.add(primary)
        count += 1
        print(f"\n--- Örnek #{count} | Kural: {primary} ---")
        print(f"  failed_rules   : {row['failed_rules']}")
        print(f"  word_count     : {row['word_count']}")
        print(f"  stopword_ratio : {row['stopword_ratio']:.4f}")
        print(f"  special_chars  : {row['special_char_ratio']:.4f}")
        print(f"  flagged_ratio  : {row['flagged_ratio']:.4f}")
        snippet = row["text"][:300].replace("\n", " ")
        print(f"  metin (ilk 300): {snippet}...")
        if len(shown_rules) >= len(rule_counts):
            break

    # ------------------------------------------------------------------
    # Birden fazla kuraldan elinen belgeler
    # ------------------------------------------------------------------
    multi = dropped_df[dropped_df["failed_rules"].str.count(",") >= 1]
    print()
    print("=" * 60)
    print(f"BİRDEN FAZLA KURALDAN ELİNEN: {len(multi):,} belge")
    print("=" * 60)
    combo_counts = Counter(dropped_df["failed_rules"])
    for combo, cnt in sorted(combo_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {combo:<50} → {cnt:,}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="analyze_filtering.py çıktı dizini")
    args = parser.parse_args()

    try:
        from datasets import load_from_disk
        import pandas as pd
        ds = load_from_disk(args.input)
        df = ds.to_pandas()
    except Exception as e:
        print(f"Hata: {e}")
        return

    show_analysis(df)


if __name__ == "__main__":
    main()
