"""Environment and dataset preflight. Does not train or certify research gates."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def doctor() -> dict[str, Any]:
    result: dict[str, Any] = {"report_only_not_gate_pass": True,
        "python": platform.python_version(), "platform": platform.platform(),
        "free_disk_gib": round(shutil.disk_usage(Path.cwd()).free / 2**30, 2), "packages": {}}
    for package in ("numpy", "Pillow", "torch", "torchvision", "mmcv", "mmengine", "mmsegmentation", "mmdet", "mmpretrain"):
        try:
            result["packages"][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result["packages"][package] = None
    try:
        run = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=10, check=False)
        result["nvidia_smi"] = {"returncode": run.returncode, "stdout": run.stdout.strip(), "stderr": run.stderr.strip()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["nvidia_smi"] = {"error": str(exc)}
    if result["packages"]["torch"]:
        try:
            import torch
            result["torch_cuda"] = {"available": torch.cuda.is_available(), "runtime": torch.version.cuda,
                "compiled_arches": torch.cuda.get_arch_list() if torch.cuda.is_available() else []}
            if torch.cuda.is_available():
                result["torch_cuda"]["devices"] = [{"name": torch.cuda.get_device_name(i),
                    "capability": list(torch.cuda.get_device_capability(i))} for i in range(torch.cuda.device_count())]
        except Exception as exc:
            result["torch_import_error"] = f"{type(exc).__name__}: {exc}"
    return result


def image_map(folder: Path) -> dict[str, Path]:
    if not folder.is_dir():
        raise ValueError(f"Missing directory: {folder}")
    found: dict[str, Path] = {}
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
            key = path.relative_to(folder).with_suffix("").as_posix()
            if key in found:
                raise ValueError(f"Ambiguous duplicate stem: {folder}/{key}")
            found[key] = path
    if not found:
        raise ValueError(f"No supported images in {folder}")
    return found


def audit(root: Path, splits: list[str]) -> dict[str, Any]:
    import numpy as np
    from PIL import Image
    pairs: dict[str, tuple[str, str]] = {}
    images: dict[str, tuple[str, str, str]] = {}
    manifest, warnings, errors, summary = [], [], [], {}
    for split in splits:
        if split not in {"train", "val", "test"}:
            raise ValueError(f"Unsupported split: {split}")
        maps = {name: image_map(root/split/name) for name in ("A", "B", "label")}
        keys = set(maps["A"])
        if not all(set(mapping) == keys for mapping in maps.values()):
            raise ValueError(f"{split}: A/B/label filenames do not match")
        label_values: Counter[int] = Counter()
        for key in sorted(keys):
            arrays = {}
            for name in maps:
                with Image.open(maps[name][key]) as image:
                    arrays[name] = np.array(image)
            a, b, label = arrays["A"], arrays["B"], arrays["label"]
            if a.shape != b.shape or a.shape[:2] != label.shape[:2]:
                raise ValueError(f"Shape mismatch: {split}/{key}")
            if a.ndim != 3 or a.shape[2] != 3:
                raise ValueError(f"Expected 3-channel RGB image: {split}/{key}")
            if label.ndim == 3 and label.shape[2] in (3, 4):
                if not (np.array_equal(label[..., 0], label[..., 1]) and np.array_equal(label[..., 0], label[..., 2])):
                    raise ValueError(f"Colored semantic label requires explicit conversion: {split}/{key}")
                label = label[..., 0]
            if label.ndim != 2:
                raise ValueError(f"Expected grayscale label: {split}/{key}")
            values, counts = np.unique(label, return_counts=True)
            if not set(values.tolist()).issubset({0, 1, 255}) or (1 in values and 255 in values):
                raise ValueError(f"Ambiguous label encoding at {split}/{key}: {values.tolist()}")
            label_values.update({int(v): int(c) for v, c in zip(values, counts)})
            hashes = []
            for temporal, image in (("A", a), ("B", b)):
                digest = hashlib.sha256(str((image.shape, str(image.dtype))).encode()+image.tobytes()).hexdigest()
                hashes.append(digest)
                old = images.get(digest)
                if old and old[0] != split:
                    warnings.append(f"Repeated single image across splits: {old} and {(split, key, temporal)}")
                images.setdefault(digest, (split, key, temporal))
            pair_hash = hashlib.sha256("|".join(sorted(hashes)).encode()).hexdigest()
            old_pair = pairs.get(pair_hash)
            if old_pair and old_pair[0] != split:
                errors.append(f"Repeated image pair across splits: {old_pair} and {(split, key)}")
            pairs.setdefault(pair_hash, (split, key))
            manifest.append({"split": split, "key": key, "shape": list(a.shape), "a_sha256": hashes[0], "b_sha256": hashes[1],
                "label_sha256": hashlib.sha256(str((label.shape, str(label.dtype))).encode()+label.tobytes()).hexdigest()})
        if label_values.get(1, 0) and label_values.get(255, 0):
            errors.append(f"Mixed 0/1 and 0/255 label encodings in {split}; normalize explicitly")
        summary[split] = {"pairs": len(keys), "label_values": sorted(label_values.keys())}
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"structural_check_passed": not errors, "manual_review_required": True,
        "limitations": "Does not certify official split provenance, near-duplicates, spatial overlap, semantics or licenses.",
        "summary": summary, "warnings": warnings, "errors": errors, "manifest_sha256": digest, "manifest": manifest}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    env = sub.add_parser("doctor")
    env.add_argument("--out", type=Path, default=Path("reports/environment.json"))
    data = sub.add_parser("audit")
    data.add_argument("--root", type=Path, required=True)
    data.add_argument("--splits", nargs="+", choices=("train", "val", "test"), default=["train", "val", "test"])
    data.add_argument("--out", type=Path, default=Path("reports/data_audit.json"))
    args = parser.parse_args()
    try:
        result = doctor() if args.command == "doctor" else audit(args.root, args.splits)
        write_json(args.out, result)
        print(json.dumps({k: v for k, v in result.items() if k != "manifest"}, ensure_ascii=False, indent=2))
        return 1 if result.get("errors") else 0
    except (OSError, ValueError, ImportError) as exc:
        write_json(args.out, {"structural_check_passed": False, "error": str(exc)})
        print(f"CHECK FAILED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
