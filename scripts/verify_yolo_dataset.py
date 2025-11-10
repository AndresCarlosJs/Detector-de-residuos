import os
import json
from pathlib import Path


def find_files(root: Path, exts):
    for p in root.rglob("*"):
        if p.suffix.lower() in exts and p.is_file():
            yield p


def verify(dataset_root: Path):
    result = {"splits": {}, "labels_dir_counts": {}}
    exts_img = {".jpg", ".jpeg", ".png"}

    for split in ("train", "val", "test"):
        split_dir = dataset_root / split
        images = [p for p in find_files(split_dir, exts_img)] if split_dir.exists() else []
        labels_next_to_images = []
        orphan_images = []

        for img in images:
            lbl = img.with_suffix('.txt')
            if lbl.exists():
                labels_next_to_images.append(lbl)
            else:
                orphan_images.append(img)

        result['splits'][split] = {
            'images_count': len(images),
            'labels_next_to_images_count': len(labels_next_to_images),
            'orphan_images_count': len(orphan_images),
            'orphan_images_sample': [str(p.relative_to(dataset_root)) for p in orphan_images[:20]]
        }

    # Count label files stored under labels/ (common separate folder)
    labels_dir = dataset_root / 'labels'
    labels_in_labels_dir = []
    if labels_dir.exists():
        for p in find_files(labels_dir, {'.txt'}):
            labels_in_labels_dir.append(p)

    result['labels_dir_counts'] = {
        'labels_count': len(labels_in_labels_dir),
        'labels_sample': [str(p.relative_to(dataset_root)) for p in labels_in_labels_dir[:30]]
    }

    # Cross-check: how many labels in labels/ have a corresponding image under train/val/test
    img_basenames = {}
    for split in ('train', 'val', 'test'):
        split_dir = dataset_root / split
        if not split_dir.exists():
            continue
        for p in find_files(split_dir, exts_img):
            img_basenames.setdefault(p.stem, []).append(p)

    labels_with_image = []
    orphan_labels_in_labels_dir = []
    for lbl in labels_in_labels_dir:
        stem = lbl.stem
        if stem in img_basenames:
            labels_with_image.append(lbl)
        else:
            orphan_labels_in_labels_dir.append(lbl)

    result['labels_dir_counts']['labels_with_image_count'] = len(labels_with_image)
    result['labels_dir_counts']['orphan_labels_count'] = len(orphan_labels_in_labels_dir)
    result['labels_dir_counts']['orphan_labels_sample'] = [str(p.relative_to(dataset_root)) for p in orphan_labels_in_labels_dir[:30]]

    return result


def main():
    # dataset path as in dataset.yaml (relative to repository root)
    repo_root = Path(__file__).resolve().parents[1]
    ds_rel = Path('ControlResiduos') / 'datasets' / 'garbage_classification'
    ds = repo_root / ds_rel
    if not ds.exists():
        print(f"Dataset path not found: {ds}")
        return

    report = verify(ds)
    out_json = Path(__file__).resolve().parents[0] / 'verify_report.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"Wrote report to {out_json}")


if __name__ == '__main__':
    main()
