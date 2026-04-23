"""
Veri setini HuggingFace'den indir ve diske kaydet.

Kullanım:
  python download_data.py
  python download_data.py --output_dir ./data
"""

import argparse
from datasets import load_dataset


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="musabg/wikipedia-oscar-tr",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./data",
        help="Veri setinin kaydedileceği dizin.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"'{args.dataset_name}' indiriliyor...")
    dataset = load_dataset(args.dataset_name, split="train")

    print(f"Toplam belge: {len(dataset):,}")
    print(f"Sütunlar: {dataset.column_names}")
    print(f"İlk örnek:\n{dataset[0]['text'][:300]}\n")

    print(f"Diske kaydediliyor → {args.output_dir}")
    dataset.save_to_disk(args.output_dir)
    print("İndirme tamamlandı.")


if __name__ == "__main__":
    main()
