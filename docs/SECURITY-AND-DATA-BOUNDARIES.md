# Security and data boundaries

## Public repository may contain

- company-neutral operating rules;
- blank or placeholder templates;
- lifecycle tooling and tests;
- public documentation; and
- release manifests, hashes and validation evidence.
- owner-approved company role templates, governed skills and blank homework workers
  that contain no live employee or customer data.

## Public repository must not contain

- employee live state, workload or performance data;
- customer, order, payment, medical, HR or banking data;
- credentials, tokens, cookies, browser profiles or private keys;
- private platform identifiers, admin links or support cases;
- company strategy, unpublished commercial plans or private evidence; or
- absolute paths that disclose an employee's computer username or folder layout.

## Release controls

Every pull request runs release validation and lifecycle tests. Every public release
also receives a full Git-history secret scan. Ordinary employees never receive bypass
permission for release controls.

The release proof is an enforced exact inventory, not a decorative artifact. Managed
sources, component trees and update targets reject symbolic-link redirection. JSON
control files reject duplicate keys. Download extraction rejects traversal, duplicate
or symbolic-link members and archives beyond the bounded source-release envelope.

Production workflows pin remote Actions to immutable commits. The portal audits its
production dependency graph before build and deployment, applies a restrictive content
security policy and sends transport, framing, referrer, capability and content-type
headers. Download responses remain separately `noindex`.

The core can stop and escalate sensitive topics; it does not replace the company's
legal, HR, security, finance or medical review processes.
