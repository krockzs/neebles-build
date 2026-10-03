#!/usr/bin/python3
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

def fail(message):
    raise SystemExit("FATAL :: " + message)

if len(sys.argv) != 2:
    fail("expected component")

component = sys.argv[1]
if component not in {"boss", "calamares"}:
    fail("unsupported component " + component)

house = Path("/opt/neebles-build") / component
manifest_path = house / "current_manifest.json"

if not house.is_dir():
    fail("house missing " + str(house))
if not manifest_path.is_file():
    fail("manifest missing " + str(manifest_path))

data = json.loads(manifest_path.read_text(encoding="utf-8"))
entries = data.get("entries")
if not isinstance(entries, list):
    fail("manifest entries invalid")

applied = 0
skipped_links = 0

for entry in entries:
    path_name = entry.get("path")
    kind = entry.get("type")
    mode_text = entry.get("mode")

    if not isinstance(path_name, str) or not isinstance(mode_text, str):
        fail("invalid manifest entry")

    relative = Path(path_name)
    if relative.is_absolute() or ".." in relative.parts:
        fail("unsafe path " + path_name)

    if not relative.parts or relative.parts[0] not in {"packages", "rootfs"}:
        continue

    target = house / relative
    if not os.path.lexists(target):
        fail("missing declared path " + path_name)

    current = os.lstat(target)

    if kind == "symlink":
        if not stat.S_ISLNK(current.st_mode):
            fail("type mismatch " + path_name)
        expected_target = entry.get("target")
        if not isinstance(expected_target, str):
            fail("invalid symlink target declaration " + path_name)
        if os.readlink(target) != expected_target:
            fail("symlink target mismatch " + path_name)
        skipped_links += 1
        continue

    if kind == "file" and not stat.S_ISREG(current.st_mode):
        fail("type mismatch " + path_name)
    if kind == "file":
        expected_size = entry.get("size")
        expected_sha = entry.get("sha256")
        if not isinstance(expected_size, int) or not isinstance(expected_sha, str):
            fail("invalid file integrity declaration " + path_name)
        if current.st_size != expected_size:
            fail("size mismatch " + path_name)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != expected_sha:
            fail("sha256 mismatch " + path_name)
    if kind == "dir" and not stat.S_ISDIR(current.st_mode):
        fail("type mismatch " + path_name)
    if kind not in {"file", "dir"}:
        fail("unsupported type " + str(kind))

    mode = int(mode_text, 8)
    os.chmod(target, mode, follow_symlinks=False)
    applied += 1

print("GREEN :: CUSTOM RUNTIME METADATA MATERIALIZED :: " + component)
print("APPLIED :: " + str(applied))
print("SYMLINKS SKIPPED :: " + str(skipped_links))
