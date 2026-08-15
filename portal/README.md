# Kairali AI Method public portal

This deployment is the public, indexable landing page and download infrastructure for the Kairali AI Method and AI-Human Workspace. Its stable URL is [kairali-ai-method.vercel.app](https://kairali-ai-method.vercel.app), and existing `/downloads/*` links remain available at their original URLs.

## Important boundary

The landing page is deliberately indexable and canonical at the stable Vercel URL. Download responses remain available but carry a scoped `X-Robots-Tag` so search engines focus on the landing page. This is a public site, so it must contain no confidential information, credentials, private evidence or live employee work.

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
7. Merge only the approved change to the production branch. Vercel then updates the public deployment while the stable landing-page and download URLs remain unchanged.

Do not edit only the website label when the downloadable file also changed. A change is complete only when the source, generated artifact, download manifest and portal agree.
