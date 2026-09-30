#!/usr/bin/env python3

from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sys

EXPECTED_AUTHORITY_FILES = {
    "authority-supply.json",
    "boss.modules.install_staging.json",
    "boss.modules.update_staging.json",
    "platform.filesystem_boundary.json",
    "platform.desktop_session_interface.json",
    "system.dns_resolver_config.json",
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

EXPECTED_SUPPLY = {
    "schema": "1",
    "name": "neebles-authority-supply",
    "entries": [
        {
            "authority": "platform.filesystem_boundary",
            "location": "/usr/lib/neebles/platform/authority/platform.filesystem_boundary.json",
        },
        {
            "authority": "system.dns_resolver_config",
            "location": "/usr/lib/neebles/platform/authority/system.dns_resolver_config.json",
        },
        {
            "authority": "boss.modules.install_staging",
            "location": "/usr/lib/neebles/platform/authority/boss.modules.install_staging.json",
        },
        {
            "authority": "boss.modules.update_staging",
            "location": "/usr/lib/neebles/platform/authority/boss.modules.update_staging.json",
        },
        {
            "authority": "platform.desktop_session_interface",
            "location": "/usr/lib/neebles/platform/authority/platform.desktop_session_interface.json",
        },
    ],
}

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

destination_authority.mkdir(parents=True, exist_ok=True)
(destination_platform / "bin").mkdir(
    parents=True,
    exist_ok=True
)

for child in list(destination_authority.iterdir()):
    if child.is_file() or child.is_symlink():
        child.unlink()
    elif child.is_dir():
        shutil.rmtree(child)

for name in sorted(EXPECTED_AUTHORITY_FILES):
    shutil.copy2(source_authority / name, destination_authority / name)

for provider_name in sorted(EXPECTED_PROVIDERS):
    source_provider = source_providers[provider_name]
    destination_provider = destination_providers[provider_name]

    shutil.copy2(
        source_provider,
        destination_provider
    )

    destination_provider.chmod(0o755)

for name in sorted(EXPECTED_AUTHORITY_FILES):
    source_path = source_authority / name
    destination_path = destination_authority / name

    if sha(source_path) != sha(destination_path):
        fail("materialized authority differs from OS source :: " + name)

for provider_name in sorted(EXPECTED_PROVIDERS):
    source_provider = source_providers[provider_name]
    destination_provider = destination_providers[provider_name]

    if sha(source_provider) != sha(destination_provider):
        fail(
            "materialized platform provider differs from OS source :: "
            + provider_name
        )

print("GREEN :: OS platform authority and provider materialized into BUILD")

for name in sorted(EXPECTED_AUTHORITY_FILES):
    print(name + " :: " + sha(destination_authority / name))

for provider_name in sorted(EXPECTED_PROVIDERS):
    print(
        provider_name
        + " :: "
        + sha(destination_providers[provider_name])
    )
