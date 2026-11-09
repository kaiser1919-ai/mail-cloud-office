# Release 1.1 — stable component refresh

Owner request: update all repository components to current stable versions and publish release 1.1 with short notes. Scope: portable source installer, not a production deployment or an in-place upgrade utility.

## Requirements
- R1: Pin the latest official stable Nextcloud Server, Mail, Calendar, richdocuments and amd64 richdocumentscode verified on 2026-11-09; no RC/beta/nightly. Record publisher URLs, compatibility constraints and core SHA256.
- R2: Retain Ubuntu 24.04/PHP 8.3 and Debian 13/PHP 8.4; system dependencies use the newest available candidates in the selected OS's signed stable/security repositories, not arbitrary upstream majors or PPAs. Include bundled LDAP/MFA apps through the updated core. Verify the local capacity app's declared compatibility and increment its version when adapting it.
- R3: Prevent silent mixing of release component versions on an existing/interrupted installation before modifying packages/services. Identical-version resume remains supported; the new release is not a v1.0 migration command.
- R4: Update RU/EN installation instructions to v1.1.0, current versions and truthful verification limits; preserve historical v1.0 acceptance evidence. Include short release notes.
- R5: Publish reviewed source to the existing GitHub main, create new v1.1.0 tag and stable release, verify exact SHA and release visibility.

## Constraints
- C1: Do not change production, deploy to VPS, use private installation state in tests, publish secrets/proprietary fonts, rewrite history or move/delete existing tags/releases.
- C2: Preserve TLS/signature/checksum validation, localhost/MFA gate, resource/storage guards, OS profiles and native architecture. Verify upstream artifact metadata rather than guessing versions/checksums.
- C3: Distinguish local/CI/static checks from fresh live acceptance. The previous v1.0 live acceptance is not proof of v1.1 runtime acceptance. A stable source release must disclose any missing live validation.

## Edge cases
- E1: Wrong/missing declared version in an existing core/app is rejected before package/service changes; absent components during a same-release interrupted install are allowed.
- E2: Missing/incompatible upstream stable artifact or failed required local/CI regression blocks publication; no unverified fallback or disabling compatibility checks.
- E3: Remote main divergence or an already-existing release/tag must not be overwritten; inspect before publishing, and compare old refs afterwards.

## Definition of done
- D1: Unit regressions, both OS template rendering, syntax, artifact checksum/metadata/signature-presence checks and GitHub CI pass; record limitations of each check.
- D2: RU/EN documentation and per-item coverage/review cover this scope; no claim of new clean-VPS/browser/reboot acceptance without actual evidence.
- D3: Public v1.1.0 tag/release points to verified main, contains short change notes, and old refs remain unchanged.

## Research and critique
Official sources checked 2026-11-09: Nextcloud changelog/install, App Store stable channels and publishers' GitHub release APIs/XML. NC35 requires PHP>=8.3,<8.6; richdocuments12 targets only NC35; Mail5.13.1 and Calendar6.6.5 target NC32–35; CODE26.4.502 targets NC30–35. Existing sentinel_pool declared NC34 only, so simply replacing downloads would fail enable. Existing creates guards skip old core/apps: a cross-release rerun would otherwise silently mix versions. Stable OS packages deliberately differ between distributions; latest upstream major is not necessarily their stable supported package.

## Plan
1. Verify official versions, release assets, metadata and SHA; save evidence.
2. Centralize component pins, refresh app compatibility, add early version guard and regressions; request stable OS package candidates.
3. Test locally and in existing CI; review actual diff separately, update documentation and evidence without inheriting old live PASS.
4. Publish a new tag/release only after checks; verify public artifacts and preserved historical refs.
