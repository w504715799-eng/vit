"""Small, framework-independent utilities; these are not a change detector."""
from __future__ import annotations
from typing import Any
import numpy as np


def shift_image(image: np.ndarray, dx: int, dy: int) -> tuple[np.ndarray, np.ndarray]:
    """Translate right/down for positive dx/dy; never wrap pixels around.

    Returns a copy and a mask of real pixels in the shifted image. Do NOT
    translate the reference-frame change label with this function.
    """
    image = np.asarray(image)
    if image.ndim not in (2, 3):
        raise ValueError("Expected HxW or HxWxC image")
    if isinstance(dx, bool) or isinstance(dy, bool) or not isinstance(dx, (int, np.integer)) or not isinstance(dy, (int, np.integer)):
        raise ValueError("dx/dy must be integer pixels")
    h, w = image.shape[:2]
    if h == 0 or w == 0 or abs(dx) >= w or abs(dy) >= h:
        raise ValueError("Shift must leave a nonempty image overlap")
    out = np.zeros_like(image)
    valid = np.zeros((h, w), dtype=bool)
    x0, x1 = max(0, dx), min(w, w + dx)
    y0, y1 = max(0, dy), min(h, h + dy)
    out[y0:y1, x0:x1] = image[y0-dy:y1-dy, x0-dx:x1-dx]
    valid[y0:y1, x0:x1] = True
    return out, valid


def common_mask(shape: tuple[int, int], margin: int = 4) -> np.ndarray:
    """Use the SAME mask for clean and all +/-margin translation conditions."""
    h, w = shape
    if not isinstance(margin, int) or isinstance(margin, bool) or margin < 0 or 2*margin >= min(h, w):
        raise ValueError("Invalid common evaluation margin")
    mask = np.zeros((h, w), dtype=bool)
    mask[margin:h-margin, margin:w-margin] = True
    return mask


def binary_counts(pred: np.ndarray, target: np.ndarray, valid: np.ndarray | None = None) -> dict[str, int]:
    """Inputs must ALREADY be binary {0,1}; ignore pixels go in valid only.

    A source mask's white 255 is a positive class, NOT automatically ignore.
    Convert source labels explicitly before invoking this function.
    """
    pred, target = np.asarray(pred), np.asarray(target)
    if pred.ndim != 2 or pred.shape != target.shape:
        raise ValueError("Expected equal HxW prediction and target")
    if not np.isin(pred, [0, 1]).all() or not np.isin(target, [0, 1]).all():
        raise ValueError("Predictions and targets must be binary 0/1")
    if valid is None:
        valid = np.ones(pred.shape, dtype=bool)
    valid = np.asarray(valid)
    if valid.shape != pred.shape or valid.dtype != np.bool_:
        raise ValueError("valid must be an equal-sized Boolean mask")
    if not valid.any():
        raise ValueError("No valid evaluation pixels")
    p, y = pred[valid].astype(bool), target[valid].astype(bool)
    return {"tp": int(np.sum(p & y)), "fp": int(np.sum(p & ~y)),
            "fn": int(np.sum(~p & y)), "tn": int(np.sum(~p & ~y))}


def counts_to_metrics(counts: dict[str, Any]) -> dict[str, float | None]:
    """Aggregate counts across images BEFORE using this for micro metrics.

    Undefined metrics are None, never silently 0 or 1. All rates are 0..1.
    """
    vals = []
    for key in ("tp", "fp", "fn", "tn"):
        value = counts[key]
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)) or value < 0:
            raise ValueError("Counts must be nonnegative integers")
        vals.append(int(value))
    tp, fp, fn, tn = vals
    def ratio(a: int, b: int) -> float | None:
        return a / b if b else None
    return {"f1": ratio(2*tp, 2*tp+fp+fn), "iou": ratio(tp, tp+fp+fn),
            "precision": ratio(tp, tp+fp), "recall": ratio(tp, tp+fn),
            "unchanged_fpr": ratio(fp, fp+tn)}
