# Security and data boundaries

## Public repository may contain

- company-neutral operating rules;
- blank or placeholder templates;
- lifecycle tooling and tests;
- public documentation; and
- release manifests, hashes and validation evidence.

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

The core can stop and escalate sensitive topics; it does not replace the company's
legal, HR, security, finance or medical review processes.
