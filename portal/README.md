# Kairali AI Method portal

This is the stable, no-login delivery page for approved Kairali AI Method material.

## Important boundary

The portal is deliberately indexable and therefore public. Search indexing is not a
release or approval signal. v2.0.1 is held after a post-publication Monitor finding.
v2.4.0 is a public release only where its repository manifests and immutable release
proof say `APPROVED_BY_OWNER` / `RELEASED` and that channel's protected production
gates pass. Candidate labels and install refusals remain authoritative. Download files
carry a scoped `noindex` response header, but anyone with their URL can still open them.
The portal and downloads must contain no confidential information, credentials, private
evidence or live employee work.

## Local check

```text
npm install
npm run validate
npm run typecheck
npm run build
```

## Approved update flow

1. Amend governed source files in GitHub.
2. Regenerate every affected PPTX, PDF, DOCX, homework or release archive.
3. Replace the matching file in `public/downloads/`.
4. Run `npm run refresh-downloads` to update the committed hash manifest.
5. Run the portal and repository gates.
6. Push a branch and review its Vercel preview.
7. Merge only the approved change to the production branch. Vercel then updates the stable portal URL.

Do not edit only the website label when the downloadable file also changed. A change is complete only when the source, generated artifact, download manifest and portal agree.

## Mac-only v2.5.0 publication

Before publication, verify the default GitHub release is v2.4.0 and record its identity. Freeze the two v2.5.0 edition ZIPs, their sidecars and the refreshed download manifest together. Keep the private preview and its downloads local until the owner approves the exact release and website.

When publishing the approved Mac release, explicitly set `make_latest` to the string `"false"` on the GitHub release. Read back both `/releases/latest` (v2.4.0) and `/releases/tags/v2.5.0` (approved publisher and six checked assets). Stop distribution if either readback differs. Verify both Windows buttons still deliver the approved v2.4.0 ZIPs and both Mac buttons deliver the approved v2.5.0 ZIPs. Compare SHA-256 against the frozen packet before announcing. The Mac update notice must identify the exact signed commit for manual installation. Keep automatic updates ineligible for this release.
