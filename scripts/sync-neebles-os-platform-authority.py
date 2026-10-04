#!/usr/bin/env python3

from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import uuid

EXPECTED_AUTHORITY_FILES = {
    "authority-supply.json",
    "boss.modules.install_staging.json",
    "boss.modules.update_staging.json",
    "neebles.domestic_workspace.json",
    "platform.filesystem_boundary.json",
    "platform.desktop_session_interface.json",
    "system.dns_resolver_config.json",
    "boss.modules.ipc.json",
    "boss.runtime.json",
    "modules.installed_runtime.json",
    "modules.runtime.json",
}

EXPECTED_PROVIDERS = {
    "neebles-boundary-provider":
        "/usr/lib/neebles/platform/bin/neebles-boundary-provider",
    "neebles-desktop-session-provider":
        "/usr/lib/neebles/platform/bin/neebles-desktop-session-provider",
}

EXPECTED_PROVIDER_INSTALL_PATH = EXPECTED_PROVIDERS[
    "neebles-boundary-provider"
]

EXPECTED_DESKTOP_SESSION_PROVIDER_INSTALL_PATH = EXPECTED_PROVIDERS[
    "neebles-desktop-session-provider"
]

EXPECTED_SUPPLY = {'schema': '1',
 'name': 'neebles-authority-supply',
 'entries': [{'authority': 'platform.filesystem_boundary',
              'location': '/usr/lib/neebles/platform/authority/platform.filesystem_boundary.json'},
             {'authority': 'system.dns_resolver_config',
              'location': '/usr/lib/neebles/platform/authority/system.dns_resolver_config.json'},
             {'authority': 'boss.modules.install_staging',
              'location': '/usr/lib/neebles/platform/authority/boss.modules.install_staging.json'},
             {'authority': 'boss.modules.update_staging',
              'location': '/usr/lib/neebles/platform/authority/boss.modules.update_staging.json'},
             {'authority': 'modules.installed_runtime',
              'location': '/usr/lib/neebles/platform/authority/modules.installed_runtime.json'},
             {'authority': 'neebles.domestic_workspace',
              'location': '/usr/lib/neebles/platform/authority/neebles.domestic_workspace.json'},
             {'authority': 'platform.desktop_session_interface',
              'location': '/usr/lib/neebles/platform/authority/platform.desktop_session_interface.json'},
             {'authority': 'boss.modules.ipc',
              'location': '/usr/lib/neebles/platform/authority/boss.modules.ipc.json'},
             {'authority': 'boss.runtime',
              'location': '/usr/lib/neebles/platform/authority/boss.runtime.json'},
             {'authority': 'modules.runtime',
              'location': '/usr/lib/neebles/platform/authority/modules.runtime.json'}]}

EXPECTED_PLATFORM = {
    "schema": "1",
    "name": "neebles-platform-authority",
    "authority": "platform.filesystem_boundary",
    "protocol": "neebles-filesystem-boundary-v1",
    "provider": EXPECTED_PROVIDER_INSTALL_PATH,
}

EXPECTED_DESKTOP_SESSION_PLATFORM = {
    "schema": "1",
    "name": "neebles-platform-authority",
    "authority": "platform.desktop_session_interface",
    "protocol": "neebles-desktop-session-interface-v1",
    "provider": EXPECTED_DESKTOP_SESSION_PROVIDER_INSTALL_PATH,
}

EXPECTED_EXTERNAL = {
    "schema": "1",
    "name": "neebles-external-data-authority",
    "authority": "system.dns_resolver_config",
    "source": "/etc/resolv.conf",
    "destination": "/etc/resolv.conf",
    "access": "read_only",
}

EXPECTED_WRITABLE = {
    "boss.modules.install_staging.json": {
        "schema": "1",
        "name": "neebles-writable-data-authority",
        "authority": "boss.modules.install_staging",
        "root": "/opt/neebles/shared/tmp",
    },
    "boss.modules.update_staging.json": {
        "schema": "1",
        "name": "neebles-writable-data-authority",
        "authority": "boss.modules.update_staging",
        "root": "/opt/neebles/modules",
    },
    "neebles.domestic_workspace.json": {
        "schema": "1",
        "name": "neebles-writable-data-authority",
        "authority": "neebles.domestic_workspace",
        "root": "/opt/neebles-build",
    },
}

def fail(message):
    print("FATAL :: " + message, file=sys.stderr)
    raise SystemExit(1)

def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        fail("invalid JSON " + str(path) + " :: " + repr(exc))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument("--os-root", required=True)
parser.add_argument("--build-root", required=True)
args = parser.parse_args()

source_platform = Path(args.os_root).resolve() / "platform"
source_authority = source_platform / "authority"
source_providers = {
    name: source_platform / "bin" / name
    for name in EXPECTED_PROVIDERS
}

destination_platform = (
    Path(args.build_root).resolve()
    / "config"
    / "includes.chroot"
    / "usr"
    / "lib"
    / "neebles"
    / "platform"
)

destination_authority = destination_platform / "authority"
destination_providers = {
    name: destination_platform / "bin" / name
    for name in EXPECTED_PROVIDERS
}

if not source_authority.is_dir():
    fail("OS authority source missing :: " + str(source_authority))

actual_files = {
    path.name
    for path in source_authority.iterdir()
    if path.is_file()
}

if actual_files != EXPECTED_AUTHORITY_FILES:
    fail("OS authority source file set mismatch :: " + repr(sorted(actual_files)))

for provider_name, source_provider in source_providers.items():
    if not source_provider.is_file():
        fail(
            "OS platform provider missing :: "
            + provider_name
            + " :: "
            + str(source_provider)
        )

    if not source_provider.stat().st_mode & 0o111:
        fail(
            "OS platform provider is not executable :: "
            + provider_name
        )

if load_json(source_authority / "authority-supply.json") != EXPECTED_SUPPLY:
    fail("AuthoritySupply semantic drift")

if load_json(source_authority / "platform.filesystem_boundary.json") != EXPECTED_PLATFORM:
    fail("filesystem boundary semantic drift")

if (
    load_json(
        source_authority
        / "platform.desktop_session_interface.json"
    )
    != EXPECTED_DESKTOP_SESSION_PLATFORM
):
    fail("desktop session interface semantic drift")

if load_json(source_authority / "system.dns_resolver_config.json") != EXPECTED_EXTERNAL:
    fail("DNS resolver semantic drift")

for name, expected in EXPECTED_WRITABLE.items():
    if load_json(source_authority / name) != expected:
        fail("writable authority semantic drift :: " + name)

destination_platform.parent.mkdir(
    parents=True,
    exist_ok=True,
)

stage_root = Path(
    tempfile.mkdtemp(
        prefix=".platform.stage-",
        dir=str(destination_platform.parent),
    )
)

stage_authority = stage_root / "authority"
stage_bin = stage_root / "bin"

stage_authority.mkdir(parents=True, exist_ok=True)
stage_bin.mkdir(parents=True, exist_ok=True)

for name in sorted(EXPECTED_AUTHORITY_FILES):
    source_path = source_authority / name
    staged_path = stage_authority / name

    shutil.copy2(source_path, staged_path)
    staged_path.chmod(0o644)

    if sha(source_path) != sha(staged_path):
        shutil.rmtree(stage_root)

        fail(
            "staged authority differs from OS source :: "
            + name
        )

for provider_name in sorted(EXPECTED_PROVIDERS):
    source_provider = source_providers[provider_name]
    staged_provider = stage_bin / provider_name

    shutil.copy2(
        source_provider,
        staged_provider,
    )

    staged_provider.chmod(0o755)

    if sha(source_provider) != sha(staged_provider):
        shutil.rmtree(stage_root)

        fail(
            "staged platform provider differs from OS source :: "
            + provider_name
        )

destination_authority.parent.mkdir(
    parents=True,
    exist_ok=True,
)

for destination_provider in destination_providers.values():
    destination_provider.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

transaction_id = uuid.uuid4().hex

backup_root = destination_platform.parent / (
    ".platform.backup-" + transaction_id
)

backup_authority = backup_root / "authority"
backup_bin = backup_root / "bin"

backup_root.mkdir(parents=True, exist_ok=False)
backup_bin.mkdir(parents=True, exist_ok=False)

authority_had_previous = destination_authority.exists()

provider_had_previous = {
    name: destination_providers[name].exists()
    for name in EXPECTED_PROVIDERS
}

authority_published = False
providers_published = []

try:
    if authority_had_previous:
        destination_authority.rename(backup_authority)

    stage_authority.rename(destination_authority)
    authority_published = True

    for provider_name in sorted(EXPECTED_PROVIDERS):
        destination_provider = destination_providers[provider_name]
        staged_provider = stage_bin / provider_name
        backup_provider = backup_bin / provider_name

        if provider_had_previous[provider_name]:
            destination_provider.rename(backup_provider)

        staged_provider.rename(destination_provider)
        providers_published.append(provider_name)

except Exception as exc:
    rollback_failures = []

    for provider_name in reversed(sorted(EXPECTED_PROVIDERS)):
        destination_provider = destination_providers[provider_name]
        backup_provider = backup_bin / provider_name

        try:
            if backup_provider.exists():
                if destination_provider.exists():
                    destination_provider.unlink()

                backup_provider.rename(destination_provider)

            elif (
                provider_name in providers_published
                and not provider_had_previous[provider_name]
                and destination_provider.exists()
            ):
                destination_provider.unlink()

        except Exception as rollback_exc:
            rollback_failures.append(
                provider_name + " :: " + repr(rollback_exc)
            )

    try:
        if backup_authority.exists():
            if destination_authority.exists():
                shutil.rmtree(destination_authority)

            backup_authority.rename(destination_authority)

        elif (
            authority_published
            and not authority_had_previous
            and destination_authority.exists()
        ):
            shutil.rmtree(destination_authority)

    except Exception as rollback_exc:
        rollback_failures.append(
            "authority :: " + repr(rollback_exc)
        )

    if stage_root.exists():
        shutil.rmtree(stage_root)

    if rollback_failures:
        fail(
            "platform publication failed and rollback was incomplete :: "
            + repr(exc)
            + " :: "
            + " | ".join(rollback_failures)
            + " :: recovery material :: "
            + str(backup_root)
        )

    if backup_root.exists():
        shutil.rmtree(backup_root)

    fail(
        "platform publication failed; previous materialization restored :: "
        + repr(exc)
    )

if stage_root.exists():
    shutil.rmtree(stage_root)

for name in sorted(EXPECTED_AUTHORITY_FILES):
    source_path = source_authority / name
    destination_path = destination_authority / name

    if sha(source_path) != sha(destination_path):
        fail(
            "committed authority differs from OS source :: "
            + name
        )

for provider_name in sorted(EXPECTED_PROVIDERS):
    source_provider = source_providers[provider_name]
    destination_provider = destination_providers[provider_name]

    if sha(source_provider) != sha(destination_provider):
        fail(
            "committed platform provider differs from OS source :: "
            + provider_name
        )

if backup_root.exists():
    shutil.rmtree(backup_root)

print("GREEN :: OS platform authority and provider materialized into BUILD")

for name in sorted(EXPECTED_AUTHORITY_FILES):
    print(name + " :: " + sha(destination_authority / name))

for provider_name in sorted(EXPECTED_PROVIDERS):
    print(
        provider_name
        + " :: "
        + sha(destination_providers[provider_name])
    )
