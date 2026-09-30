#!/usr/bin/env python3

from pathlib import Path
import argparse
import hashlib
import shutil
import sys
import tempfile
import uuid


def fail(message):
    print('FATAL :: ' + message, file=sys.stderr)
    raise SystemExit(1)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish_directory(staged, destination):
    if destination.is_symlink():
        fail("transaction destination may not be a symlink :: " + str(destination))

    destination.parent.mkdir(parents=True, exist_ok=True)

    backup = destination.parent / (
        "." + destination.name + ".backup-" + uuid.uuid4().hex
    )

    had_previous = destination.exists()

    try:
        if had_previous:
            destination.rename(backup)

        staged.rename(destination)

    except Exception as exc:
        rollback_error = None

        if had_previous and backup.exists():
            try:
                backup.rename(destination)
            except Exception as rollback_exc:
                rollback_error = rollback_exc

        if rollback_error is not None:
            fail(
                "transactional publication failed and rollback also failed :: "
                + repr(exc)
                + " :: rollback :: "
                + repr(rollback_error)
            )

        fail(
            "transactional publication failed; previous destination restored :: "
            + repr(exc)
        )

    if had_previous and backup.exists():
        try:
            shutil.rmtree(backup)
        except Exception as exc:
            fail(
                "transaction committed but backup cleanup failed :: "
                + str(backup)
                + " :: "
                + repr(exc)
            )


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

destination.parent.mkdir(parents=True, exist_ok=True)

stage = Path(
    tempfile.mkdtemp(
        prefix=".construction.stage-",
        dir=str(destination.parent),
    )
)

try:
    stage_marker = stage / ".gitkeep"
    stage_marker.write_text("", encoding="utf-8")
    stage_marker.chmod(0o644)

    for source_path in source_files:
        staged_path = stage / source_path.name

        shutil.copy2(source_path, staged_path)
        staged_path.chmod(0o644)

        if sha(source_path) != sha(staged_path):
            fail(
                "staged construction declaration differs from CUSTOM :: "
                + source_path.name
            )

    publish_directory(stage, destination)

finally:
    if stage.exists():
        shutil.rmtree(stage)

print("GREEN :: CUSTOM construction declarations materialized into BUILD")
print("DECLARATIONS :: " + str(len(source_files)))

for source_path in source_files:
    destination_path = destination / source_path.name

    if sha(source_path) != sha(destination_path):
        fail(
            "committed construction declaration differs from CUSTOM :: "
            + source_path.name
        )

    print(source_path.name + " :: " + sha(destination_path))
