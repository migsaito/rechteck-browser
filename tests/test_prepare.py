import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prepare", ROOT / "scripts/prepare.py")
prepare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare)
spec2 = importlib.util.spec_from_file_location("collect", ROOT / "scripts/collect.py")
collect = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(collect)


class PrepareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name)
        self.brand = self.source / "browser/branding/unofficial"
        fixtures = {
            "mach": "# fixture, not a Mozilla source tree\n",
            "browser/branding/unofficial/configure.sh": "MOZ_APP_DISPLAYNAME=Nightly\n",
            "browser/branding/unofficial/moz.build": 'DIRS += ["content", "locales"]\n',
            "browser/branding/unofficial/locales/en-US/brand.ftl": "\n".join(f"{key} = Nightly" for key in ("-brand-shorter-name", "-brand-short-name", "-brand-shortcut-name", "-brand-full-name", "-brand-product-name", "-vendor-short-name")),
            "browser/branding/unofficial/locales/en-US/brand.properties": "\n".join(f"{key}=Nightly" for key in ("brandShorterName", "brandShortName", "brandFullName")),
            "browser/branding/unofficial/branding.nsi": "\n".join(f'!define {key}   "old"' for key in ("BrandFullNameInternal", "BrandFullName", "CompanyName", "URLInfoAbout", "HelpLink", "URLManualDownload")),
            "browser/app/profile/firefox.js": 'pref("xpinstall.signatures.required", true);\n',
            "browser/base/content/browser.css": ":root { color: black; }\n",
        }
        for relative, text in fixtures.items():
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        (self.brand / "firefox.ico").write_bytes(b"old")
        (self.brand / "default32.png").write_bytes(prepare.png(32))

    def test_idempotent_and_preserves_upstream_extension_security(self):
        prepare.apply(self.source)
        paths = [p for p in self.source.rglob("*") if p.is_file()]
        first = {p: p.read_bytes() for p in paths}
        prepare.apply(self.source)
        self.assertEqual(first, {p: p.read_bytes() for p in paths})
        prefs = (self.source / "browser/app/profile/firefox.js").read_text()
        self.assertIn('pref("xpinstall.signatures.required", true)', prefs)
        self.assertEqual(prefs.count(prepare.START), 1)
        brand = self.source / "browser/branding/rechteck"
        self.assertIn("Rechteck Browser", (brand / "branding.nsi").read_text())
        self.assertEqual((self.brand / "firefox.ico").read_bytes(), b"old")
        self.assertEqual(struct.unpack("<HHH", (brand / "firefox.ico").read_bytes()[:6]), (0, 1, 6))

    def test_missing_assignment_fails_before_mutation(self):
        (self.brand / "configure.sh").write_text("unexpected\n")
        with self.assertRaises(ValueError):
            prepare.apply(self.source)
        self.assertFalse((self.source / "browser/branding/rechteck").exists())

    def test_existing_user_config_is_not_overwritten(self):
        config = self.source / "mozconfig"
        config.write_text("my configuration")
        with self.assertRaises(ValueError):
            prepare.apply(self.source)
        self.assertEqual(config.read_text(), "my configuration")

    def test_dry_run_does_not_write(self):
        prepare.apply(self.source, dry_run=True)
        self.assertFalse((self.source / "mozconfig").exists())
        self.assertFalse((self.source / "browser/branding/rechteck").exists())

    def test_rejects_non_source_directory(self):
        (self.source / "mach").unlink()
        with self.assertRaises(ValueError):
            prepare.apply(self.source)

    def test_installer_collector_rejects_missing_or_ambiguous_installer(self):
        output = self.source / "output"
        with self.assertRaises(ValueError):
            collect.collect(self.source, output)
        (self.source / "one.installer.exe").write_bytes(b"fixture")
        (self.source / "two.installer.exe").write_bytes(b"fixture")
        with self.assertRaises(ValueError):
            collect.collect(self.source, output)

    def test_collector_writes_provenance_and_checksum(self):
        (self.source / "one.installer.exe").write_bytes(b"fixture installer")
        target = collect.collect(self.source, self.source / "output")
        self.assertEqual(target.read_bytes(), b"fixture installer")
        self.assertTrue((target.parent / "SHA256SUMS").exists())
        self.assertTrue((target.parent / "build-info.json").exists())


if __name__ == "__main__":
    unittest.main()
