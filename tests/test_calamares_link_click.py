#!/usr/bin/env python3
"""Calamares link UI/runtime contract; never launches a real browser."""
import json
import runpy
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
QML = ROOT / "config/includes.chroot/etc/calamares/branding/neebles/show.qml"
WRAPPER = ROOT / "config/includes.chroot/usr/bin/neebles-installer"
HELPER = ROOT / "config/includes.chroot/usr/lib/neebles/neebles-calamares-link-opener"


class LinkContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helper = runpy.run_path(str(HELPER))

    def test_qml_uses_explicit_click_and_displays_url_not_label(self):
        qml = QML.read_text(encoding="utf-8")
        self.assertIn('"http://127.0.0.1:28766/open-link"', qml)
        self.assertIn('onClicked: presentation.requestOpenLink(presentation.slideLink)', qml)
        self.assertIn('cursorShape: Qt.PointingHandCursor', qml)
        self.assertIn('text: presentation.slideLink.replace(/^https:', qml)
        self.assertIn('textFormat: Text.PlainText', qml)
        self.assertNotIn('Qt.openUrlExternally(link)', qml)

    def test_launcher_starts_helper_as_desktop_user(self):
        wrapper = WRAPPER.read_text(encoding="utf-8")
        self.assertIn('neebles-calamares-link-opener', wrapper)
        self.assertIn('"$(id -u)" -ne 0', wrapper)
        self.assertIn('kill "$LINK_OPENER_PID"', wrapper)
        self.assertIn('pkexec /opt/neebles-build/calamares/neebles-calamares-launcher', wrapper)

    def test_validator_https_and_no_credentials(self):
        validate = self.helper["valid_url"]
        self.assertTrue(validate("https://www.google.cl"))
        self.assertTrue(validate("https://example.org/some/path?q=1"))
        for url in (
            "http://example.com", "javascript:alert(1)",
            "https://user:pass@example.org", "https://bad.example/a b",
            "file:///etc/passwd", "https://bad.example:99999/",
        ):
            with self.subTest(url=url):
                self.assertFalse(validate(url))

    def test_only_link_declared_in_active_text_allowed(self):
        allowed = self.helper["allowed_link"]
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "1.txt").write_text(
                "[es_CL]\n[link=https://www.google.cl]\nVisitar sitio web\n[/link]\n",
                encoding="utf-8",
            )
            active = base / "active-slot"
            active.write_text("1", encoding="ascii")
            with patch.dict(allowed.__globals__, {"SLIDES": base, "ACTIVE_SLOT": active}):
                self.assertTrue(allowed(1, "https://www.google.cl"))
                self.assertFalse(allowed(1, "https://evil.example"))
                self.assertFalse(allowed(2, "https://www.google.cl"))
                active.write_text("2", encoding="ascii")
                self.assertFalse(allowed(1, "https://www.google.cl"))

    def test_post_endpoint_dispatches_only_predeclared_url(self):
        opener = self.helper["open_url"]
        handler = self.helper["LinkHandler"]
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "1.txt").write_text(
                "[en_US]\n[link=https://www.google.cl]\nVisit website\n[/link]\n",
                encoding="utf-8",
            )
            active = base / "active-slot"
            active.write_text("1", encoding="ascii")
            calls = []
            with patch.dict(handler.do_POST.__globals__, {
                "SLIDES": base,
                "ACTIVE_SLOT": active,
                "open_url": lambda url: calls.append(url) or True,
            }):
                server = HTTPServer(("127.0.0.1", 0), handler)
                t = threading.Thread(target=server.serve_forever, daemon=True)
                t.start()
                try:
                    endpoint = f"http://127.0.0.1:{server.server_port}/open-link"
                    def post(url):
                        req = urllib.request.Request(
                            endpoint,
                            data=json.dumps({"slot": 1, "url": url}).encode(),
                            headers={"Content-Type": "application/json"},
                            method="POST",
                        )
                        try:
                            with urllib.request.urlopen(req, timeout=2) as response:
                                return response.status
                        except urllib.error.HTTPError as exc:
                            return exc.code
                    self.assertEqual(post("https://www.google.cl"), 200)
                    self.assertEqual(post("https://evil.example"), 403)
                    self.assertEqual(calls, ["https://www.google.cl"])
                finally:
                    server.shutdown()
                    server.server_close()
                    t.join(timeout=2)


    def test_native_kde_default_then_xdg_gio_firefox_fallback(self):
        import subprocess
        from unittest.mock import Mock
        helper = self.helper
        func = helper["open_url"]
        cmds = helper["desktop_openers"]
        with patch.dict(func.__globals__, {"desktop_openers": lambda url: [
            ["/usr/bin/kde-open", url],
            ["/usr/bin/xdg-open", url],
            ["/usr/bin/gio", "open", url],
            ["/usr/bin/firefox-esr", "--new-tab", url],
        ]}):
            with patch.object(func.__globals__["os"], "geteuid", return_value=1000):
                with patch.dict(func.__globals__["os"].environ, {"DISPLAY": ":0"}):
                    outcomes = [1, 1, 0]
                    invocations = []
                    def fake_popen(argv, **kwargs):
                        invocations.append(argv[0])
                        proc = Mock()
                        proc.wait.return_value = outcomes.pop(0)
                        return proc
                    with patch.object(func.__globals__["subprocess"], "Popen", side_effect=fake_popen):
                        self.assertTrue(func("https://www.google.cl"))
                    self.assertEqual(invocations, ["/usr/bin/kde-open", "/usr/bin/xdg-open", "/usr/bin/gio"])

    def test_helper_rejects_root_and_bad_url_before_launch(self):
        func = self.helper["open_url"]
        with patch.object(func.__globals__["os"], "geteuid", return_value=0):
            with patch.object(func.__globals__["subprocess"], "Popen") as popen:
                self.assertFalse(func("https://www.google.cl"))
                popen.assert_not_called()
        with patch.object(func.__globals__["os"], "geteuid", return_value=1000):
            self.assertFalse(func("file:///tmp/exploit"))

    def test_cors_preflight_restricts_origin(self):
        handler = self.helper["LinkHandler"]
        server = HTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/open-link"
            request = urllib.request.Request(url, method="OPTIONS", headers={"Origin": "null", "Access-Control-Request-Method": "POST"})
            with urllib.request.urlopen(request, timeout=3) as response:
                self.assertEqual(response.status, 204)
                self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "null")
            request = urllib.request.Request(url, method="OPTIONS", headers={"Origin": "https://untrusted.example"})
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(request, timeout=3)
            self.assertEqual(cm.exception.code, 403)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_link_failure_is_visible_without_console(self):
        qml = QML.read_text(encoding="utf-8")
        self.assertIn('slideLinkStatus = "⚠ "', qml)
        self.assertIn('text: presentation.slideLinkStatus', qml)
        self.assertIn('id: slideUrlText', qml)
        wrapper = WRAPPER.read_text(encoding="utf-8")
        self.assertIn('calamares-link-opener.log', wrapper)
        self.assertIn('http://127.0.0.1:28766/health', wrapper)


if __name__ == "__main__":
    unittest.main()
