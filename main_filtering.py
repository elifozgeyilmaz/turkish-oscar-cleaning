"""
Türkçe OSCAR veri seti filtreleme — giriş noktası.

Kullanım:
  # HuggingFace'den yükle
  python main_filtering.py --output_path ./filtered_dataset

  # Yerelde parquet dosyasından yükle
  python main_filtering.py --data_files ./data/*.parquet --output_path ./filtered_dataset

  # Fasttext modeli ile (dil tespiti)
  python main_filtering.py --fasttext_model_path ./lid.176.bin --output_path ./filtered_dataset
"""

import argparse
from multiprocessing import cpu_count

from datasets import load_dataset, load_from_disk

from filtering import load_fasttext_model, filter_by_language, should_keep_document, modify_document
from parameters import parameters_filtering_tr


def parse_args():
    parser = argparse.ArgumentParser(description="Türkçe OSCAR filtreleme.")
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="musabg/wikipedia-oscar-tr",
        help="HuggingFace dataset adı.",
    )
    parser.add_argument(
        "--data_files",
        type=str,
        default=None,
        help="Yerel parquet dosyası yolu (glob destekler: ./data/*.parquet).",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        help="Dataset split'i.",
    )
    parser.add_argument(
        "--fasttext_model_path",
        type=str,
        default=None,
        help="lid.176.bin dosyasının yolu. Verilmezse dil tespiti atlanır.",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="./filtered_dataset",
        help="Filtrelenmiş veri setinin kaydedileceği dizin.",
    )
    parser.add_argument(
        "--num_proc",
        type=int,
        default=cpu_count(),
        help="Paralel işlem sayısı.",
    )
    parser.add_argument(
        "--dropped_path",
        type=str,
        default=None,
        help="Atılan belgelerin kaydedileceği dizin (verilmezse kaydedilmez).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    params = parameters_filtering_tr

    # ------------------------------------------------------------------
    # 1. Veri setini yükle
    # ------------------------------------------------------------------
    print("Veri seti yükleniyor...")
    if args.data_files:
        dataset = load_dataset(
            "parquet",
            data_files=args.data_files,
            split=args.split,
        )
    else:
        dataset = load_dataset(args.dataset_name, split=args.split)

    initial_size = len(dataset)
    print(f"Toplam belge: {initial_size:,}")

    # ------------------------------------------------------------------
    # 2. Fasttext modelini yükle (varsa)
    # ------------------------------------------------------------------
    fasttext_model = None
    if args.fasttext_model_path and params["cond_check_lang_id"]:
        print("Fasttext modeli yükleniyor...")
        fasttext_model = load_fasttext_model(args.fasttext_model_path)
        print(f"Model yüklendi. Beklenen label: '{params['lang_id_label']}'")

    # ------------------------------------------------------------------
    # 3. Belgeleri düzelt (whitespace, URL temizliği)
    # ------------------------------------------------------------------
    print("\nBelgeler düzenleniyor...")
    dataset = dataset.map(
        lambda x: {"text": modify_document(x["text"], params)},
        num_proc=args.num_proc,
        desc="Düzenleme",
    )

    # ------------------------------------------------------------------
    # 4. Kural tabanlı filtreleme (multiprocessing)
    # ------------------------------------------------------------------
    print("\nKural tabanlı filtreleme uygulanıyor...")
    dataset = dataset.map(
        lambda x: {"_keep": should_keep_document(x["text"], params, fasttext_model=None)},
        num_proc=args.num_proc,
        desc="Kural filtresi",
    )

    if args.dropped_path:
        dropped = dataset.filter(lambda x: not x["_keep"], num_proc=args.num_proc, desc="Atılanlar")
        dropped = dropped.remove_columns(["_keep"])
        print(f"Atılan belgeler kaydediliyor → {args.dropped_path}")
        dropped.save_to_disk(args.dropped_path)

    dataset = dataset.filter(lambda x: x["_keep"], num_proc=args.num_proc, desc="Kalan")
    dataset = dataset.remove_columns(["_keep"])
    after_rules = len(dataset)
    _print_stats("Kural filtresi", initial_size, after_rules)

    # ------------------------------------------------------------------
    # 5. Fasttext dil tespiti filtrelemesi (tek process — model pickle edilemez)
    # ------------------------------------------------------------------
    if fasttext_model is not None:
        print("\nDil tespiti filtrelemesi uygulanıyor (fasttext)...")
        before_lang = len(dataset)
        dataset = dataset.filter(
            lambda x: filter_by_language(
                x["text"],
                fasttext_model,
                params["lang_id_label"],
                params["lang_id_min_cutoff"],
            ),
            num_proc=1,
            desc="Dil tespiti",
        )
        _print_stats("Dil tespiti filtresi", before_lang, len(dataset))

    # ------------------------------------------------------------------
    # 6. Sonuçları kaydet
    # ------------------------------------------------------------------
    print(f"\nFiltrelenmiş veri seti kaydediliyor → {args.output_path}")
    dataset.save_to_disk(args.output_path)

    print("\n--- Özet ---")
    print(f"Başlangıç : {initial_size:,}")
    print(f"Son       : {len(dataset):,}")
    print(f"Atılan    : {initial_size - len(dataset):,} ({(initial_size - len(dataset)) / initial_size * 100:.1f}%)")
    print("Tamamlandı.")


def _print_stats(label: str, before: int, after: int) -> None:
    removed = before - after
    pct = removed / before * 100 if before > 0 else 0
    print(f"  {label}: {before:,} → {after:,}  ({removed:,} atıldı, %{pct:.1f})")


if __name__ == "__main__":
    main()
