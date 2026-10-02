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
