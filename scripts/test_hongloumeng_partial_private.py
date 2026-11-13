#!/usr/bin/env python3
import copy
import json
import unittest
from unittest.mock import patch
from hongloumeng_partial_private import DATA, inspect_partial, render


class PartialPrivateTests(unittest.TestCase):
    def setUp(self):
        self.draft = {"schemaVersion": 1, "language": "ja", "number": 6,
                      "status": "partial_owner_translation_needed", "complete": False,
                      "blocks": [{"sourceIndex": 0, "sourceSegments": [
                          {"start": 0, "end": 2, "sourceText": "SOURCE_ONLY_A", "text": "前の訳"},
                          {"start": 2, "end": 5, "status": "owner_translation_needed",
                           "sourceTextSha256": "a" * 64, "label": "【日訳未完 CH006-P01】"},
                          {"start": 5, "end": 9, "sourceText": "SOURCE_ONLY_B", "text": "後の訳"}]},
                          {"sourceIndex": 1, "sourceText": "SOURCE_ONLY_C", "text": "通常の訳"}]}

    def test_visible_order_and_unfinished_notice(self):
        output = render(self.draft)
        self.assertLess(output.index("前の訳"), output.index("【日訳未完 CH006-P01】"))
        self.assertLess(output.index("【日訳未完 CH006-P01】"), output.index("後の訳"))
        self.assertIn("未完成", output)
        self.assertIn("noindex,nofollow", output)
        self.assertIn("id=\"CH006-P01\"", output)
        self.assertNotIn("SOURCE_ONLY", output)

    def test_no_files_read_during_render(self):
        with patch("pathlib.Path.read_text", side_effect=AssertionError("No source file reads allowed")):
            render(self.draft)

    def test_missing_translation_never_falls_back(self):
        self.draft["blocks"][1].pop("text")
        with self.assertRaises(ValueError): render(self.draft)

    def test_missing_segment_never_falls_back(self):
        self.draft["blocks"][0]["sourceSegments"][0].pop("text")
        with self.assertRaises(ValueError): render(self.draft)

    def test_owner_payload_fields_rejected(self):
        for key in ("text", "sourceText", "body", "notes"):
            draft = copy.deepcopy(self.draft)
            draft["blocks"][0]["sourceSegments"][1][key] = "synthetic forbidden payload"
            with self.assertRaises(ValueError): render(draft)

    def test_wrong_label_rejected(self):
        self.draft["blocks"][0]["sourceSegments"][1]["label"] = "generic placeholder"
        with self.assertRaises(ValueError): render(self.draft)

    def test_complete_rejected(self):
        self.draft["complete"] = True
        with self.assertRaises(ValueError): render(self.draft)

    def test_escaping(self):
        self.draft["blocks"][1]["text"] = "<script>\n訳"
        output = render(self.draft)
        self.assertNotIn("<script>", output)
        self.assertIn("&lt;script&gt;<br>訳", output)

    def test_renderer_does_not_mutate_draft(self):
        before = copy.deepcopy(self.draft)
        render(self.draft)
        self.assertEqual(before, self.draft)

    def test_six_repository_placeholders_and_exact_ranges(self):
        expected = {6: [(0, 66, 109), (3, 0, 14), (3, 41, 135)],
                    9: [(19, 79, 117), (22, 30, 57)], 12: [(11, 40, 58)]}
        ids = []
        for n, ranges in expected.items():
            draft = json.loads((DATA / "chapters" / f"ch{n:03}.partial.json").read_text())
            entries = inspect_partial(draft)
            self.assertEqual([(e["sourceBlockIndex"], e["start"], e["end"]) for e in entries], ranges)
            output = render(draft)
            for e in entries:
                ids.append(e["id"])
                self.assertEqual(output.count(e["label"]), 1)
                self.assertEqual(output.count("id=\"" + e["id"] + "\""), 1)
        self.assertEqual(len(ids), 6)
        self.assertEqual(len(set(ids)), 6)


    def test_chapter65_four_metadata_only_placeholders(self):
        draft = json.loads((DATA / "chapters/ch065.partial.json").read_text())
        entries = inspect_partial(draft)
        self.assertEqual([(e["sourceBlockIndex"], e["start"], e["end"]) for e in entries],
                         [(0, 207, 228), (12, 25, 80), (18, 0, 175), (19, 134, 211)])
        self.assertEqual([e["id"] for e in entries], [f"CH065-P{i:02}" for i in range(1, 5)])
        output = render(draft)
        self.assertEqual(output.count("data-source-block="), 39)
        for entry in entries:
            self.assertEqual(output.count(entry["label"]), 1)
            self.assertEqual(output.count('id="' + entry["id"] + '"'), 1)

if __name__ == "__main__":
    unittest.main()
