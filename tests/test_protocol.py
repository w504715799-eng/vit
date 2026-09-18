import sys
import tempfile
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from protocol_utils import shift_image, common_mask, binary_counts, counts_to_metrics
from preflight import audit


class ProtocolTests(unittest.TestCase):
    def test_identity_is_copy(self):
        image = np.arange(16).reshape(4, 4)
        shifted, valid = shift_image(image, 0, 0)
        np.testing.assert_array_equal(image, shifted)
        self.assertIsNot(image, shifted)
        self.assertTrue(valid.all())

    def test_right_down_no_wrap(self):
        image = np.arange(25).reshape(5, 5)
        shifted, valid = shift_image(image, 1, 2)
        np.testing.assert_array_equal(shifted[2:, 1:], image[:-2, :-1])
        self.assertEqual(int(valid.sum()), 12)
        self.assertTrue((shifted[:2] == 0).all())

    def test_negative_rgb(self):
        image = np.arange(75).reshape(5, 5, 3)
        shifted, valid = shift_image(image, -2, -1)
        np.testing.assert_array_equal(shifted[:-1, :-2], image[1:, 2:])
        self.assertEqual(int(valid.sum()), 12)

    def test_common_region_for_all_shifts(self):
        image = np.zeros((20, 20, 3))
        common = common_mask((20, 20), 4)
        self.assertEqual(int(common.sum()), 144)
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                _, valid = shift_image(image, dx, dy)
                self.assertTrue(valid[common].all())

    def test_invalid_shift(self):
        for dx in (1.5, 4, True):
            with self.assertRaises(ValueError):
                shift_image(np.zeros((4, 4)), dx, 0)

    def test_invalid_margin(self):
        for margin in (-1, 3, 1.5, True):
            with self.assertRaises(ValueError):
                common_mask((5, 5), margin)

    def test_metrics(self):
        counts = binary_counts(np.array([[1, 1], [0, 0]]), np.array([[1, 0], [1, 0]]))
        self.assertEqual(counts, {"tp": 1, "fp": 1, "fn": 1, "tn": 1})
        self.assertEqual(counts_to_metrics(counts)["f1"], 0.5)
        self.assertAlmostEqual(counts_to_metrics(counts)["iou"], 1/3)

    def test_mask_excludes_errors(self):
        p = np.array([[1, 1], [0, 0]])
        y = np.array([[1, 0], [1, 0]])
        c = binary_counts(p, y, np.array([[True, False], [False, True]]))
        self.assertEqual(counts_to_metrics(c)["f1"], 1)

    def test_white_mask_not_implicitly_ignore(self):
        with self.assertRaises(ValueError):
            binary_counts(np.zeros((2, 2)), np.full((2, 2), 255))

    def test_empty_positives_undefined_f1(self):
        values = counts_to_metrics({"tp": 0, "fp": 0, "fn": 0, "tn": 10})
        self.assertIsNone(values["f1"])
        self.assertEqual(values["unchanged_fpr"], 0)

    def test_invalid_count(self):
        with self.assertRaises(ValueError):
            counts_to_metrics({"tp": -1, "fp": 0, "fn": 0, "tn": 0})

    def test_no_valid_pixels(self):
        with self.assertRaises(ValueError):
            binary_counts(np.zeros((2, 2)), np.zeros((2, 2)), np.zeros((2, 2), dtype=bool))

    def test_cross_split_pair_leakage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for split in ("train", "val"):
                for field in ("A", "B", "label"):
                    (root/split/field).mkdir(parents=True)
                    array = np.zeros((8, 8), dtype=np.uint8) if field == "label" else np.full((8, 8, 3), 100 if field == "A" else 150, dtype=np.uint8)
                    Image.fromarray(array).save(root/split/field/"sample.png")
            report = audit(root, ["train", "val"])
            self.assertFalse(report["structural_check_passed"])
            self.assertTrue(report["errors"])

    def test_missing_dataset_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                audit(Path(directory), ["train"])


if __name__ == "__main__":
    unittest.main()
