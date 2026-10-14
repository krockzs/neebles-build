#!/usr/bin/env python3
"""Calamares text contract regression, without starting the BUILD service."""
import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "config/includes.chroot/usr/lib/neebles/neebles-calamares-slides"
QML = ROOT / "config/includes.chroot/etc/calamares/branding/neebles/show.qml"


def load_validator():
    tree = ast.parse(SERVICE.read_text(encoding="utf-8"), filename=str(SERVICE))
    names = {"MAX_TEXT_SIZE", "LOCALE_HEADER_RE", "TAG_RE", "ALLOWED_CONTENT_TAGS"}
    selected = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names
            for target in node.targets
        ):
            selected.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name == "validate_text_bytes":
            selected.append(node)
    assert len(selected) == len(names) + 1, "Unexpected validator AST"
    context = {"re": re}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(SERVICE), "exec"), context)
    return context["validate_text_bytes"]


def slide(*locales, link="https://www.google.cl"):
    return "\n".join(
        f"[{locale}]\n"
        "[heading]\nNEEBLES CONNECT\n[/heading]\n"
        "[body]\n<b>SSH</b>, VNC y Tailscale.\n[/body]\n"
        f"[link={link}]\nMás información\n[/link]\n"
        for locale in locales
    ).encode("utf-8")


class CalamaresTextContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validate = staticmethod(load_validator())

    def test_multilingual_slides_with_https_links(self):
        self.assertTrue(self.validate(slide(
            "ar", "es_CL", "en_US", "ca@valencia",
            "ca_ES@valencia", "sr@latin", "sr_RS@latin"
        )))

    def test_reject_unsafe_links(self):
        for link in ("http://example.org", "javascript:alert(1)",
                     "file:///etc/passwd", 'https://example.org"onclick="x'):
            with self.subTest(link=link):
                self.assertFalse(self.validate(slide("es_CL", link=link)))

    def test_reject_unbalanced_tags(self):
        self.assertFalse(self.validate(b"[en_US]\n[body]\nUnclosed\n"))
        self.assertFalse(self.validate(b"[en_US]\n[/link]\n"))

    def test_reject_invalid_utf8_and_oversize(self):
        self.assertFalse(self.validate(b"\xff"))
        self.assertFalse(self.validate(b"x" * (64 * 1024 + 1)))

    def test_qml_locale_variants_and_link(self):
        source = QML.read_text(encoding="utf-8")
        self.assertIn("(?:@[A-Za-z0-9_-]+)?", source)
        self.assertIn("parseSlideLink(content)", source)


if __name__ == "__main__":
    unittest.main()
