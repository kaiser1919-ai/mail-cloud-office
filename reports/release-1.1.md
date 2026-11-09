# v1.1.0 — stable component refresh

Date: 2026-11-09 (Asia/Novosibirsk). Scope: source installer; no production/VPS deployment in this task.

## Changes / Изменения

| Component | v1.0 | v1.1 |
|---|---|---|
| Nextcloud Server | 34.0.4 | **35.0.2** |
| Mail | 5.12.4 | **5.13.1** |
| Calendar | 6.6.2 | **6.6.5** |
| Office connector (richdocuments) | 11.1.2 | **12.0.1** |
| Built-in Collabora CODE app | 26.4.402 | **26.4.502** |
| Local shared-capacity app | 0.1.0 | **0.2.0**, declares NC34–35 |
| CI Ansible | 2.19 range | **2.22.0** |
| CI checkout / setup-python | v4 / v5 | **v7.0.1 / v7.1.0** |

Bundled LDAP 2.0.0, TOTP17.1.0 and backup-codes2.0.0 are supplied by the pinned core archive, not independently downloaded or forcibly downgraded. Native Postfix/Dovecot/Rspamd/OpenLDAP/MariaDB/Redis/Nginx/PHP/Certbot and dependencies select current candidates from the supported distribution's signed stable/security repositories. There is no distro upgrade or PPA: Ubuntu24.04 retains PHP8.3/Dovecot2.3; Debian13 retains PHP8.4/Dovecot2.4. Actual installed OS package revisions are recorded on the target in `state/packages.tsv`, not invented by this source-only release.

Component pins/hashes now live in `components.json`. App downloads use pinned SHA256 followed by native Nextcloud integrity verification before enable. The new read-only preflight rejects an existing core/app with a mismatched/missing/malformed declared version before package/service changes. This prevents skipped downloads from silently mixing old and new versions; it is **not** a v1.0→v1.1 migration tool. Same-release interrupted installs remain resumable.

## Primary sources and compatibility

- [Official stable Server35.0.2 / changelog](https://nextcloud.com/changelog/), [core checksum](https://download.nextcloud.com/server/releases/nextcloud-35.0.2.tar.bz2.sha256).
- [Mail stable](https://apps.nextcloud.com/apps/mail), [Calendar stable](https://apps.nextcloud.com/apps/calendar), [Office publisher release](https://github.com/nextcloud-releases/richdocuments/releases/tag/v12.0.1), [CODE stable](https://apps.nextcloud.com/apps/richdocumentscode).
- Publisher APIs, exact URLs, downloaded archive SHA256, metadata and bundled app versions: [components-1.1.json](components-1.1.json).
- Static checks against the tagged NC35/Mail API sources used by the local app/provisioner: [api-compatibility-1.1.json](api-compatibility-1.1.json). Presence of methods is not an integration test.

Server35 requires PHP>=8.3,<8.6. Mail5.13.1 and Calendar6.6.5 allow NC32–35/PHP8.1–8.5; richdocuments12.0.1 requires NC35/PHP>=8.3; CODE26.4.502 allows NC30–35. Both chosen OS PHP branches satisfy these declarations. Server GitHub `/releases/latest` points at an older maintained branch; stable selection used the official Server changelog instead.

## Verification

- Resolved CI finding: Ansible2.22 requires controller Python>=3.13; replaced the incompatible3.12 dev job with3.14 and retained3.13. Target distro Python/Ansible is unchanged.
- PASS: 93 unit regressions, including new manifest, early refusal, no-mutation, same-release resume and documentation tests.
- PASS: Ansible2.22.0 playbook syntax, 20 actual templates rendered for each OS (40 renders), shell syntax, Python compile.
- PASS: real local HTTPS/Ansible URI fixture retries503 and non-XML, accepts discovery XML and rejects an untrusted certificate. Initial sandbox-only RPC socket refusal was resolved by running the isolated fixture with permitted local sockets, not by disabling verification.
- PASS: all five downloaded archives pass pinned SHA256, real safe-extractor member/path/size checks and version metadata. All app file hashes match their signature manifests; signatures/certificates are present. This is not native `occ` certificate verification.
- PASS: [GitHub CI run 42624636538](https://github.com/kaiser1919-ai/mail-cloud-office/actions/runs/42624636538) on source `7443a18be5364e86eefb05d221173ef607135e08`: offline-contracts (3.14) SUCCESS, offline-contracts (3.13) SUCCESS, ubuntu-native SUCCESS. Final documentation-only commits do not change this tested runtime. Native Ubuntu CI exercises real distro parsers, synthetic LDAP/mail/TLS/Redis/privacy and local fixtures; it does not install or exercise the new NC35 browser stack.
- NOT RUN: new clean-VPS installation/rerun/reboot, native `occ` app-signature verification, actual browser Mail/Office save/reopen, simultaneous load or restore with NC35. Artifact hash/signature-file checks do not replace `occ` cryptographic validation.

**Historical v1.0 Ubuntu/Debian live PASS is not transferred to v1.1.** This stable-source refresh is not a claim of new live deployment acceptance, a security audit, deliverability certification, automatic upgrade or completed external backup. Prepare independent backup/MFA and test on a clean VPS before real data.

## Coverage and separate review: specs/release-1.1.md

The complete item-by-item source review below was performed by the same agent in a separate verification pass, not an independent-agent/security audit. Publication observations are recorded after tag/release creation in the local release audit; they cannot be evidence inside their own not-yet-published Git object.

- **R1: Pin the latest official stable Nextcloud Server, Mail, Calendar, richdocuments and amd64 richdocumentscode verified on 2026-11-09; no RC/beta/nightly. Record publisher URLs, compatibility constraints and core SHA256.**
  PASS — exact official stable pins and five downloaded archives checked; components.json, reports/components-1.1.json, tests/release_artifacts.py.
- **R2: Retain Ubuntu 24.04/PHP 8.3 and Debian 13/PHP 8.4; system dependencies use the newest available candidates in the selected OS's signed stable/security repositories, not arbitrary upstream majors or PPAs. Include bundled LDAP/MFA apps through the updated core. Verify the local capacity app's declared compatibility and increment its version when adapting it.**
  PASS — both profiles/render results preserved; apt state=latest with fresh signed OS indexes; target Ansible refreshed on install; bundled versions recorded; local app0.2.0 declares NC34–35.
- **R3: Prevent silent mixing of release component versions on an existing/interrupted installation before modifying packages/services. Identical-version resume remains supported; the new release is not a v1.0 migration command.**
  PASS — component_guard is called before preflight/SWAP/state migration/APT; no writes in the guard; wrong core/app, absent/malformed marker, symlink and interrupted same-version cases exercised.
- **R4: Update RU/EN installation instructions to v1.1.0, current versions and truthful verification limits; preserve historical v1.0 acceptance evidence. Include short release notes.**
  PASS — both README clone commands pin v1.1.0, version matrix refreshed, missing new live acceptance explicit; historical reports carry banners; concise notes included.
- **R5: Publish reviewed source to the existing GitHub main, create new v1.1.0 tag and stable release, verify exact SHA and release visibility.**
  IMPLEMENTED / POST-PUBLICATION CHECK REQUIRED — authorized fast-forward source publication; create new v1.1.0 tag/stable release only after successful CI; verify exact SHA and visibility in release audit.
- **C1: Do not change production, deploy to VPS, use private installation state in tests, publish secrets/proprietary fonts, rewrite history or move/delete existing tags/releases.**
  PASS — no production/VPS operations or private target state; explicit23-file staging and private-data/credential scan passed; original tags/releases recorded before publishing; no force/history rewriting.
- **C2: Preserve TLS/signature/checksum validation, localhost/MFA gate, resource/storage guards, OS profiles and native architecture. Verify upstream artifact metadata rather than guessing versions/checksums.**
  PASS — existing TLS/native integrity/MFA/resource/storage guards retained; five real archive checks and tagged API checks pass; SHA pinning added before app integrity verification.
- **C3: Distinguish local/CI/static checks from fresh live acceptance. The previous v1.0 live acceptance is not proof of v1.1 runtime acceptance. A stable source release must disclose any missing live validation.**
  PASS — source/local/static/CI/new-live limits explicit in both READMEs and this report; v1.0 live evidence remains historical.
- **E1: Wrong/missing declared version in an existing core/app is rejected before package/service changes; absent components during a same-release interrupted install are allowed.**
  PASS — read-only negative guard tests fail closed; identical-version core/app and absent not-yet-installed components pass.
- **E2: Missing/incompatible upstream stable artifact or failed required local/CI regression blocks publication; no unverified fallback or disabling compatibility checks.**
  PASS — five real official archives validated;93unit/syntax/40renders/HTTPSfixture and all CI jobs pass. No compatibility/signature/TLS guard disabled.
- **E3: Remote main divergence or an already-existing release/tag must not be overwritten; inspect before publishing, and compare old refs afterwards.**
  PRE-PUBLICATION PASS / POST-PUBLICATION CHECK REQUIRED — exact remote main matched baseline; v1.1.0 absent; old refs/releases captured; ordinary non-force push only.
- **D1: Unit regressions, both OS template rendering, syntax, artifact checksum/metadata/signature-presence checks and GitHub CI pass; record limitations of each check.**
  PASS —93unit,40render,syntax,compile,actual discovery HTTPS negative fixture, archive metadata/SHA/signed file hash checks and CI all pass; native occ cryptographic/live checks explicitly not run.
- **D2: RU/EN documentation and per-item coverage/review cover this scope; no claim of new clean-VPS/browser/reboot acceptance without actual evidence.**
  PASS — updated bilingual docs plus full exact-item review/coverage here; live acceptance not claimed.
- **D3: Public v1.1.0 tag/release points to verified main, contains short change notes, and old refs remain unchanged.**
  IMPLEMENTED / POST-PUBLICATION CHECK REQUIRED — source/runtime verified; new immutable tag/release and historical ref comparison to be checked in local release audit.

**Source verification verdict: PASS.** Overall publication completion additionally requires the post-publication checks named above. No new live-VPS acceptance verdict is issued.

## Short release notes / Кратко для GitHub Release

Обновлены стабильные компоненты: Nextcloud35.0.2, Mail5.13.1, Calendar6.6.5, Office12.0.1 и CODE26.4.502. Версии и SHA256 собраны в единый manifest; системные пакеты получают актуальные stable/security-версии Ubuntu24.04/Debian13. Индикатор общего диска адаптирован по метаданным к NC35, обновлены CI и RU/EN-инструкции. Добавлена защита от смешивания версий при повторном запуске.

Для новой чистой VPS; **не автоматическое обновление v1.0**. Новая серверная/браузерная приёмка NC35 не выполнялась; результаты v1.0 не переносятся на этот релиз. Перед реальными данными нужны тестовая установка, backup и MFA.
