"""Copy YOLO label .txt files from labels/<split>/* to the matching image directories.

This makes the detection dataset compatible with ultralytics which expects label files
next to images (same directory, same base filename with .txt).

Usage:
    python scripts\sync_yolo_labels.py --root ControlResiduos\datasets\garbage_classification

It will process train, val, test splits and report counts.
"""
import argparse
import os
import shutil
from pathlib import Path


def sync_labels(root: Path) -> None:
    labels_root = root / "labels"
    if not labels_root.exists():
        print(f"No labels/ folder found under {root}")
        return

    splits = [p.name for p in labels_root.iterdir() if p.is_dir()]
    total = 0
    copied = 0

    for split in splits:
        for class_dir in (labels_root / split).iterdir():
            if not class_dir.is_dir():
                continue
            for lbl in class_dir.glob("*.txt"):
                total += 1
                # find matching image in root/<split>/<class>/<name>.*
                img_dir = root / split / class_dir.name
                stem = lbl.stem
                found = False
                if img_dir.exists():
                    for ext in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
                        img_path = img_dir / (stem + ext)
                        if img_path.exists():
                            dst = img_dir / (stem + ".txt")
                            try:
                                shutil.copy2(lbl, dst)
                                copied += 1
                            except Exception as e:
                                print(f"Failed copying {lbl} -> {dst}: {e}")
                            found = True
                            break
                if not found:
                    # try matching in root/<split> (no class subfolder)
                    img_dir2 = root / split
                    for ext in (".jpg", ".jpeg", ".png", ".bmp", ".webp"):
                        img_path = img_dir2 / (stem + ext)
                        if img_path.exists():
                            dst = img_dir2 / (stem + ".txt")
                            try:
                                shutil.copy2(lbl, dst)
                                copied += 1
                            except Exception as e:
                                print(f"Failed copying {lbl} -> {dst}: {e}")
                            found = True
                            break
                if not found:
                    print(f"No image found for label: {lbl}")

    print(f"Labels processed: {total}, copied next to images: {copied}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Path to dataset root (contains train/ val/ test/ and labels/)")
    args = parser.parse_args()
    root = Path(args.root)
    if not root.exists():
        print(f"Dataset root does not exist: {root}")
        return
    sync_labels(root)


if __name__ == "__main__":
    main()
