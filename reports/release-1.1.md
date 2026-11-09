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

- PASS: 93 unit regressions, including new manifest, early refusal, no-mutation, same-release resume and documentation tests.
- PASS: Ansible2.22.0 playbook syntax, 20 actual templates rendered for each OS (40 renders), shell syntax, Python compile.
- PASS: real local HTTPS/Ansible URI fixture retries503 and non-XML, accepts discovery XML and rejects an untrusted certificate. Initial sandbox-only RPC socket refusal was resolved by running the isolated fixture with permitted local sockets, not by disabling verification.
- PASS: all five downloaded archives pass pinned SHA256, real safe-extractor member/path/size checks and version metadata. All app file hashes match their signature manifests; signatures/certificates are present. This is not native `occ` certificate verification.
- GitHub CI: first run exposed the Ansible2.22 controller requirement Python>=3.13; Python3.12 dev job was incompatible and3.13 was cancelled by matrix fail-fast. Corrected CI to3.13/3.14 and documented the development interpreter requirement. Native target Python/Ansible profiles remain unchanged. Await rerun before release.
- NOT RUN: new clean-VPS installation/rerun/reboot, native `occ` app-signature verification, actual browser Mail/Office save/reopen, simultaneous load or restore with NC35. Artifact hash/signature-file checks do not replace `occ` cryptographic validation.

**Historical v1.0 Ubuntu/Debian live PASS is not transferred to v1.1.** This stable-source refresh is not a claim of new live deployment acceptance, a security audit, deliverability certification, automatic upgrade or completed external backup. Prepare independent backup/MFA and test on a clean VPS before real data.

## Coverage: specs/release-1.1.md

### Requirements
- [x] R1 — Official stable versions, exact artifacts/metadata and core SHA recorded in components manifest/evidence.
- [x] R2 — Native OS profiles unchanged; latest OS package candidates requested; bundled apps follow core; capacity-app metadata/version updated.
- [x] R3 — Wizard calls component_guard before preflight/SWAP/legacy-state migration/APT; mismatch/malformed metadata fail closed; same-version resume tested.
- [x] R4 — RU/EN README pins v1.1.0 and discloses missing new live acceptance; old reports explicitly historical; short notes below.
- [ ] R5 — Pending verified GitHub publication.
### Constraints
- [x] C1 — No production/deploy/private target state, proprietary fonts or history rewriting; only public source files staged explicitly.
- [x] C2 — TLS/integrity/storage/MFA guards and OS profiles preserved; app SHA strengthens downloads; artifact validation remains required before release.
- [x] C3 — Local/static/CI/live evidence explicitly separated; no inherited v1.0 live PASS.
### Edge cases
- [x] E1 — Wrong/missing/malformed versions refuse before package/service changes; absent components during identical-version interrupted install allowed.
- [ ] E2 — Await final artifact checks and CI; publication remains gated.
- [ ] E3 — Remote baseline and tag/release conflict checks required before publishing; never force/move refs.
### Definition of done
- [ ] D1 — Await artifact validation and CI; local unit/render/syntax/HTTPS fixture PASS.
- [x] D2 — Scope/limits, per-item coverage and separate verification pass recorded here; no new live claim.
- [ ] D3 — Await public tag/release verification.

## Separate review pass

Verdict: **PENDING**. Review is by the same agent in a separate verification pass, not an independent-agent audit. Final per-item review and publication evidence will be recorded before the release is announced complete.

## Short release notes / Кратко для GitHub Release

Обновлены стабильные компоненты: Nextcloud35.0.2, Mail5.13.1, Calendar6.6.5, Office12.0.1 и CODE26.4.502. Версии и SHA256 собраны в единый manifest; системные пакеты получают актуальные stable/security-версии Ubuntu24.04/Debian13. Индикатор общего диска адаптирован по метаданным к NC35, обновлены CI и RU/EN-инструкции. Добавлена защита от смешивания версий при повторном запуске.

Для новой чистой VPS; **не автоматическое обновление v1.0**. Новая серверная/браузерная приёмка NC35 не выполнялась; результаты v1.0 не переносятся на этот релиз. Перед реальными данными нужны тестовая установка, backup и MFA.
