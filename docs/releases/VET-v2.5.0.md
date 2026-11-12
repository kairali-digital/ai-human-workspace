# v2.5.0 verification record

## Release decision

This report records the evidence available before the final package was frozen. The detached assurance packet binds the final source tree, downloadable assets and Mac host skill to the Builder, Claude and Monitor reports and the owner's release decision. Use the Mac release only when the approved packet matches the downloaded bytes. Until then the release decision is pending.

## Mac preflight

Both the development source and its extracted installable package ran 239 test methods. Each passed all 232 applicable tests and skipped seven Windows-only methods. Six original stable releases from v2.0.0 through v2.4.0 completed 66 upgrade, rollback and return operations. Each case preserved 25 baseline worker files. The held v2.0.1 release was excluded.

On macOS 27.0.1 build 26A434, the scheduler configured a disposable worker, successfully launched the registered job, completed a second invocation, paused and resumed. Removing the job left its service, registration file and temporary worker absent. A separate removable-volume denial test detected the startup failure and rolled back the registration.

The private personal map retained its hash, owner and 0600 mode through downgrade export and restore on the tested Mac. A disposable Mac host skill installed a synthetic worker using its bundled source. Restoring the previous skill preserved every checked host file.

With network access denied, the restore rehearsal rebuilt both the candidate and last stable source, reconstructed the Mac skill, installed v2.4.0, updated to v2.5.0 and rolled back to v2.4.0. All 22 checked user files survived. That rehearsal used the development storage device. The independent-copy drill is recorded separately in the final assurance packet.

The next review candidate passed 233 applicable tests in source and packaged form. Independent review verified 12 historical edition migrations and withheld approval pending corrections to worker recovery, source verification and update instructions. The revised implementation adds a scoped operating-record snapshot and binds recovery and rollback to edition and manifest. Its focused recovery drill and production dependency audit passed locally. The detached packet must record the results for the final bytes.

## Distribution scope

v2.5.0 is the Mac candidate. The common feed stays on v2.4.0 for Windows. Earlier Windows CI passed on a development snapshot. Windows v2.5.0 desktop installation, native scheduling, historical file protection and recovery remain outside the Mac qualification. No automatic release update is eligible.

The two edition downloads, their SHA-256 sidecars and the portal inventory are verified together. The final release record must identify the signed source commit, all asset digests, both platform routes, independent recovery and the owner's decision.
