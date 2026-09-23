#!/usr/bin/python3

import hashlib
import json
import os
import socket
import stat
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


REPOSITORY = "krockzs/neebles-custom"

COMPONENTS = {
    "boss": {
        "local": Path("/opt/neebles-build/boss"),
        "current": "boss_current_manifest.json",
        "old": "boss_old_manifest.json",
    },
    "calamares": {
        "local": Path("/opt/neebles-build/calamares"),
        "current": "calamares_current_manifest.json",
        "old": "calamares_old_manifest.json",
    },
}

BRANCH_CANDIDATES = [
    "neebles-custom",
    "main",
    "master",
]

TIMEOUT = 12
MAX_DIFFERENCE_PATHS = 100
HELPER_SOCKET = "/run/neebles-check.sock"
HELPER_TIMEOUT = 1800

RECOVERY_ROOT = Path(
    "/usr/lib/neebles/neebles-check/restore"
)

RECOVERY_TOOLS = (
    RECOVERY_ROOT
    / "metadata"
    / "tools.json"
)

BOSS_IDENTITY = Path(
    "/opt/neebles-build/.boss.restore.identity.json"
)

BOSS_INSTALLATION = Path(
    "/opt/neebles/client"
)

NEEBLES_LAUNCHER = Path(
    "/usr/lib/neebles/neebles-launcher"
)


def load_recovery_tools():
    with RECOVERY_TOOLS.open(
        "r",
        encoding="utf-8",
    ) as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise RuntimeError(
            "invalid recovery tools manifest"
        )

    if data.get("schema") != 1:
        raise RuntimeError(
            "unsupported recovery tools schema"
        )

    artifacts = data.get("artifacts")
    tools = data.get("tools")

    if not isinstance(artifacts, dict):
        raise RuntimeError(
            "invalid recovery artifacts table"
        )

    if not isinstance(tools, dict):
        raise RuntimeError(
            "invalid recovery tools table"
        )

    return {
        "artifacts": artifacts,
        "tools": tools,
    }



def resolve_recovery_systemctl():
    with RECOVERY_TOOLS.open(
        "r",
        encoding="utf-8",
    ) as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise RuntimeError(
            "invalid recovery tools manifest"
        )

    if data.get("schema") != 1:
        raise RuntimeError(
            "unsupported recovery tools schema"
        )

    config = data.get("systemctl")

    if not isinstance(config, dict):
        raise RuntimeError(
            "missing recovery systemctl configuration"
        )

    def resolve_private_file(
        relative,
        expected_sha,
        executable=False,
    ):
        if not isinstance(relative, str):
            return None

        relative_path = Path(relative)

        if (
            relative_path.is_absolute()
            or ".." in relative_path.parts
        ):
            return None

        if (
            not isinstance(expected_sha, str)
            or len(expected_sha) != 64
            or any(
                character not in "0123456789abcdefABCDEF"
                for character in expected_sha
            )
        ):
            return None

        candidate = RECOVERY_ROOT / relative_path

        if not candidate.is_file():
            return None

        if executable and not os.access(
            candidate,
            os.X_OK,
        ):
            return None

        try:
            if (
                sha256_file(candidate)
                != expected_sha
            ):
                return None
        except OSError:
            return None

        return candidate

    private = resolve_private_file(
        config.get("path"),
        config.get("sha256"),
        executable=True,
    )

    loader_config = config.get("loader")

    loader = None

    if isinstance(loader_config, dict):
        loader = resolve_private_file(
            loader_config.get("path"),
            loader_config.get("sha256"),
            executable=True,
        )

    libraries = config.get("libraries")

    valid_libraries = True

    if not isinstance(libraries, list):
        valid_libraries = False
    else:
        for item in libraries:
            if not isinstance(item, dict):
                valid_libraries = False
                break

            if resolve_private_file(
                item.get("path"),
                item.get("sha256"),
            ) is None:
                valid_libraries = False
                break

    library_paths_raw = config.get(
        "library_paths"
    )

    library_paths = []

    if isinstance(library_paths_raw, list):
        for relative in library_paths_raw:
            if not isinstance(relative, str):
                library_paths = []
                break

            relative_path = Path(relative)

            if (
                relative_path.is_absolute()
                or ".." in relative_path.parts
            ):
                library_paths = []
                break

            candidate = (
                RECOVERY_ROOT
                / relative_path
            )

            if not candidate.is_dir():
                library_paths = []
                break

            library_paths.append(
                str(candidate)
            )

    if (
        private is not None
        and loader is not None
        and valid_libraries
        and library_paths
    ):
        return {
            "path": str(private),
            "loader": str(loader),
            "library_paths": library_paths,
            "provider": "private",
        }

    host_path = config.get("host")

    if not isinstance(host_path, str):
        raise RuntimeError(
            "invalid host systemctl path"
        )

    host = Path(host_path)

    if (
        host.is_file()
        and os.access(host, os.X_OK)
    ):
        return {
            "path": str(host),
            "loader": None,
            "library_paths": [],
            "provider": "host_fallback",
        }

    raise RuntimeError(
        "recovery systemctl unavailable"
    )


def resolve_recovery_tool(name):
    recovery = load_recovery_tools()
    tools = recovery["tools"]
    artifacts = recovery["artifacts"]

    config = tools.get(name)

    if not isinstance(config, dict):
        raise RuntimeError(
            "unknown recovery tool: " + name
        )

    artifact_name = config.get("artifact")
    applet = config.get("applet")
    host_path = config.get("host")

    if not isinstance(artifact_name, str):
        raise RuntimeError(
            "invalid recovery artifact"
        )

    if not isinstance(applet, str) or not applet:
        raise RuntimeError(
            "invalid private recovery tool applet"
        )

    if not isinstance(host_path, str):
        raise RuntimeError(
            "invalid host recovery tool path"
        )

    artifact = artifacts.get(artifact_name)

    if not isinstance(artifact, dict):
        raise RuntimeError(
            "unknown recovery artifact: " + artifact_name
        )

    private_rel = artifact.get("path")
    expected_sha = artifact.get("sha256")

    if not isinstance(private_rel, str):
        raise RuntimeError(
            "invalid private recovery artifact path"
        )

    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise RuntimeError(
            "invalid private recovery artifact sha256"
        )

    private_path = RECOVERY_ROOT / private_rel

    if (
        private_path.is_file()
        and os.access(private_path, os.X_OK)
    ):
        try:
            valid_private = (
                sha256_file(private_path)
                == expected_sha
            )
        except OSError:
            valid_private = False

        if valid_private:
            return {
                "path": str(private_path),
                "applet": applet,
                "provider": "private",
            }

    host = Path(host_path)

    if (
        host.is_file()
        and os.access(host, os.X_OK)
    ):
        return {
            "path": str(host),
            "applet": None,
            "provider": "host_fallback",
        }

    raise RuntimeError(
        "recovery tool unavailable: " + name
    )


def helper_request(operation, payload=None):
    request = {
        "schema": 1,
        "operation": operation,
    }

    if payload is not None:
        request["payload"] = payload

    try:
        with socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM,
        ) as client:
            client.settimeout(
                HELPER_TIMEOUT
            )

            client.connect(
                HELPER_SOCKET
            )

            client.sendall(
                (
                    json.dumps(
                        request,
                        separators=(",", ":"),
                    )
                    + "\n"
                ).encode(
                    "utf-8"
                )
            )

            chunks = []

            while True:
                chunk = client.recv(
                    1024 * 1024
                )

                if not chunk:
                    break

                chunks.append(
                    chunk
                )

    except OSError as error:
        raise PermissionError(
            "privileged helper unavailable: "
            + str(error)
        ) from error

    try:
        response = json.loads(
            b"".join(
                chunks
            ).decode(
                "utf-8"
            )
        )

    except Exception as error:
        raise PermissionError(
            "invalid privileged helper response: "
            + str(error)
        ) from error

    if response.get("ok") is not True:
        raise PermissionError(
            response.get(
                "error",
                "privileged helper rejected request",
            )
        )

    if response.get("operation") != operation:
        raise PermissionError(
            "privileged helper operation mismatch"
        )

    return response


def manifest_digest(normalized):
    encoded = json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode(
        "utf-8"
    )

    return hashlib.sha256(
        encoded
    ).hexdigest()


def record_boss_identity(slot, normalized):
    response = helper_request(
        "restore-write-boss-identity",
        {
            "slot": slot,
            "version": normalized["version"],
            "manifest_sha256": manifest_digest(
                normalized
            ),
        },
    )

    return response.get(
        "identity"
    )


def read_boss_identity():
    response = helper_request(
        "restore-read-boss-identity"
    )

    identity = response.get(
        "identity"
    )

    if identity is None:
        return None

    if not isinstance(identity, dict):
        raise RuntimeError(
            "invalid Boss restore identity"
        )

    if identity.get("schema") != 1:
        raise RuntimeError(
            "unsupported Boss restore identity schema"
        )

    if identity.get("slot") not in {
        "current",
        "old",
    }:
        raise RuntimeError(
            "invalid Boss restore identity slot"
        )

    version = identity.get(
        "version"
    )

    digest = identity.get(
        "manifest_sha256"
    )

    if not isinstance(version, str) or not version:
        raise RuntimeError(
            "invalid Boss restore identity version"
        )

    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(
            character not in "0123456789abcdefABCDEF"
            for character in digest
        )
    ):
        raise RuntimeError(
            "invalid Boss restore identity digest"
        )

    return identity


def sha256_file(path):


    digest = hashlib.sha256()

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def entry_type(path):
    mode = path.lstat().st_mode

    if stat.S_ISREG(mode):
        return "file"

    if stat.S_ISDIR(mode):
        return "dir"

    if stat.S_ISLNK(mode):
        return "symlink"

    return "other"


def fetch_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "NEEBLES-Check/1.0",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=TIMEOUT,
    ) as response:
        payload = response.read()

    return json.loads(
        payload.decode("utf-8")
    )


def detect_default_branch():
    url = (
        "https://api.github.com/repos/"
        + REPOSITORY
    )

    try:
        data = fetch_json(url)
    except Exception:
        return None

    branch = data.get("default_branch")

    if isinstance(branch, str) and branch:
        return branch

    return None


def raw_url(branch, filename):
    return (
        "https://raw.githubusercontent.com/"
        + REPOSITORY
        + "/"
        + branch
        + "/"
        + filename
    )


def fetch_manifest(filename):
    branches = []

    detected = detect_default_branch()

    if detected:
        branches.append(detected)

    for branch in BRANCH_CANDIDATES:
        if branch not in branches:
            branches.append(branch)

    last_error = None

    for branch in branches:
        try:
            data = fetch_json(
                raw_url(
                    branch,
                    filename,
                )
            )

            return {
                "branch": branch,
                "manifest": data,
            }

        except Exception as error:
            last_error = str(error)

    raise RuntimeError(
        last_error
        or "remote manifest unavailable"
    )


def validate_manifest(manifest, component):
    if not isinstance(manifest, dict):
        raise ValueError("manifest is not an object")

    if manifest.get("component") != component:
        raise ValueError("component mismatch")

    version = manifest.get("version")

    if not isinstance(version, str) or not version:
        raise ValueError("invalid version")

    entries = manifest.get("entries")

    if not isinstance(entries, list):
        raise ValueError("entries is not a list")

    normalized = {}

    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("invalid entry")

        path = item.get("path")
        kind = item.get("type")
        mode = item.get("mode")

        if not isinstance(path, str) or not path:
            raise ValueError("invalid entry path")

        if path.startswith("/"):
            raise ValueError("absolute manifest path")

        parts = Path(path).parts

        if ".." in parts:
            raise ValueError("parent traversal in manifest")

        if kind not in {
            "file",
            "dir",
            "symlink",
            "other",
        }:
            raise ValueError("invalid entry type")

        if not isinstance(mode, str):
            raise ValueError("invalid entry mode")

        if path in normalized:
            raise ValueError("duplicate manifest path")

        normalized[path] = item

    return {
        "version": version,
        "entries": normalized,
    }


def contract_roots(entries):
    roots = set()

    for path in entries:
        parts = Path(path).parts

        if parts:
            roots.add(parts[0])

    return roots


def local_inventory(root, roots):
    result = {}

    if not root.is_dir():
        return result

    for base, dirs, files in os.walk(
        root,
        followlinks=False,
    ):
        base_path = Path(base)

        for name in sorted(
            list(dirs) + list(files)
        ):
            path = base_path / name
            rel = path.relative_to(root).as_posix()
            parts = Path(rel).parts

            if not parts:
                continue

            if parts[0] not in roots:
                continue

            kind = entry_type(path)

            item = {
                "path": rel,
                "type": kind,
                "mode": oct(
                    stat.S_IMODE(
                        path.lstat().st_mode
                    )
                ),
            }

            if kind == "file":
                item["size"] = path.lstat().st_size
                item["sha256"] = sha256_file(path)

            elif kind == "symlink":
                item["target"] = os.readlink(path)

            result[rel] = item

    return result


def privileged_inventory(local_root):
    component = None

    for name, config in COMPONENTS.items():
        if Path(config["local"]) == Path(local_root):
            component = name
            break

    if component is None:
        raise PermissionError(
            "privileged helper does not allow this path"
        )

    response = helper_request(
        "inventory",
        {
            "component": component,
        },
    )

    inventory = response.get(
        "inventory"
    )

    if not isinstance(
        inventory,
        dict,
    ):
        raise PermissionError(
            "privileged helper returned invalid inventory"
        )

    return inventory

def compare_manifest(local_root, normalized):
    expected = normalized["entries"]
    roots = contract_roots(expected)

    try:
        actual = local_inventory(
            local_root,
            roots,
        )

    except PermissionError:
        actual = privileged_inventory(
            local_root
        )

    expected_paths = set(expected)
    actual_paths = set(actual)

    missing = sorted(
        expected_paths - actual_paths
    )

    extra = sorted(
        actual_paths - expected_paths
    )

    different = []

    for path in sorted(
        expected_paths & actual_paths
    ):
        if expected[path] != actual[path]:
            different.append(path)

    valid = (
        not missing
        and not extra
        and not different
    )

    return {
        "valid": valid,
        "expected_entries": len(expected),
        "local_entries": len(actual),
        "missing_count": len(missing),
        "extra_count": len(extra),
        "different_count": len(different),
        "missing": missing[:MAX_DIFFERENCE_PATHS],
        "extra": extra[:MAX_DIFFERENCE_PATHS],
        "different": different[:MAX_DIFFERENCE_PATHS],
        "difference_output_truncated": (
            len(missing) > MAX_DIFFERENCE_PATHS
            or len(extra) > MAX_DIFFERENCE_PATHS
            or len(different) > MAX_DIFFERENCE_PATHS

        ),
    }


def check_component(component):
    config = COMPONENTS[component]
    local_root = config["local"]

    result = {
        "component": component,
        "local_path": str(local_root),
        "local_present": local_root.is_dir(),
        "remote_verified": False,
        "valid": None,
        "status": None,
        "matched_version": None,
        "current_version": None,
        "old_version": None,
        "update_available": None,
        "remote_branch": None,
    }

    try:
        current_remote = fetch_manifest(
            config["current"]
        )

        old_remote = fetch_manifest(
            config["old"]
        )

    except Exception as error:
        result["status"] = (
            "unverified_remote_unavailable"
        )
        result["remote_error"] = str(error)
        return result

    try:
        current = validate_manifest(
            current_remote["manifest"],
            component,
        )

        old = validate_manifest(
            old_remote["manifest"],
            component,
        )

    except Exception as error:
        result["valid"] = None
        result["status"] = "remote_manifest_invalid"
        result["remote_error"] = str(error)
        return result

    result["remote_verified"] = True
    result["remote_branch"] = current_remote["branch"]
    result["current_version"] = current["version"]
    result["old_version"] = old["version"]

    if not local_root.is_dir():
        result["valid"] = False
        result["status"] = "local_missing"
        return result

    try:
        current_compare = compare_manifest(
            local_root,
            current,
        )

    except PermissionError as error:
        result["valid"] = None
        result["status"] = "permission_denied_requires_root"
        result["local_error"] = str(error)
        return result

    if current_compare["valid"]:
        result["valid"] = True
        result["status"] = "current"
        result["matched_version"] = current["version"]
        result["matched_slot"] = "current"
        result["update_available"] = False
        result["comparison"] = current_compare

        if component == "boss":
            try:
                result["restore_identity"] = (
                    record_boss_identity(
                        "current",
                        current,
                    )
                )
            except Exception as error:
                result["restore_identity_error"] = str(
                    error
                )

        return result

    try:
        old_compare = compare_manifest(
            local_root,
            old,
        )

    except PermissionError as error:
        result["valid"] = None
        result["status"] = "permission_denied_requires_root"
        result["local_error"] = str(error)
        return result

    if old_compare["valid"]:
        result["valid"] = True
        result["status"] = "old"
        result["matched_version"] = old["version"]
        result["matched_slot"] = "old"
        result["update_available"] = (
            old["version"] != current["version"]
        )
        result["comparison"] = old_compare

        if component == "boss":
            try:
                result["restore_identity"] = (
                    record_boss_identity(
                        "old",
                        old,
                    )
                )
            except Exception as error:
                result["restore_identity_error"] = str(
                    error
                )

        return result

    result["valid"] = False
    result["status"] = "mismatch"
    result["update_available"] = None
    result["comparison"] = {
        "current": current_compare,
        "old": old_compare,
    }

    return result


def overall_status(results):
    statuses = [
        item["status"]
        for item in results
    ]

    if any(
        item["valid"] is False
        for item in results
    ):
        return "invalid"

    if all(
        item["valid"] is True
        for item in results
    ):
        return "valid"

    if all(
        status == "unverified_remote_unavailable"
        for status in statuses
    ):
        return "unverified_remote_unavailable"

    if any(
        status == "permission_denied_requires_root"
        for status in statuses
    ):
        return "permission_denied_requires_root"

    return "partially_unverified"


def exit_code(results):
    if any(
        item["valid"] is False
        for item in results
    ):
        return 1

    if any(
        item["status"] == "permission_denied_requires_root"
        for item in results
    ):
        return 2

    return 0


def resolve_boss_restore_target(identity):
    slot = identity["slot"]

    config = COMPONENTS["boss"]

    manifest_name = (
        config["current"]
        if slot == "current"
        else config["old"]
    )

    remote = fetch_manifest(
        manifest_name
    )

    normalized = validate_manifest(
        remote["manifest"],
        "boss",
    )

    if normalized["version"] != identity["version"]:
        raise RuntimeError(
            "Boss restore identity version no longer matches remote authority"
        )

    digest = manifest_digest(
        normalized
    )

    if digest != identity["manifest_sha256"]:
        raise RuntimeError(
            "Boss restore identity digest no longer matches remote authority"
        )

    return {
        "slot": slot,
        "version": normalized["version"],
        "manifest_sha256": digest,
        "branch": remote["branch"],
        "normalized": normalized,
    }


def launch_boss_reinstall():
    if not NEEBLES_LAUNCHER.is_file():
        raise RuntimeError(
            "NEEBLES launcher is missing"
        )

    if not os.access(
        NEEBLES_LAUNCHER,
        os.X_OK,
    ):
        raise RuntimeError(
            "NEEBLES launcher is not executable"
        )

    environment = os.environ.copy()

    for name in (
        "PYTHONHOME",
        "LD_LIBRARY_PATH",
        "SSL_CERT_FILE",
    ):
        environment.pop(
            name,
            None,
        )

    process = subprocess.Popen(
        [
            str(NEEBLES_LAUNCHER),
        ],
        env=environment,
        close_fds=True,
        start_new_session=True,
    )

    return {
        "path": str(
            NEEBLES_LAUNCHER
        ),
        "pid": process.pid,
    }


def finalize_boss_restore(
    corpus_status,
    component,
    details=None,
):
    if os.geteuid() == 0:
        output = {
            "schema": "neebles-check-v1",
            "mode": "--restore",
            "overall_status": (
                "restore_requires_desktop_user"
            ),
            "corpus_status": corpus_status,
            "components": [component],
            "message": (
                "Run restore from the desktop user, "
                "not as root"
            ),
        }

        if details is not None:
            output.update(
                details
            )

        return output, 2

    try:
        purge = helper_request(
            "restore-purge-active-boss"
        )
    except Exception as error:
        output = {
            "schema": "neebles-check-v1",
            "mode": "--restore",
            "overall_status": (
                "active_boss_purge_failed"
            ),
            "corpus_status": corpus_status,
            "components": [component],
            "error": str(error),
        }

        if details is not None:
            output.update(
                details
            )

        return output, 2

    try:
        relaunch = launch_boss_reinstall()
    except Exception as error:
        output = {
            "schema": "neebles-check-v1",
            "mode": "--restore",
            "overall_status": (
                "boss_relaunch_failed"
            ),
            "corpus_status": corpus_status,
            "components": [component],
            "purge": purge,
            "error": str(error),
        }

        if details is not None:
            output.update(
                details
            )

        return output, 2

    output = {
        "schema": "neebles-check-v1",
        "mode": "--restore",
        "overall_status": (
            "boss_reinstall_started"
        ),
        "corpus_status": corpus_status,
        "components": [component],
        "purge": purge,
        "relaunch": relaunch,
    }

    if details is not None:
        output.update(
            details
        )

    return output, 0


def restore_boss():
    if not BOSS_INSTALLATION.is_dir():
        return {
            "schema": "neebles-check-v1",
            "mode": "--restore",
            "overall_status": "boss_not_installed",
            "message": "Boss aún no está instalado",
        }, 0

    initial = check_component(
        "boss"
    )

    if initial.get("valid") is True:
        return finalize_boss_restore(
            "corpus_ready",
            initial,
        )

    repairable_statuses = {
        "local_missing",
        "mismatch",
    }

    if (
        initial.get("remote_verified") is not True
        or initial.get("valid") is not False
        or initial.get("status")
        not in repairable_statuses
    ):
        return {
            "schema": "neebles-check-v1",
            "mode": "--restore",
            "overall_status": "corpus_unverified",
            "components": [initial],
        }, 2

    try:
        identity = read_boss_identity()
    except Exception as error:
        return {
            "schema": "neebles-check-v1",
            "mode": "--restore",
            "overall_status": "restore_identity_unavailable",
            "components": [initial],
            "error": str(error),
        }, 2

    if identity is None:
        return {
            "schema": "neebles-check-v1",
            "mode": "--restore",
            "overall_status": "restore_identity_missing",
            "components": [initial],
        }, 2

    try:
        target = resolve_boss_restore_target(
            identity
        )
    except Exception as error:
        return {
            "schema": "neebles-check-v1",
            "mode": "--restore",
            "overall_status": "restore_identity_mismatch",
            "components": [initial],
            "restore_identity": identity,
            "error": str(error),
        }, 2

    corpus = COMPONENTS["boss"]["local"]
    original_present = corpus.is_dir()

    if original_present:
        try:
            backup = helper_request(
                "restore-backup-boss"
            )
        except Exception as error:
            return {
                "schema": "neebles-check-v1",
                "mode": "--restore",
                "overall_status": "restore_backup_failed",
                "components": [initial],
                "restore_identity": identity,
                "error": str(error),
            }, 2
    else:
        backup = None

    attempts = []

    stage_payload = {
        "slot": target["slot"],
        "version": target["version"],
        "manifest_sha256": target[
            "manifest_sha256"
        ],
        "branch": target["branch"],
    }

    for attempt_number in range(1, 4):
        attempt = {
            "attempt": attempt_number,
        }

        try:
            attempt["stage"] = helper_request(
                "restore-stage-boss",
                stage_payload,
            )

            attempt["publish"] = helper_request(
                "restore-publish-boss"
            )

            recheck = check_component(
                "boss"
            )

            attempt["recheck"] = recheck

            if recheck.get("valid") is True:
                attempt["restore_identity"] = (
                    record_boss_identity(
                        target["slot"],
                        target["normalized"],
                    )
                )

                if original_present:
                    attempt["commit"] = helper_request(
                        "restore-commit-boss"
                    )

                attempts.append(
                    attempt
                )

                return finalize_boss_restore(
                    "corpus_repaired",
                    recheck,
                    {
                        "restore_identity": identity,
                        "target": stage_payload,
                        "backup": backup,
                        "attempts": attempts,
                    },
                )

            if not original_present:
                attempt["cleanup"] = helper_request(
                    "restore-remove-boss-corpus"
                )

        except Exception as error:
            attempt["error"] = str(error)

            if not original_present:
                try:
                    attempt["cleanup"] = helper_request(
                        "restore-remove-boss-corpus"
                    )
                except Exception as cleanup_error:
                    attempt["cleanup_error"] = str(
                        cleanup_error
                    )

        attempts.append(
            attempt
        )

    recovery = None
    recovery_error = None

    try:
        if original_present:
            recovery = helper_request(
                "restore-rollback-boss"
            )
        else:
            recovery = helper_request(
                "restore-remove-boss-corpus"
            )
    except Exception as error:
        recovery_error = str(error)

    output = {
        "schema": "neebles-check-v1",
        "mode": "--restore",
        "overall_status": "corpus_repair_failed",
        "components": [initial],
        "restore_identity": identity,
        "target": stage_payload,
        "backup": backup,
        "attempts": attempts,
        "recovery": recovery,
    }

    if recovery_error is not None:
        output["overall_status"] = (
            "corpus_repair_failed_recovery_error"
        )
        output["recovery_error"] = recovery_error
        return output, 2

    return output, 1


def usage():
    return {
        "error": "invalid_arguments",
        "usage": [
            "neebles-check --boss",
            "neebles-check --calamares",
            "neebles-check --all",
            "neebles-check --restore",
        ],
    }


def main():
    if len(sys.argv) != 2:
        print(
            json.dumps(
                usage(),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 2

    argument = sys.argv[1]

    if argument == "--boss":
        components = ["boss"]

    elif argument == "--calamares":
        components = ["calamares"]

    elif argument == "--all":
        components = [
            "boss",
            "calamares",
        ]

    elif argument == "--restore":
        output, code = restore_boss()
        print(
            json.dumps(
                output,
                indent=2,
                ensure_ascii=False,
            )
        )
        return code

    else:
        print(
            json.dumps(
                usage(),
                indent=2,
                ensure_ascii=False,
            )
        )
        return 2

    results = [
        check_component(component)
        for component in components
    ]

    output = {
        "schema": "neebles-check-v1",
        "repository": (
            "https://github.com/"
            + REPOSITORY
        ),
        "mode": argument,
        "overall_status": overall_status(results),
        "components": results,
    }

    print(
        json.dumps(
            output,
            indent=2,
            ensure_ascii=False,
        )
    )

    return exit_code(results)


if __name__ == "__main__":
    raise SystemExit(main())
