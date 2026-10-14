#!/usr/bin/env python3
"""Prevent BUILD from booting stale CUSTOM Calamares slideshow runtime."""
import ast
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / 'config/includes.chroot/usr/lib/neebles/neebles-calamares-slides'
PRODUCTIVE = ROOT / 'config/includes.chroot/opt/neebles-build/calamares/rootfs/usr/lib/neebles/neebles-calamares-slides'
MANIFEST = ROOT / 'config/includes.chroot/opt/neebles-build/calamares/current_manifest.json'
LAUNCHER = ROOT / 'config/includes.chroot/usr/bin/neebles-installer'
KEY = 'rootfs/usr/lib/neebles/neebles-calamares-slides'


def load_validator(script):
    tree = ast.parse(script.read_text(encoding='utf-8'))
    names = {'MAX_TEXT_SIZE', 'LOCALE_HEADER_RE', 'TAG_RE', 'ALLOWED_CONTENT_TAGS'}
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name == 'validate_text_bytes':
            nodes.append(node)
    assert len(nodes) == len(names) + 1
    scope = {'re': re}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(script), 'exec'), scope)
    return scope['validate_text_bytes']


class CalamaresProductiveParity(unittest.TestCase):
    def test_real_launcher_calls_productive_not_standalone(self):
        launcher = LAUNCHER.read_text(encoding='utf-8')
        self.assertIn('/opt/neebles-build/calamares/rootfs/usr/lib/neebles/neebles-calamares-slides', launcher)

    def test_productive_is_canonical(self):
        self.assertEqual(PRODUCTIVE.read_bytes(), CANONICAL.read_bytes())

    def test_productive_manifest_digest(self):
        entries = json.loads(MANIFEST.read_text(encoding='utf-8'))['entries']
        matching = [e for e in entries if e['path'] == KEY]
        self.assertEqual(len(matching), 1)
        entry = matching[0]
        content = PRODUCTIVE.read_bytes()
        self.assertEqual(entry['size'], len(content))
        self.assertEqual(entry['sha256'], hashlib.sha256(content).hexdigest())
        self.assertEqual(entry['mode'], '0o755')

    def test_actual_productive_accepts_link_with_regional_locales(self):
        example = ("[es_CL]\n[heading]\nNEEBLES CONNECT\n[/heading]\n"
                   "[body]\nConexión SSH\n[/body]\n"
                   "[link=https://www.google.cl]\nLeer más\n[/link]\n"
                   "[ca@valencia]\n[heading]\nCONNECT\n[/heading]\n"
                   "[body]\nConnexió\n[/body]\n"
                   "[link=https://www.google.cl]\nVisitar\n[/link]\n").encode('utf-8')
        self.assertTrue(load_validator(PRODUCTIVE)(example))


if __name__ == '__main__':
    unittest.main()
