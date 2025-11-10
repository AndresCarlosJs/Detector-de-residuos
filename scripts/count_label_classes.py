"""
Cuenta apariciones por clase en etiquetas YOLO dentro del dataset
Revisa recursivamente `ControlResiduos/datasets/garbage_classification/labels`.

Salida: conteo por split (train/val/test), por clase id y por número de archivos que contienen la clase.
"""
from pathlib import Path
import argparse
import collections
import os


def count_labels(base_labels_dir: Path):
    # Estructuras: split -> class_id -> counts
    split_counts = {}
    for split_dir in ['train', 'val', 'test']:
        p = base_labels_dir / split_dir
        counts = collections.Counter()
        files_with = collections.Counter()
        if not p.exists():
            split_counts[split_dir] = {'present': False, 'counts': counts, 'files_with': files_with, 'total_files': 0}
            continue

        txt_files = list(p.rglob('*.txt'))
        split_counts[split_dir] = {'present': True, 'counts': counts, 'files_with': files_with, 'total_files': len(txt_files)}

        for tf in txt_files:
            try:
                seen_in_file = set()
                with tf.open('r', encoding='utf-8') as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        # first token is class id
                        cls = parts[0]
                        counts[cls] += 1
                        seen_in_file.add(cls)
                for cls in seen_in_file:
                    files_with[cls] += 1
            except Exception as e:
                print(f"Warning: error reading {tf}: {e}")

    return split_counts


def pretty_print(results, names_map=None):
    for split, info in results.items():
        print(f"\n== {split.upper()} ==")
        if not info['present']:
            print("  (no existe)")
            continue
        print(f"  total label files: {info['total_files']}")
        counts = info['counts']
        files_with = info['files_with']
        if not counts:
            print("  (no hay etiquetas en este split)")
            continue
        # Sort by numeric class id
        for cls in sorted(counts.keys(), key=lambda x: int(x)):
            name = names_map.get(int(cls)) if names_map else None
            name_str = f" ({name})" if name else ""
            print(f"  class {cls}{name_str}: {counts[cls]} annotations in {files_with.get(cls,0)} files")


def load_names_from_yaml(yaml_path: Path):
    # Simple parser to extract names mapping if dataset.yaml present
    if not yaml_path.exists():
        return None
    names = {}
    try:
        with yaml_path.open('r', encoding='utf-8') as fh:
            for line in fh:
                line = line.rstrip('\n')
                if ':' in line and line.strip().startswith(' '):
                    # line like '  6: knife'
                    parts = line.strip().split(':', 1)
                    try:
                        k = int(parts[0])
                        v = parts[1].strip()
                        names[k] = v
                    except Exception:
                        continue
    except Exception:
        return None
    return names


def main():
    base = Path(__file__).resolve().parents[1] / 'ControlResiduos' / 'datasets' / 'garbage_classification'
    labels_dir = base / 'labels'
    if not labels_dir.exists():
        print(f"Labels directory not found: {labels_dir}")
        return 2

    print(f"Scanning labels under: {labels_dir}")
    results = count_labels(labels_dir)

    yaml_path = base / 'dataset.yaml'
    names = load_names_from_yaml(yaml_path)

    if names:
        print("\nFound dataset.yaml names mapping:")
        for k in sorted(names.keys()):
            print(f"  {k}: {names[k]}")

    pretty_print(results, names_map=names if names else {})
    print('\nDone.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
