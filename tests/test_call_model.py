import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import pandas as pd

from youtube_triage.call_model import load_clip, main


class RawCallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.csv = self.root / "clips.csv"
        self.rows = [
            {"title": "Decoy", "transcript_timestamped": "Do not send this row",
             "frame_captions_timestamped": "Decoy caption", "duration_seconds": 10,
             "ground_truth_label": "remove"},
            {"title": "Selected title", "transcript_timestamped": "[00:00-00:05] CSV transcript",
             "frame_captions_timestamped": "[00:03] CSV frame", "duration_seconds": 8,
             "ground_truth_label": "secret evaluation label"},
        ]
        pd.DataFrame(self.rows).to_csv(self.csv, index=False)
        (self.root / ".env").write_text('model="test/free"\nmodel_auth_key="test-key"\n')
        self.config = self.root / "config.yaml"
        self.config.write_text(
            'provider: openrouter\napi_base_url: "https://openrouter.ai/api/v1"\n'
            'env_file: ".env"\nmodel_variable: model\napi_key_variable: model_auth_key\n'
            'temperature: 0\nmax_tokens: 1600\n'
        )
        self.output = self.root / "reply.md"
        self.args = [str(self.csv), "--title", "Selected title", "--config", str(self.config),
                     "--output", str(self.output)]

    def test_csv_selection_and_raw_http_reply(self):
        # Malformed JSON and whitespace in model content must remain untouched.
        content = '\n {"decision":"keep"}}  \n'
        envelope = {"model": "test/actual-provider", "choices": [
            {"finish_reason": "stop", "message": {"content": content}}]}
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(envelope).encode())) as send:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                main(self.args)
        request = send.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "test/free")
        clip = json.loads(payload["messages"][1]["content"])
        self.assertEqual(clip, {"transcript_timestamped": self.rows[1]["transcript_timestamped"],
                                "frame_captions_timestamped": self.rows[1]["frame_captions_timestamped"],
                                "duration_seconds": 8.0})
        self.assertNotIn("secret evaluation label", request.data.decode())
        self.assertNotIn("Do not send this row", request.data.decode())
        expected = "Response model: test/actual-provider\nFinish reason: stop\n" + content + "\n"
        self.assertEqual(stdout.getvalue(), expected)
        self.assertEqual(self.output.read_bytes(), expected.encode())
        self.assertIn("Loaded 2 clips", stderr.getvalue())

    def test_duplicate_title_is_rejected(self):
        self.rows[0]["title"] = "Selected title"
        pd.DataFrame(self.rows).to_csv(self.csv, index=False)
        with self.assertRaisesRegex(ValueError, "found 2"):
            load_clip(self.csv, "Selected title")

    def test_failed_call_does_not_overwrite_reply(self):
        self.output.write_bytes(b"existing unedited reply")
        error = urllib.error.HTTPError("https://openrouter.ai", 429, "rate limit", {}, None)
        with patch("urllib.request.urlopen", side_effect=error):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exit:
                main(self.args)
        self.assertEqual(exit.exception.code, 1)
        self.assertEqual(self.output.read_bytes(), b"existing unedited reply")


if __name__ == "__main__":
    unittest.main()
