# N.E.E.B.L.E.S. BUILD

**Current integration status: N.E.E.B.L.E.S. OS 1.0.5 / source integration CLOSED / LIVE acceptance pending. Boss contract CLOSED.**

Source-side integration is complete. The next certification frontier is the real N.E.E.B.L.E.S. Live environment, installation flow and installed-system acceptance.

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

- Boss version: `1.0.18`
- Boss source commit: `73a21c253f7335b9c1e0947cc854b6a3188d61c6`
- certified CUSTOM revision: `4b7397700d18c65d1b0852c09494df45213f69d4`
- controlled Qt build world: `6.8.2`

Published Boss 1.0.18 SHA256:

```text
bootstrap.json  15807a27915650acd50cd444c4f6e20fb183265e3f64528e79eebd27b87d269e
boss-runtime.tar.gz  9eda9b502c33f19d6cab5cd07ee3feb60dede4f1da7427d018c5dbe69e4a4c3b
client-data.tar.gz  1b98d333545c44ed4127da544d4b14c0918ed505cc0a84685e19cb9a24127a3e
critical-update-manifest.json  37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570
install.sh  7607f63eb3cb90537b336a3e212def14a179c58ae1654ee36839a23e6c265a34
neebles-auth-agent  da272cfedf4ab0ee4054740db1d3cf742983b54327eab5f7cb63d05336573100
neebles-backend  b2ddec3359e1c7da4c9b8f116120c9a09566e2c629086877f93950cce75c0eb2
neebles-installer  17dab2e0db5fd804a90cd86db6c609a6dc5cb306010222c7fd6bd6b4f945a40b
neebles-runtime-resolve  27d5b4c380659bb120b430622914d0d8f38b4b1e997c1b279fa7924a2fa4fa26
neebles-ui  0e6c344c5fc91a98864dd1046128e4648d3a35d860c149fb2e94c1ba2820db85
SHA256SUMS  7ea7971247390e91c7fdee1f783098031b54e08654d7757619c11788e330f4ce
```

These hashes belong specifically to the published Boss 1.0.18 release.

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

