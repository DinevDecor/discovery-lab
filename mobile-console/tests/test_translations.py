import _pathsetup  # noqa: F401
import json
import unittest
from pathlib import Path

from mobile_console.translations import source_hash, valid_entries


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class TranslationCacheTests(unittest.TestCase):
    def test_valid_translation_requires_exact_source_hash(self):
        source = "A source sentence"
        digest = source_hash(source)
        cache = {
            "entries": {
                digest: {"source": source, "bg": "Изречение от източника", "source_sha256": digest}
            }
        }
        self.assertIn(digest, valid_entries(cache))

    def test_changed_source_invalidates_old_translation(self):
        old = "Old source text"
        digest = source_hash(old)
        cache = {
            "entries": {
                digest: {"source": "Changed source text", "bg": "Стар превод", "source_sha256": digest}
            }
        }
        self.assertEqual({}, valid_entries(cache))

    def test_declared_hash_mismatch_invalidates_translation(self):
        source = "Exact source"
        digest = source_hash(source)
        cache = {
            "entries": {
                digest: {"source": source, "bg": "Точен източник", "source_sha256": "bad-hash"}
            }
        }
        self.assertEqual({}, valid_entries(cache))

    def test_checked_in_cache_is_derived_and_well_formed(self):
        data = json.loads((SITE / "translations-bg.json").read_text(encoding="utf-8"))
        self.assertEqual(1, data["version"])
        self.assertEqual("bg", data["language"])
        self.assertIsInstance(data["entries"], dict)
        self.assertEqual(data["entries"], valid_entries(data))


class BulgarianDisplaySafetyTests(unittest.TestCase):
    def test_default_document_language_is_bulgarian(self):
        html = (SITE / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="bg">', html)
        self.assertIn('<script src="bg-ui.js"></script>', html)

    def test_browser_layer_has_no_api_key_or_model_endpoint(self):
        js = (SITE / "bg-ui.js").read_text(encoding="utf-8")
        for forbidden in ("OPENAI_API_KEY", "api.openai.com", "/v1/chat/completions", "sk-"):
            self.assertNotIn(forbidden, js)

    def test_original_language_toggle_is_present(self):
        js = (SITE / "bg-ui.js").read_text(encoding="utf-8")
        self.assertIn("machine-console-language", js)
        self.assertIn("Покажи оригинала", js)
        self.assertIn('language === "bg" ? "en" : "bg"', js)

    def test_translation_cache_is_read_only_in_browser(self):
        js = (SITE / "bg-ui.js").read_text(encoding="utf-8")
        self.assertIn('fetch(CACHE_URL, { cache: "no-cache" })', js)
        for method in ('method: "POST"', "method: 'POST'", 'method: "PUT"', 'method: "PATCH"', 'method: "DELETE"'):
            self.assertNotIn(method, js)


if __name__ == "__main__":
    unittest.main()
