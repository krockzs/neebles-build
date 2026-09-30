#!/usr/bin/env python3

from pathlib import Path
import argparse
import hashlib
import shutil
import sys


def fail(message):
    print('FATAL :: ' + message, file=sys.stderr)
    raise SystemExit(1)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_subject(subject):
    if not subject:
        return False
    if subject in {'.', '..'}:
        return False
    for character in subject:
        if not (
            character.isascii()
            and (character.isalnum() or character in {'.', '-', '_'})
        ):
            return False
    return True


parser = argparse.ArgumentParser()
parser.add_argument('--custom-root', required=True)
parser.add_argument('--build-root', required=True)
args = parser.parse_args()

custom_root = Path(args.custom_root).resolve()
build_root = Path(args.build_root).resolve()

source = custom_root / 'runtime' / 'construction'
destination = (
    build_root
    / 'config'
    / 'includes.chroot'
    / 'usr'
    / 'lib'
    / 'neebles'
    / 'domestic'
    / 'construction'
)

if not source.is_dir():
    fail('CUSTOM construction namespace missing :: ' + str(source))

source_files = []

for child in sorted(source.iterdir(), key=lambda item: item.name):
    if child.name == '.gitkeep':
        if child.is_symlink() or not child.is_file():
            fail('invalid CUSTOM construction marker')
        continue

    if child.is_symlink():
        fail('construction declaration may not be a symlink :: ' + child.name)

    if not child.is_file():
        fail('construction namespace may contain only files :: ' + child.name)

    if child.suffix != '.json':
        fail('construction declaration must use .json :: ' + child.name)

    if not valid_subject(child.stem):
        fail('unsafe construction subject filename :: ' + child.name)

    source_files.append(child)

destination.mkdir(parents=True, exist_ok=True)

for child in sorted(destination.iterdir(), key=lambda item: item.name):
    if child.name == '.gitkeep':
        continue

    if child.is_symlink():
        fail('unexpected destination symlink :: ' + child.name)

    if child.is_dir():
        fail('unexpected destination directory :: ' + child.name)

    if child.suffix != '.json':
        fail('unexpected destination file :: ' + child.name)

    child.unlink()

destination_marker = destination / '.gitkeep'

if not destination_marker.exists():
    destination_marker.write_text('', encoding='utf-8')

for source_path in source_files:
    destination_path = destination / source_path.name
    shutil.copy2(source_path, destination_path)
    destination_path.chmod(0o644)

    if sha(source_path) != sha(destination_path):
        fail(
            'materialized construction declaration differs from CUSTOM :: '
            + source_path.name
        )

print('GREEN :: CUSTOM construction declarations materialized into BUILD')
print('DECLARATIONS :: ' + str(len(source_files)))

for source_path in source_files:
    print(source_path.name + ' :: ' + sha(source_path))
