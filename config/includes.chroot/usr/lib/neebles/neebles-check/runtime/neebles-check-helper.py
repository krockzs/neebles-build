#!/usr/bin/python3

import importlib.machinery
import json
import os
import socket
import stat
import struct
import subprocess
import sys
import time
import types
from pathlib import Path


CHECKER = Path("/usr/lib/neebles/neebles-check/runtime/neebles-check.py")

COMPONENTS = {
    "boss": Path(
        "/opt/neebles-build/boss"
    ),
    "calamares": Path(
        "/opt/neebles-build/calamares"
    ),
}

ROOTS = {
    "packages",
    "rootfs",
}

BOSS_CORPUS = Path(
    "/opt/neebles-build/boss"
)

BOSS_BACKUP = Path(
    "/opt/neebles-build/.boss.restore.backup"
)

BOSS_DISCARD = Path(
    "/opt/neebles-build/.boss.restore.discard"
)

BOSS_IDENTITY = Path(
    "/opt/neebles-build/.boss.restore.identity.json"
)

BOSS_STAGE = Path(
    "/opt/neebles-build/.boss.restore.stage"
)

BOSS_RUNTIME = Path(
    "/opt/neebles-build/.boss.restore.runtime"
)

RECOVERY_ROOTFS = Path(
    "/usr/lib/neebles/neebles-check/restore/rootfs"
)

RUNTIME_ENV = Path(
    "/etc/neebles/runtime.env"
)

SHARED_SETTINGS = Path(
    "/opt/neebles/shared/settings"
)



ACTIVE_BOSS_CLIENT = Path(
    "/opt/neebles/client"
)

ACTIVE_BOSS_SYSTEM_UNITS = (
    "neebles-external.service",
    "neebles-external.socket",
    "neebles-runtime.service",
    "neebles-stage0.service",
)

ACTIVE_BOSS_USER_UNITS = (
    "neebles-tray-sni-host.service",
    "neebles-tray-host.service",
    "neebles-tray-manager.service",
)

ACTIVE_BOSS_PATHS = (
    Path("/opt/neebles/client"),

    Path("/usr/local/bin/neebles"),

    Path(
        "/usr/share/icons/hicolor/256x256/apps/"
        "neebles-boss-launcher-icon.png"
    ),
    Path(
        "/usr/share/icons/hicolor/256x256/apps/"
        "neebles-boss-icon.png"
    ),
    Path(
        "/usr/share/icons/hicolor/256x256/apps/"
        "neebles-boss-tray-icon.png"
    ),
    Path(
        "/usr/share/icons/hicolor/256x256/apps/"
        "neebles-installer-icon.png"
    ),

    Path(
        "/usr/share/applications/"
        "org.neebles.Boss.desktop"
    ),
    Path(
        "/usr/share/applications/"
        "org.neebles.Installer.desktop"
    ),

    Path(
        "/usr/lib/systemd/user/"
        "neebles-tray-manager.service"
    ),
    Path(
        "/usr/lib/systemd/user/"
        "neebles-tray-host.service"
    ),
    Path(
        "/usr/lib/systemd/user/"
        "neebles-tray-sni-host.service"
    ),

    Path(
        "/usr/lib/systemd/system/"
        "neebles-runtime.service"
    ),
    Path(
        "/usr/lib/systemd/system/"
        "neebles-external.socket"
    ),
    Path(
        "/usr/lib/systemd/system/"
        "neebles-external.service"
    ),

    # Historical Boss-owned Stage0 residue.
    Path(
        "/usr/lib/systemd/system/"
        "neebles-stage0.service"
    ),

    Path(
        "/etc/systemd/system/"
        "multi-user.target.wants/"
        "neebles-runtime.service"
    ),
    Path(
        "/etc/systemd/system/"
        "multi-user.target.wants/"
        "neebles-stage0.service"
    ),
    Path(
        "/etc/systemd/system/"
        "sockets.target.wants/"
        "neebles-external.socket"
    ),

    # Historical user-unit enablement residue.
    Path(
        "/etc/systemd/user/"
        "default.target.wants/"
        "neebles-tray-manager.service"
    ),
    Path(
        "/etc/systemd/user/"
        "default.target.wants/"
        "neebles-tray-host.service"
    ),
    Path(
        "/etc/systemd/user/"
        "default.target.wants/"
        "neebles-tray-sni-host.service"
    ),

    # Historical XDG tray-host residue.
    Path(
        "/etc/xdg/autostart/"
        "neebles-tray-host.desktop"
    ),

    Path(
        "/etc/neebles/runtime.env"
    ),
    Path(
        "/etc/systemd/system/"
        "neebles-external.socket.d"
    ),

    Path(
        "/usr/share/plasma/plasmoids/"
        "org.neebles.launcher"
    ),
    Path(
        "/usr/share/plasma/plasmoids/"
        "org.neebles.spacer"
    ),

    Path(
        "/usr/lib/x86_64-linux-gnu/"
        "qt6/qml/NEEBLES/BossEvents"
    ),
)

PRESERVED_NEEBLES_PATHS = (
    Path("/opt/neebles/modules"),
    Path("/opt/neebles/shared"),
    Path("/opt/neebles/shared/settings"),
)


CUSTOM_REPOSITORY = (
    "https://github.com/krockzs/neebles-custom.git"
)



def peer_credentials():
    descriptor = sys.stdin.fileno()

    peer_socket = socket.fromfd(
        descriptor,
        socket.AF_UNIX,
        socket.SOCK_STREAM,
    )

    try:
        size = struct.calcsize(
            "3i"
        )

        raw = peer_socket.getsockopt(
            socket.SOL_SOCKET,
            socket.SO_PEERCRED,
            size,
        )
    finally:
        peer_socket.close()

    pid, uid, gid = struct.unpack(
        "3i",
        raw,
    )

    if (
        pid <= 0
        or uid < 0
        or gid < 0
    ):
        raise RuntimeError(
            "invalid peer credentials"
        )

    return {
        "pid": pid,
        "uid": uid,
        "gid": gid,
    }


def read_runtime_identity():
    try:
        metadata = RUNTIME_ENV.lstat()
    except FileNotFoundError:
        return None

    if stat.S_ISLNK(
        metadata.st_mode
    ):
        raise RuntimeError(
            "runtime identity file is a symlink"
        )

    if not stat.S_ISREG(
        metadata.st_mode
    ):
        raise RuntimeError(
            "runtime identity file is not regular"
        )

    values = {}

    for raw in RUNTIME_ENV.read_text(
        encoding="utf-8"
    ).splitlines():
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split(
            "=",
            1,
        )

        if key in {
            "NEEBLES_DESKTOP_UID",
            "NEEBLES_DESKTOP_GID",
        }:
            values[key] = value.strip()

    uid = values.get(
        "NEEBLES_DESKTOP_UID"
    )

    gid = values.get(
        "NEEBLES_DESKTOP_GID"
    )

    if uid is None and gid is None:
        return None

    if (
        uid is None
        or gid is None
        or not uid.isdigit()
        or not gid.isdigit()
    ):
        raise RuntimeError(
            "invalid runtime desktop identity"
        )

    return {
        "uid": int(uid),
        "gid": int(gid),
        "source": "runtime_env",
    }


def read_settings_identity():
    try:
        metadata = SHARED_SETTINGS.lstat()
    except FileNotFoundError:
        return None

    if stat.S_ISLNK(
        metadata.st_mode
    ):
        raise RuntimeError(
            "shared settings path is a symlink"
        )

    if not stat.S_ISDIR(
        metadata.st_mode
    ):
        raise RuntimeError(
            "shared settings path is not directory"
        )

    return {
        "uid": metadata.st_uid,
        "gid": metadata.st_gid,
        "source": "shared_settings",
    }


def authorize_restore_peer():
    peer = peer_credentials()

    runtime_identity = (
        read_runtime_identity()
    )

    settings_identity = (
        read_settings_identity()
    )

    identities = [
        identity
        for identity in (
            runtime_identity,
            settings_identity,
        )
        if identity is not None
    ]

    if not identities:
        raise PermissionError(
            "desktop identity unavailable"
        )

    expected_uid = identities[0]["uid"]
    expected_gid = identities[0]["gid"]

    for identity in identities[1:]:
        if (
            identity["uid"] != expected_uid
            or identity["gid"] != expected_gid
        ):
            raise PermissionError(
                "desktop identity sources disagree"
            )

    if (
        peer["uid"] != 0
        and (
            peer["uid"] != expected_uid
            or peer["gid"] != expected_gid
        )
    ):
        raise PermissionError(
            "peer is not authorized desktop identity"
        )

    return {
        "peer": peer,
        "desktop": {
            "uid": expected_uid,
            "gid": expected_gid,
            "source": "+".join(
                identity["source"]
                for identity in identities
            ),
        },
        "authority": (
            "root"
            if peer["uid"] == 0
            else "desktop"
        ),
    }


def load_checker():
    loader = importlib.machinery.SourceFileLoader(
        "neebles_check_runtime",
        str(CHECKER),
    )

    module = types.ModuleType(
        loader.name
    )

    loader.exec_module(
        module
    )

    return module


def inventory(module, component):
    root = COMPONENTS[component]

    if not root.is_dir():
        return {
            "present": False,
            "inventory": {},
        }

    return {
        "present": True,
        "inventory": module.local_inventory(
            root,
            ROOTS,
        ),
    }



def path_present(path):
    return (
        path.exists()
        or path.is_symlink()
    )


def run_recovery_tool(
    module,
    name,
    *arguments,
):
    tool = module.resolve_recovery_tool(
        name
    )

    command = [
        tool["path"],
    ]

    if tool["applet"] is not None:
        command.append(
            tool["applet"]
        )

    command.extend(
        str(argument)
        for argument in arguments
    )

    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if completed.returncode != 0:
        message = completed.stderr.strip()

        if not message:
            message = (
                "recovery tool failed: "
                + name
            )

        raise RuntimeError(
            message
        )

    return tool["provider"]



def run_recovery_systemctl(
    module,
    *arguments,
    uid=None,
    gid=None,
):
    tool = module.resolve_recovery_systemctl()

    environment = os.environ.copy()

    command = []

    if tool["provider"] == "private":
        environment["LD_LIBRARY_PATH"] = (
            ":".join(
                tool["library_paths"]
            )
        )

        environment["SYSTEMD_PAGER"] = "cat"

        command.extend(
            [
                tool["loader"],
                tool["path"],
            ]
        )
    else:
        command.append(
            tool["path"]
        )

        environment["SYSTEMD_PAGER"] = "cat"

    if uid is not None:
        if gid is None:
            raise RuntimeError(
                "desktop gid required with uid"
            )

        environment["XDG_RUNTIME_DIR"] = (
            "/run/user/"
            + str(uid)
        )

        environment[
            "DBUS_SESSION_BUS_ADDRESS"
        ] = (
            "unix:path=/run/user/"
            + str(uid)
            + "/bus"
        )

        def drop_identity():
            os.setgid(gid)
            os.setuid(uid)

        preexec_fn = drop_identity
    else:
        preexec_fn = None

    command.extend(
        str(argument)
        for argument in arguments
    )

    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
        preexec_fn=preexec_fn,
    )

    return {
        "provider": tool["provider"],
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }



def preserved_path_snapshot():
    snapshot = {}

    for path in PRESERVED_NEEBLES_PATHS:
        key = str(path)

        try:
            metadata = path.lstat()
        except FileNotFoundError:
            snapshot[key] = None
            continue

        snapshot[key] = {
            "device": metadata.st_dev,
            "inode": metadata.st_ino,
            "mode": stat.S_IFMT(
                metadata.st_mode
            ),
        }

    return snapshot


def boss_processes():
    matches = []

    own_pid = os.getpid()

    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue

        pid = int(entry.name)

        if pid in {
            1,
            own_pid,
        }:
            continue

        matched = False

        try:
            executable = os.readlink(
                entry / "exe"
            )

            if (
                executable
                == str(ACTIVE_BOSS_CLIENT)
                or executable.startswith(
                    str(ACTIVE_BOSS_CLIENT)
                    + "/"
                )
            ):
                matched = True

        except OSError:
            pass

        if not matched:
            try:
                raw = (
                    entry
                    / "cmdline"
                ).read_bytes()

                arguments = [
                    item.decode(
                        "utf-8",
                        errors="replace",
                    )
                    for item in raw.split(
                        bytes([0])
                    )
                    if item
                ]

                for argument in arguments:
                    if (
                        argument
                        == str(ACTIVE_BOSS_CLIENT)
                        or argument.startswith(
                            str(ACTIVE_BOSS_CLIENT)
                            + "/"
                        )
                    ):
                        matched = True
                        break

            except OSError:
                pass

        if matched:
            matches.append(pid)

    return sorted(
        set(matches)
    )


def terminate_boss_processes():
    initial = boss_processes()

    for pid in initial:
        try:
            os.kill(
                pid,
                15,
            )
        except ProcessLookupError:
            pass

    deadline = (
        time.monotonic()
        + 3.0
    )

    remaining = initial

    while (
        remaining
        and time.monotonic() < deadline
    ):
        time.sleep(
            0.1
        )

        current = set(
            boss_processes()
        )

        remaining = [
            pid
            for pid in remaining
            if pid in current
        ]

    for pid in remaining:
        try:
            os.kill(
                pid,
                9,
            )
        except ProcessLookupError:
            pass

    if remaining:
        time.sleep(
            0.2
        )

    survivors = boss_processes()

    if survivors:
        raise RuntimeError(
            "Boss processes survived shutdown: "
            + ",".join(
                str(pid)
                for pid in survivors
            )
        )

    return {
        "initial": initial,
        "forced": remaining,
    }


def unit_is_stopped(
    module,
    unit,
    uid=None,
    gid=None,
):
    result = run_recovery_systemctl(
        module,
        "--user",
        "is-active",
        unit,
        uid=uid,
        gid=gid,
    ) if uid is not None else run_recovery_systemctl(
        module,
        "is-active",
        unit,
    )

    state = result[
        "stdout"
    ].strip()

    return (
        state
        in {
            "inactive",
            "failed",
            "unknown",
        }
        or result["returncode"] != 0
        and not state
    )


def stop_active_boss_units(
    module,
    desktop,
):
    results = {
        "user": [],
        "system": [],
    }

    uid = desktop["uid"]
    gid = desktop["gid"]

    user_runtime = Path(
        "/run/user/"
        + str(uid)
    )

    user_bus = (
        user_runtime
        / "bus"
    )

    if (
        uid != 0
        and user_runtime.is_dir()
        and user_bus.exists()
    ):
        for unit in ACTIVE_BOSS_USER_UNITS:
            stop = run_recovery_systemctl(
                module,
                "--user",
                "stop",
                unit,
                uid=uid,
                gid=gid,
            )

            if not unit_is_stopped(
                module,
                unit,
                uid=uid,
                gid=gid,
            ):
                raise RuntimeError(
                    "user Boss unit remained active: "
                    + unit
                )

            results["user"].append(
                {
                    "unit": unit,
                    "provider": stop["provider"],
                    "returncode": stop["returncode"],
                }
            )

    for unit in ACTIVE_BOSS_SYSTEM_UNITS:
        stop = run_recovery_systemctl(
            module,
            "stop",
            unit,
        )

        check = run_recovery_systemctl(
            module,
            "is-active",
            unit,
        )

        state = check[
            "stdout"
        ].strip()

        if (
            check["returncode"] == 0
            and state == "active"
        ):
            raise RuntimeError(
                "system Boss unit remained active: "
                + unit
            )

        results["system"].append(
            {
                "unit": unit,
                "provider": stop["provider"],
                "returncode": stop["returncode"],
                "state": state,
            }
        )

    return results


def purge_active_boss(module):
    operation = "restore-purge-active-boss"

    try:
        authority = authorize_restore_peer()
    except Exception as error:
        return {
            "ok": False,
            "operation": operation,
            "error": (
                "restore_peer_unauthorized: "
                + str(error)
            ),
        }

    before = preserved_path_snapshot()

    try:
        units = stop_active_boss_units(
            module,
            authority["desktop"],
        )

        processes = (
            terminate_boss_processes()
        )

        removed = []
        providers = []

        for path in ACTIVE_BOSS_PATHS:
            if not path_present(path):
                continue

            provider = run_recovery_tool(
                module,
                "remove",
                "-rf",
                path,
            )

            if path_present(path):
                raise RuntimeError(
                    "Boss purge path survived: "
                    + str(path)
                )

            removed.append(
                str(path)
            )

            providers.append(
                provider
            )

        reload_system = (
            run_recovery_systemctl(
                module,
                "daemon-reload",
            )
        )

        uid = authority[
            "desktop"
        ]["uid"]

        gid = authority[
            "desktop"
        ]["gid"]

        user_runtime = Path(
            "/run/user/"
            + str(uid)
        )

        user_bus = (
            user_runtime
            / "bus"
        )

        reload_user = None

        if (
            uid != 0
            and user_runtime.is_dir()
            and user_bus.exists()
        ):
            reload_user = (
                run_recovery_systemctl(
                    module,
                    "--user",
                    "daemon-reload",
                    uid=uid,
                    gid=gid,
                )
            )

        after = preserved_path_snapshot()

        if after != before:
            raise RuntimeError(
                "preserved N.E.E.B.L.E.S. state changed during Boss purge"
            )

        if path_present(
            ACTIVE_BOSS_CLIENT
        ):
            raise RuntimeError(
                "active Boss client survived purge"
            )

    except Exception as error:
        return {
            "ok": False,
            "operation": operation,
            "error": (
                "active_boss_purge_failed: "
                + str(error)
            ),
        }

    return {
        "ok": True,
        "operation": operation,
        "authority": authority,
        "units": units,
        "processes": processes,
        "removed": removed,
        "providers": sorted(
            set(providers)
        ),
        "systemctl_provider": (
            reload_system[
                "provider"
            ]
        ),
        "user_reload_provider": (
            None
            if reload_user is None
            else reload_user[
                "provider"
            ]
        ),
        "preserved": True,
    }


def backup_boss(module):
    if not BOSS_CORPUS.is_dir():
        return {
            "ok": False,
            "operation": "restore-backup-boss",
            "error": "corpus_missing",
        }

    if path_present(BOSS_BACKUP):
        return {
            "ok": False,
            "operation": "restore-backup-boss",
            "error": "backup_exists",
        }

    provider = run_recovery_tool(
        module,
        "copy",
        "-a",
        BOSS_CORPUS,
        BOSS_BACKUP,
    )

    if not BOSS_BACKUP.is_dir():
        return {
            "ok": False,
            "operation": "restore-backup-boss",
            "error": "backup_missing_after_copy",
        }

    source_inventory = module.local_inventory(
        BOSS_CORPUS,
        ROOTS,
    )

    backup_inventory = module.local_inventory(
        BOSS_BACKUP,
        ROOTS,
    )

    if source_inventory != backup_inventory:
        run_recovery_tool(
            module,
            "remove",
            "-rf",
            BOSS_BACKUP,
        )

        return {
            "ok": False,
            "operation": "restore-backup-boss",
            "error": "backup_verification_failed",
        }

    return {
        "ok": True,
        "operation": "restore-backup-boss",
        "provider": provider,
    }


def rollback_boss(module):
    if not BOSS_BACKUP.is_dir():
        return {
            "ok": False,
            "operation": "restore-rollback-boss",
            "error": "backup_missing",
        }

    if path_present(BOSS_DISCARD):
        return {
            "ok": False,
            "operation": "restore-rollback-boss",
            "error": "discard_exists",
        }

    expected_inventory = module.local_inventory(
        BOSS_BACKUP,
        ROOTS,
    )

    displaced = False

    try:
        if path_present(BOSS_CORPUS):
            run_recovery_tool(
                module,
                "move",
                BOSS_CORPUS,
                BOSS_DISCARD,
            )
            displaced = True

        provider = run_recovery_tool(
            module,
            "move",
            BOSS_BACKUP,
            BOSS_CORPUS,
        )

        restored_inventory = module.local_inventory(
            BOSS_CORPUS,
            ROOTS,
        )

        if restored_inventory != expected_inventory:
            raise RuntimeError(
                "rollback verification failed"
            )

    except Exception:
        if path_present(BOSS_CORPUS):
            run_recovery_tool(
                module,
                "remove",
                "-rf",
                BOSS_CORPUS,
            )

        if displaced and path_present(BOSS_DISCARD):
            run_recovery_tool(
                module,
                "move",
                BOSS_DISCARD,
                BOSS_CORPUS,
            )

        raise

    if path_present(BOSS_DISCARD):
        run_recovery_tool(
            module,
            "remove",
            "-rf",
            BOSS_DISCARD,
        )

    return {
        "ok": True,
        "operation": "restore-rollback-boss",
        "provider": provider,
    }


def commit_boss_backup(module):
    if not path_present(BOSS_BACKUP):
        return {
            "ok": False,
            "operation": "restore-commit-boss",
            "error": "backup_missing",
        }

    provider = run_recovery_tool(
        module,
        "remove",
        "-rf",
        BOSS_BACKUP,
    )

    if path_present(BOSS_BACKUP):
        return {
            "ok": False,
            "operation": "restore-commit-boss",
            "error": "backup_remove_failed",
        }

    return {
        "ok": True,
        "operation": "restore-commit-boss",
        "provider": provider,
    }



def publish_boss_stage(module):
    operation = "restore-publish-boss"

    if not BOSS_STAGE.is_dir():
        return {
            "ok": False,
            "operation": operation,
            "error": "stage_missing",
        }

    corpus_present = path_present(
        BOSS_CORPUS
    )

    if corpus_present and not BOSS_CORPUS.is_dir():
        return {
            "ok": False,
            "operation": operation,
            "error": "corpus_not_directory",
        }

    if corpus_present and not BOSS_BACKUP.is_dir():
        return {
            "ok": False,
            "operation": operation,
            "error": "backup_required",
        }

    if path_present(BOSS_DISCARD):
        return {
            "ok": False,
            "operation": operation,
            "error": "discard_exists",
        }

    expected_inventory = module.local_inventory(
        BOSS_STAGE,
        ROOTS,
    )

    displaced = False
    published = False
    providers = []

    try:
        if corpus_present:
            providers.append(
                run_recovery_tool(
                    module,
                    "move",
                    BOSS_CORPUS,
                    BOSS_DISCARD,
                )
            )

            displaced = True

        providers.append(
            run_recovery_tool(
                module,
                "move",
                BOSS_STAGE,
                BOSS_CORPUS,
            )
        )

        published = True

        actual_inventory = module.local_inventory(
            BOSS_CORPUS,
            ROOTS,
        )

        if actual_inventory != expected_inventory:
            raise RuntimeError(
                "published corpus verification failed"
            )

    except Exception:
        if published and path_present(
            BOSS_CORPUS
        ):
            run_recovery_tool(
                module,
                "remove",
                "-rf",
                BOSS_CORPUS,
            )

        if displaced and path_present(
            BOSS_DISCARD
        ):
            run_recovery_tool(
                module,
                "move",
                BOSS_DISCARD,
                BOSS_CORPUS,
            )

        raise

    if path_present(BOSS_DISCARD):
        providers.append(
            run_recovery_tool(
                module,
                "remove",
                "-rf",
                BOSS_DISCARD,
            )
        )

    return {
        "ok": True,
        "operation": operation,
        "providers": providers,
        "replaced_existing": corpus_present,
    }


def remove_boss_corpus(module):
    operation = "restore-remove-boss-corpus"

    if path_present(BOSS_BACKUP):
        return {
            "ok": False,
            "operation": operation,
            "error": "backup_present",
        }

    if path_present(BOSS_DISCARD):
        return {
            "ok": False,
            "operation": operation,
            "error": "discard_present",
        }

    if not path_present(BOSS_CORPUS):
        return {
            "ok": True,
            "operation": operation,
            "changed": False,
        }

    if not BOSS_CORPUS.is_dir():
        return {
            "ok": False,
            "operation": operation,
            "error": "corpus_not_directory",
        }

    provider = run_recovery_tool(
        module,
        "remove",
        "-rf",
        BOSS_CORPUS,
    )

    if path_present(BOSS_CORPUS):
        return {
            "ok": False,
            "operation": operation,
            "error": "corpus_remove_failed",
        }

    return {
        "ok": True,
        "operation": operation,
        "changed": True,
        "provider": provider,
    }


def run_private_chroot(runtime, arguments):
    busybox = runtime / "usr/bin/busybox"

    command = [
        str(busybox),
        "chroot",
        str(runtime),
        "/usr/bin/busybox",
        "env",
        "PATH=/usr/bin:/bin",
        "HOME=/tmp",
        "GIT_PAGER=cat",
        "SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt",
    ]

    command.extend(
        arguments
    )

    completed = subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if completed.returncode != 0:
        message = completed.stderr.strip()

        if not message:
            message = completed.stdout.strip()

        if not message:
            message = "private recovery command failed"

        raise RuntimeError(
            message
        )

    return completed


def create_runtime_devices(runtime):
    dev = runtime / "dev"

    dev.mkdir(
        parents=True,
        exist_ok=True,
    )

    devices = (
        ("null", 1, 3),
        ("random", 1, 8),
        ("urandom", 1, 9),
    )

    for name, major, minor in devices:
        target = dev / name

        if path_present(target):
            raise RuntimeError(
                "runtime device already exists: "
                + str(target)
            )

        os.mknod(
            target,
            stat.S_IFCHR | 0o666,
            os.makedev(
                major,
                minor,
            ),
        )


def create_runtime_resolver(runtime):
    source = Path(
        "/etc/resolv.conf"
    )

    if not source.is_file():
        raise RuntimeError(
            "host resolver unavailable"
        )

    target = (
        runtime
        / "etc"
        / "resolv.conf"
    )

    target.write_bytes(
        source.read_bytes()
    )

    target.chmod(
        0o644
    )


def materialize_manifest_metadata(root, normalized):
    entries = normalized["entries"]

    created_directories = 0
    applied_modes = 0

    directories = [
        item
        for item in entries.values()
        if item["type"] == "dir"
    ]

    directories.sort(
        key=lambda item: (
            len(Path(item["path"]).parts),
            item["path"],
        )
    )

    for item in directories:
        target = (
            root
            / item["path"]
        )

        if target.is_symlink():
            raise RuntimeError(
                "manifest directory collides with symlink: "
                + item["path"]
            )

        if target.exists():
            if not target.is_dir():
                raise RuntimeError(
                    "manifest directory collides with non-directory: "
                    + item["path"]
                )

            continue

        parent = target.parent

        if (
            not parent.is_dir()
            or parent.is_symlink()
        ):
            raise RuntimeError(
                "unsafe or missing manifest directory parent: "
                + item["path"]
            )

        target.mkdir()
        created_directories += 1

    for path_name in sorted(entries):
        item = entries[path_name]

        if item["type"] not in {
            "file",
            "dir",
        }:
            continue

        target = (
            root
            / path_name
        )

        if target.is_symlink():
            raise RuntimeError(
                "manifest chmod target is symlink: "
                + path_name
            )

        if not target.exists():
            raise RuntimeError(
                "manifest chmod target missing: "
                + path_name
            )

        if (
            item["type"] == "file"
            and not target.is_file()
        ):
            raise RuntimeError(
                "manifest file type mismatch: "
                + path_name
            )

        if (
            item["type"] == "dir"
            and not target.is_dir()
        ):
            raise RuntimeError(
                "manifest directory type mismatch: "
                + path_name
            )

        mode = int(
            item["mode"],
            8,
        )

        os.chmod(
            target,
            mode,
        )

        applied_modes += 1

    return {
        "created_directories": created_directories,
        "applied_modes": applied_modes,
    }


def stage_boss(module, payload):

    operation = "restore-stage-boss"

    if not isinstance(payload, dict):
        return {
            "ok": False,
            "operation": operation,
            "error": "invalid_stage_payload",
        }

    slot = payload.get(
        "slot"
    )

    version = payload.get(
        "version"
    )

    digest = payload.get(
        "manifest_sha256"
    )

    branch = payload.get(
        "branch"
    )

    if slot not in {
        "current",
        "old",
    }:
        return {
            "ok": False,
            "operation": operation,
            "error": "invalid_stage_slot",
        }

    if not isinstance(version, str) or not version:
        return {
            "ok": False,
            "operation": operation,
            "error": "invalid_stage_version",
        }

    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(
            character not in "0123456789abcdefABCDEF"
            for character in digest
        )
    ):
        return {
            "ok": False,
            "operation": operation,
            "error": "invalid_stage_digest",
        }

    if (
        not isinstance(branch, str)
        or not branch
        or branch.startswith("-")
        or ".." in branch
    ):
        return {
            "ok": False,
            "operation": operation,
            "error": "invalid_stage_branch",
        }

    if path_present(BOSS_STAGE):
        return {
            "ok": False,
            "operation": operation,
            "error": "stage_exists",
        }

    if path_present(BOSS_RUNTIME):
        return {
            "ok": False,
            "operation": operation,
            "error": "runtime_exists",
        }

    if not RECOVERY_ROOTFS.is_dir():
        return {
            "ok": False,
            "operation": operation,
            "error": "private_recovery_rootfs_missing",
        }

    stage_created = False

    try:
        runtime_provider = run_recovery_tool(
            module,
            "copy",
            "-a",
            RECOVERY_ROOTFS,
            BOSS_RUNTIME,
        )

        create_runtime_devices(
            BOSS_RUNTIME
        )

        create_runtime_resolver(
            BOSS_RUNTIME
        )

        work = (
            BOSS_RUNTIME
            / "work"
        )

        work.mkdir(
            mode=0o755
        )

        run_private_chroot(
            BOSS_RUNTIME,
            [
                "GIT_LFS_SKIP_SMUDGE=1",
                "/usr/bin/git",
                "clone",
                "--branch",
                branch,
                "--single-branch",
                CUSTOM_REPOSITORY,
                "/work/neebles-custom",
            ],
        )

        repository = (
            BOSS_RUNTIME
            / "work"
            / "neebles-custom"
        )

        manifest_name = (
            "boss_current_manifest.json"
            if slot == "current"
            else "boss_old_manifest.json"
        )

        manifest_path = (
            repository
            / manifest_name
        )

        if not manifest_path.is_file():
            raise RuntimeError(
                "target Boss manifest missing"
            )

        with manifest_path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            manifest_raw = json.load(
                handle
            )

        normalized = module.validate_manifest(
            manifest_raw,
            "boss",
        )

        if normalized["version"] != version:
            raise RuntimeError(
                "target Boss version changed"
            )

        actual_digest = module.manifest_digest(
            normalized
        )

        if actual_digest != digest:
            raise RuntimeError(
                "target Boss manifest identity changed"
            )

        run_private_chroot(
            BOSS_RUNTIME,
            [
                "/usr/bin/git",
                "-C",
                "/work/neebles-custom",
                "lfs",
                "install",
                "--local",
            ],
        )

        run_private_chroot(
            BOSS_RUNTIME,
            [
                "/usr/bin/git",
                "-C",
                "/work/neebles-custom",
                "lfs",
                "pull",
            ],
        )

        run_private_chroot(
            BOSS_RUNTIME,
            [
                "/usr/bin/git",
                "-C",
                "/work/neebles-custom",
                "reset",
                "--hard",
                "HEAD",
            ],
        )

        source = (
            repository
            / "runtime"
            / "boss"
        )

        if not source.is_dir():
            raise RuntimeError(
                "Boss runtime source missing"
            )

        stage_provider = run_recovery_tool(
            module,
            "copy",
            "-a",
            source,
            BOSS_STAGE,
        )

        stage_created = True

        materialization = (
            materialize_manifest_metadata(
                BOSS_STAGE,
                normalized,
            )
        )

        comparison = module.compare_manifest(
            BOSS_STAGE,
            normalized,
        )

        if comparison.get("valid") is not True:
            raise RuntimeError(
                "staged Boss corpus failed manifest validation"
            )

        return {
            "ok": True,
            "operation": operation,
            "slot": slot,
            "version": version,
            "manifest_sha256": digest,
            "branch": branch,
            "runtime_provider": runtime_provider,
            "stage_provider": stage_provider,
            "materialization": materialization,
            "comparison": comparison,
        }

    except Exception as error:
        if stage_created and path_present(
            BOSS_STAGE
        ):
            try:
                run_recovery_tool(
                    module,
                    "remove",
                    "-rf",
                    BOSS_STAGE,
                )
            except Exception:
                pass

        return {
            "ok": False,
            "operation": operation,
            "error": str(error),
        }

    finally:
        if path_present(
            BOSS_RUNTIME
        ):
            try:
                run_recovery_tool(
                    module,
                    "remove",
                    "-rf",
                    BOSS_RUNTIME,
                )
            except Exception:
                pass


def read_boss_identity():

    operation = "restore-read-boss-identity"

    if BOSS_IDENTITY.is_symlink():
        return {
            "ok": False,
            "operation": operation,
            "error": "identity_symlink_rejected",
        }

    if not BOSS_IDENTITY.exists():
        return {
            "ok": True,
            "operation": operation,
            "identity": None,
        }

    if not BOSS_IDENTITY.is_file():
        return {
            "ok": False,
            "operation": operation,
            "error": "identity_not_regular_file",
        }

    try:
        with BOSS_IDENTITY.open(
            "r",
            encoding="utf-8",
        ) as handle:
            identity = json.load(
                handle
            )

    except Exception as error:
        return {
            "ok": False,
            "operation": operation,
            "error": (
                "identity_read_failed: "
                + str(error)
            ),
        }

    return {
        "ok": True,
        "operation": operation,
        "identity": identity,
    }


def write_boss_identity(payload):
    operation = "restore-write-boss-identity"

    if not isinstance(payload, dict):
        return {
            "ok": False,
            "operation": operation,
            "error": "invalid_identity_payload",
        }

    slot = payload.get("slot")
    version = payload.get("version")
    digest = payload.get(
        "manifest_sha256"
    )

    if slot not in {
        "current",
        "old",
    }:
        return {
            "ok": False,
            "operation": operation,
            "error": "invalid_identity_slot",
        }

    if not isinstance(version, str) or not version:
        return {
            "ok": False,
            "operation": operation,
            "error": "invalid_identity_version",
        }

    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(
            character not in "0123456789abcdefABCDEF"
            for character in digest
        )
    ):
        return {
            "ok": False,
            "operation": operation,
            "error": "invalid_identity_digest",
        }

    identity = {
        "schema": 1,
        "slot": slot,
        "version": version,
        "manifest_sha256": digest,
    }

    current = read_boss_identity()

    if current.get("ok") is not True:
        return current

    if current.get("identity") == identity:
        return {
            "ok": True,
            "operation": operation,
            "identity": identity,
            "changed": False,
        }

    temporary = Path(
        str(BOSS_IDENTITY)
        + ".tmp"
    )

    if path_present(temporary):
        return {
            "ok": False,
            "operation": operation,
            "error": "identity_temporary_exists",
        }

    try:
        with temporary.open(
            "x",
            encoding="utf-8",
        ) as handle:
            json.dump(
                identity,
                handle,
                sort_keys=True,
                separators=(",", ":"),
            )
            handle.write(
                "\n"
            )

        temporary.chmod(
            0o644
        )

        temporary.replace(
            BOSS_IDENTITY
        )

    except Exception as error:
        try:
            temporary.unlink(
                missing_ok=True
            )
        except Exception:
            pass

        return {
            "ok": False,
            "operation": operation,
            "error": (
                "identity_write_failed: "
                + str(error)
            ),
        }

    return {
        "ok": True,
        "operation": operation,
        "identity": identity,
        "changed": True,
    }


MUTATING_RESTORE_OPERATIONS = {
    "restore-write-boss-identity",
    "restore-stage-boss",
    "restore-publish-boss",
    "restore-remove-boss-corpus",
    "restore-backup-boss",
    "restore-rollback-boss",
    "restore-commit-boss",
}


def authorize_mutating_restore_operation(
    operation,
):
    if operation not in MUTATING_RESTORE_OPERATIONS:
        return None

    try:
        return authorize_restore_peer()
    except Exception as error:
        raise PermissionError(
            "restore_peer_unauthorized: "
            + str(error)
        ) from error


def main():

    raw = sys.stdin.readline(
        8192
    ).strip()

    try:
        request = json.loads(
            raw
        )
    except Exception:
        request = None

    if not isinstance(request, dict):
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "invalid_request",
                },
                separators=(",", ":"),
            )
        )
        return 2

    if request.get("schema") != 1:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "unsupported_request_schema",
                },
                separators=(",", ":"),
            )
        )
        return 2

    operation = request.get(
        "operation"
    )

    payload = request.get(
        "payload"
    )

    try:
        authorize_mutating_restore_operation(
            operation
        )
    except Exception as error:
        print(
            json.dumps(
                {
                    "ok": False,
                    "operation": operation,
                    "error": str(error),
                },
                separators=(",", ":"),
            )
        )
        return 2

    if operation == "inventory":
        module = load_checker()
        if not isinstance(payload, dict):
            result = {
                "ok": False,
                "operation": operation,
                "error": "invalid_inventory_payload",
            }

        else:
            component = payload.get(
                "component"
            )

            if component not in COMPONENTS:
                result = {
                    "ok": False,
                    "operation": operation,
                    "error": "invalid_component",
                }

            else:
                data = inventory(
                    module,
                    component,
                )

                result = {
                    "ok": True,
                    "operation": operation,
                    "component": component,
                    "present": data["present"],
                    "inventory": data["inventory"],
                }

    elif operation == "restore-read-boss-identity":
        result = read_boss_identity()

    elif operation == "restore-write-boss-identity":
        result = write_boss_identity(
            payload
        )

    elif operation == "restore-stage-boss":
        module = load_checker()
        result = stage_boss(
            module,
            payload,
        )

    elif operation == "restore-publish-boss":
        module = load_checker()
        result = publish_boss_stage(
            module
        )

    elif operation == "restore-remove-boss-corpus":
        module = load_checker()
        result = remove_boss_corpus(
            module
        )

    elif operation == "restore-backup-boss":
        module = load_checker()
        result = backup_boss(
            module
        )

    elif operation == "restore-rollback-boss":
        module = load_checker()
        result = rollback_boss(
            module
        )

    elif operation == "restore-commit-boss":
        module = load_checker()
        result = commit_boss_backup(
            module
        )

    elif operation == "restore-purge-active-boss":
        module = load_checker()
        result = purge_active_boss(
            module
        )

    else:
        result = {
            "ok": False,
            "operation": operation,
            "error": "invalid_operation",
        }

    print(
        json.dumps(
            result,
            separators=(",", ":"),
        )
    )

    return 0 if result.get(
        "ok"
    ) else 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
