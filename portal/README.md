# Kairali AI Method portal

This is the stable, no-login delivery page for approved Kairali AI Method material.

## Important boundary

`noindex` keeps the portal out of normal search results. It is not authentication. Anyone with the link can open it, so the portal must contain no confidential information, credentials, private evidence or live employee work.

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
