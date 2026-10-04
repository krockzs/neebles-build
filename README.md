# N.E.E.B.L.E.S. BUILD

**Current integration status (2026-10-04): source integration CLOSED; real Live boot and Boss 1.0.21 installation exercised; final installed-system acceptance and the next integrated release remain pending. Boss contract remains CLOSED.**

Source-side integration is complete. A real N.E.E.B.L.E.S. Live session has now been used to install and exercise Boss 1.0.21, including Launcher/Tray startup and Test Module installation. The remaining frontier is the next integrated image/release pass and final installed-system acceptance.

BUILD remains the image-side materialization and recovery layer. Point 8 did not change that ownership boundary; it hardened how canonical OS and CUSTOM material is published into the image.

N.E.E.B.L.E.S. BUILD is the materialization layer used to compose the N.E.E.B.L.E.S. OS image.

It turns certified project inputs into filesystem state consumed by the live-build process.

## Pre-LIVE closure

The current image source targets **N.E.E.B.L.E.S. OS 1.0.5**.

The customized installer runtime identifies itself as **NEEBLES-Calamares 1.0.6**.

The slideshow integration now provides:

- local slide progression independent of network availability
- immediate progression when video playback reaches end-of-media
- background synchronization of remote slide media
- optional localized TXT sidecars
- localized `es_CL` and `en_US` text
- English fallback for unsupported locales
- stable media geometry when TXT content is absent
- staging and atomic publication of synchronized material
- active-slide protection during synchronization
- offline reuse of locally available material
- domestic Qt 6.8.2 validation of `show.qml` and `show.local.qml`

Source-level integration and domestic validation are complete.

Real Live boot, Calamares execution, installation and installed-system behavior remain intentionally unclaimed until LIVE acceptance.

## Responsibilities

- live-build configuration
- base package selection
- Calamares build integration
- materialized platform authority
- certified Boss and Calamares runtime corpora
- shared module runtime territory
- opaque materialization of domestic construction declarations
- independent recovery environment
- image-side filesystem composition

## Platform authority

Canonical platform authority belongs to N.E.E.B.L.E.S. OS.

BUILD carries its materialized copy below:

```text
config/includes.chroot/usr/lib/neebles/platform/
```

The OS-defined `neebles.domestic_workspace` authority is synchronized into the image together with the canonical AuthoritySupply.

Point 8 certified the final image-side permission contract:

```text
authority JSON descriptors  root:root 0644
platform providers          root:root 0755
```

BUILD normalizes those permissions during materialization. Source bytes remain unchanged.

This is required because Boss authenticates platform-controlled material and rejects writable authority components that would violate the platform-control boundary.

BUILD materializes authority. It does not become the semantic owner of platform authority.

Platform-authority publication is also transactional. BUILD stages the next materialized state and does not leave a partially published AuthoritySupply/provider tree when synchronization fails.

## Boss corpus

N.E.E.B.L.E.S. CUSTOM owns the certified domestic Boss runtime corpus.

BUILD carries the image-side materialization required by the OS build.

## CUSTOM runtime metadata materialization

CUSTOM owns the canonical integrity and effective installed metadata of the Boss and Calamares domestic corpora.

BUILD carries an image-side copy of each canonical current manifest:

```text
/opt/neebles-build/boss/current_manifest.json
/opt/neebles-build/calamares/current_manifest.json
```

The corresponding source-side material is carried under:

```text
config/includes.chroot/opt/neebles-build/boss/current_manifest.json
config/includes.chroot/opt/neebles-build/calamares/current_manifest.json
```

During image construction, BUILD applies CUSTOM-declared runtime modes generically through:

```text
/usr/lib/neebles/build/apply-custom-runtime-metadata.py
config/hooks/normal/0910-neebles-custom-runtime-metadata.hook.chroot
```

The materializer is not a second permission authority. Before applying metadata to a regular file it verifies the manifest-declared type, size and SHA256. For symlinks it verifies the declared target and does not chmod the link. Missing, changed or type-mismatched material is fatal.

The resulting law is:

```text
CUSTOM
    -> owns certified bytes, integrity and effective installed modes

BUILD
    -> carries the certified manifest
    -> verifies the material
    -> materializes the declared modes
```

This replaces the former hard-coded runtime permission list in `9999-neebles-runtime-permissions.hook.chroot`. That hook is retired because it duplicated CUSTOM metadata and could drift into a second permission truth.

`0900-neebles-build-territory.hook.chroot` remains separate. It owns only BUILD-created filesystem territory and its directory contract; it does not redefine metadata belonging to CUSTOM runtime corpora.

This distinction is required because Git does not preserve the complete Unix mode semantics needed for privileged runtime files such as SUID entries. Repository transport therefore preserves the certified manifest, while BUILD reconstructs the effective runtime metadata deterministically during image materialization.

## Shared module territory

BUILD owns the image-side filesystem territory used by domestic module material:

```text
/opt/neebles-build/modules
/opt/neebles-build/modules/packages
/opt/neebles-build/modules/rootfs
```

The current directory contract is:

```text
/opt/neebles-build/modules           root:root 0755
/opt/neebles-build/modules/packages  root:root 0775
/opt/neebles-build/modules/rootfs    root:root 0755
```

This is a shared pool.

BUILD does not create a separate physical package store for every module and does not infer module technology from material placed there.

CUSTOM certifies material file metadata and integrity; BUILD governs the image-side territory.

## Domestic construction declarations

Canonical construction declarations belong to N.E.E.B.L.E.S. CUSTOM.

BUILD materializes their image-side copy under:

```text
config/includes.chroot/usr/lib/neebles/domestic/construction/
```

Materialization is performed explicitly before live-build using:

```text
scripts/sync-neebles-custom-construction.py
```

BUILD transports declaration files opaquely.

Point 8 hardened construction publication so replacement is transactional: a failed publication must not expose a partially replaced declaration tree and the previous valid material is restored when publication cannot complete.

It does not interpret construction semantics, module technology, compiler identity or package-manager identity.

The installed declaration territory follows:

```text
directory     root:root 0755
declarations  root:root 0644
```

An empty CUSTOM construction namespace is valid.

## Recovery

BUILD owns the independent `neebles-check` recovery environment.

Canonical recovery source lives below:

```text
config/includes.chroot/usr/lib/neebles/neebles-check/
```

Boss normal startup does not depend on invoking the recovery engine.

### Module certification

`neebles-check` now includes a dynamic module mode:

```text
neebles-check --module <module_id>
```

Modules are not a third static checker component.

The checker resolves dynamic authority from CUSTOM:

```text
runtime/manifests/modules/<module_id>.packages.tsv
runtime/manifests/modules/<module_id>.manifest.json
```

The package selector and integrity manifest are fetched from the same remote revision/branch.

The checker verifies:

- safe dynamic module identity
- exact required DEB membership
- TSV SHA256 vs integrity-manifest SHA256 agreement
- required material type
- mode
- size
- SHA256
- symlink target
- missing required material
- changed required material

The observed shared pool is fixed to:

```text
/opt/neebles-build/modules
```

The privileged helper cannot accept a caller-selected module root.

Only paths required by the requested module are inventoried. Unrelated shared material is ignored.

A module cannot claim ownership of the shared `packages` or `rootfs` roots themselves.

Path traversal, absolute selected paths and symlink-ancestor escape are rejected.

## Point 7 / Point 8 boundary

Point 7 established the ownership split and Point 8 globally recertified it:

```text
CUSTOM  -> certified material, membership, integrity, construction semantics
OS      -> platform authority semantics
BUILD   -> image-side materialization and independent recovery
Boss    -> generic governed consumption and execution
```

Point 8 confirmed that BUILD remains byte/semantic opaque for consumer construction declarations and does not become a second authority, Lifecycle, Registry or module-technology engine.

The final Point 8 BUILD corrections were local hardening only:

- materialize the current `neebles.domestic_workspace` authority into the image-side AuthoritySupply;
- make CUSTOM construction publication transactional;
- make OS platform-authority publication transactional;
- normalize platform authority JSON descriptors to `root:root 0644`;
- preserve platform providers as `root:root 0755`;
- preserve byte identity while normalizing filesystem permissions.

Final pre-VM certification included:

```text
BUILD Python syntax                         GREEN
disposable CUSTOM publication               GREEN
disposable platform publication             GREEN
platform authority descriptor modes         0644
platform provider modes                     0755
Boss / BUILD git diff --check               GREEN
Point 8 worktree contract                   GREEN
```

Point 8 is **GREEN / CLOSED** and **BOSS CONTRACT CLOSED** is now **YES**.

This does not claim that the final N.E.E.B.L.E.S. image has already completed real machine/VM acceptance. Installed-system behavior remains for the dedicated VM phase.

Generated build products, caches and temporary workspaces are not canonical source.

---

## Operational build and media recipe

This section records the current productive build procedure.

Source/build certification and real Live acceptance are separate gates.

### Certified Boss baseline

Current certified Boss release:

- Boss version: `1.0.22`
- Boss source commit: `21923d5117a06b315dc8bcc0eb0d414c7e0b425d`
- certified CUSTOM revision: `580e5948f25cc64e44d07976699f676de7a99174`
- controlled Qt build world: `6.8.2`

Published Boss 1.0.22 SHA256:

```text
bootstrap.json  464626ed38c8f71164afad5168bc11acd06b38b6c8ca7b3ae165995a88ce5cce
boss-runtime.tar.gz  0a4fe9224dfd958f4f5865b63959ebbe1fc7e272e3c859711d7e971026776e7b
client-data.tar.gz  b6aa6d269b3911dc8f62a062237c1df6c802291a063b0644de8bd75dae5a4f06
critical-update-manifest.json  37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570
install.sh  cc7ecf920f380ec06b4cf88572e48efcfaca0770ffc7b1b70bd61e6bc8742710
neebles-auth-agent  203d581fe1f09e6eeb71758674a086c11e1fb37c2a506913d29991ec21e503c5
neebles-backend  fe4557e3d10f7107a80bc3099b8ada42336788f9f8b275b222685d45c02bff80
neebles-installer  eb27a02fa156f03315454fef3e89a709b45d1b748cf9c01ca1e67a2983ee6cf1
neebles-runtime-resolve  c14a2f31b8c37719a093a5582ce030d9d84efd1562f399f77da379d6fb5c6ae2
neebles-ui  dd5f7e204c75774722abe182418fb236d655812891718286e409e611dec35d5d
SHA256SUMS  d8683fc2cfefd86f1b77a20fe038c5f2ddcadc234ba3cea4c25b1e8a1fea7a21
```

These hashes belong specifically to the published Boss 1.0.22 release.

### How Boss is compiled against certified CUSTOM material

Boss is not compiled against an arbitrary host Qt installation.

The certified Boss release build consumes the exact CUSTOM revision declared by the release workflow.

Controlled build material:

```text
neebles-custom/qt_6.8.2
neebles-custom/runtime/boss/rootfs
neebles-custom/runtime/manifests/boss.rootfs.tsv
neebles-custom/boss_current_manifest.json
```

The certified sequence is:

```text
1. Checkout the exact Boss source revision.
2. Checkout the exact certified CUSTOM revision.
3. Load CUSTOM controlled Qt 6.8.2 material.
4. Verify the Qt package snapshot with its SHA256SUMS.
5. Install the controlled Qt 6.8.2 build material.
6. Resolve the controlled Qt6 CMake package.
7. Verify certified CUSTOM Boss runtime inputs.
8. Build the Rust release binaries.
9. Build the static musl neebles-runtime-resolve bootstrap resolver.
10. Build Boss UI.
11. Build installer UI.
12. Build authorization agent.
13. Build Plasma launcher plugin.
14. Build Qt tray host.
15. Materialize the domestic Boss runtime manifest.
16. Rehydrate manifest-declared empty runtime directories.
17. Package and certify boss-runtime.tar.gz.
18. Materialize the complete release payload.
19. Verify the complete release payload.
20. Generate SHA256SUMS.
21. Publish the versioned Boss release.
```

CUSTOM owns and certifies the controlled physical material.

Boss consumes that controlled material during its certified build.

BUILD does not become the Boss compiler authority. BUILD materializes the resulting certified product into the image.

### Boss productive house inside BUILD

The productive Boss image-side house is:

```text
/opt/neebles-build/boss
/opt/neebles-build/boss/packages
/opt/neebles-build/boss/rootfs
```

The corresponding BUILD source territory is:

```text
config/includes.chroot/opt/neebles-build/boss
config/includes.chroot/opt/neebles-build/boss/packages
config/includes.chroot/opt/neebles-build/boss/rootfs
```

CUSTOM remains owner of the certified domestic Boss corpus.

BUILD only materializes the image-side copy.

### Calamares productive house

Calamares is independent from Boss.

The productive image-side house is:

```text
/opt/neebles-build/calamares
/opt/neebles-build/calamares/packages
/opt/neebles-build/calamares/rootfs
```

The canonical certified source remains CUSTOM:

```text
neebles-custom/runtime/calamares/packages
neebles-custom/runtime/calamares/rootfs
neebles-custom/runtime/manifests/calamares.packages.tsv
neebles-custom/runtime/manifests/calamares.rootfs.tsv
neebles-custom/calamares_current_manifest.json
```

Boss and Calamares remain separate domestic runtime corpora.

### Canonical full ISO build

The normal clean N.E.E.B.L.E.S. image build recipe is:

```bash
cd ~/NEEBLES/neebles-build
sudo lb clean --chroot
sudo lb clean --binary
sudo rm -rf .build
sudo lb config
sudo env WGET_OPTIONS="--inet4-only --timeout=30 --tries=5" lb build
```

A successful live-build execution means the ISO was generated.

It does not by itself certify Live behavior.

### Identify the USB device before writing

Never assume the destination device.

Inspect connected block devices first:

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,RM,MOUNTPOINTS
```

Identify the USB drive by model, size, transport and removable flag.

Confirm again immediately before writing:

```bash
lsblk -o NAME,MODEL,SIZE,TRAN,RM,MOUNTPOINTS
```

Unmount every mounted partition belonging to that USB device before using dd.

Example only after the real device has been positively identified:

```text
sudo umount /dev/DEVICE1
sudo dd if=live-image-amd64.hybrid.iso of=/dev/DEVICE bs=4M status=progress conv=fsync
sync
```

`DEVICE` must be replaced by the real whole USB block device identified with lsblk.

Do not use a partition as the dd destination.

Do not execute dd until the destination device has been positively identified.

### Acceptance boundary

After writing the ISO, the next gate is real Live acceptance:

```text
boot ISO or USB
validate Live environment
validate Calamares runtime
validate Boss bootstrap
validate authorization-agent path
validate installation
validate permanent domestic Boss runtime
validate installed system
```

Only that real Live gate can close runtime acceptance.



## Current checkpoint — 2026-10-04

The current development checkpoint is intentionally **pre-1.0.22**. No new Boss release is being cut in this checkpoint.

Important facts for the next BUILD pass:

- Boss **1.0.21** is the currently published Boss release.
- The OS platform boundary provider was repaired after Live testing so an ordinary user no longer needs to copy the domestic rootfs `/etc` tree merely to expose files such as `/etc/resolv.conf`; the provider now uses a Bubblewrap overlay-based boundary.
- Explicit AuthoritySupply plus the repaired provider successfully reached the remote Registry and exposed Test Module in Live.
- BUILD must eventually rematerialize the updated OS provider into a fresh image; that rebuild is deliberately deferred to the next integration session.
- Boss Tray work is source-complete enough for the next release candidate: Qt Tray Host controlled build, DESTDIR install gate, domestic final ELF gate and Rust release build are GREEN. Runtime click/dismiss behavior still requires real Plasma acceptance.
- The existing Launcher build/install/certification order is a protected integration path and must not be casually reordered.
- `neebles-build` operations continue to require root authority during image construction.

No statement in this checkpoint claims that Boss 1.0.22, a new ISO, or final Test Module certification has been published.
