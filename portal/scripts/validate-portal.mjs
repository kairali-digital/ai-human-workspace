import { createHash } from "node:crypto";
import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const manifest = JSON.parse(await readFile(path.join(root, "content", "download-manifest.json"), "utf8"));
const packageManifest = JSON.parse(await readFile(path.join(root, "package.json"), "utf8"));
const packageLock = JSON.parse(await readFile(path.join(root, "package-lock.json"), "utf8"));
const issues = [];
if (packageManifest.engines?.node !== "22.x") {
  issues.push("portal Node runtime must remain pinned to the tested 22.x line");
}
if (packageLock.packages?.[""]?.engines?.node !== packageManifest.engines?.node) {
  issues.push("package-lock root Node runtime does not match package.json");
}
const required = new Set([
  "AI-HUMAN-v210-REUSABLE-EDITION-PUBLIC-KIT.zip",
  "AI-HUMAN-v210-REUSABLE-EDITION-PUBLIC-KIT.zip.sha256",
  "KAIRALI-AI-HUMAN-v210-EMPLOYEE-EDITION-PUBLIC-KIT.zip",
  "KAIRALI-AI-HUMAN-v210-EMPLOYEE-EDITION-PUBLIC-KIT.zip.sha256",
  "KAIRALI-AI-METHOD-ROLLOUT-v151-PUBLIC-KIT.zip",
  "KAIRALI-AI-METHOD-DECK-v16-PUBLIC-KIT.pptx",
  "KAIRALI-AI-METHOD-ADVANCED-CLI-BONUS-v8-PUBLIC-KIT.pptx",
  "EMPLOYEE-SETUP-AND-PROOF-GUIDE-v7-PUBLIC-KIT.pdf",
  "FACILITATOR-RUNBOOK-v9-PUBLIC-KIT.pdf",
  "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-PACK.zip",
  "SETUP-HELPER-CARD-v7-PUBLIC-KIT.pdf",
  "KAIRALI-MANAGED-UPDATE-WORKFLOW.md",
]);

const records = new Map(manifest.files.map((file) => [file.name, file]));
for (const name of required) {
  if (!records.has(name)) issues.push(`manifest lacks required download: ${name}`);
}

const downloads = path.join(root, "public", "downloads");
const actual = (await readdir(downloads)).sort();
const listed = [...records.keys()].sort();
if (JSON.stringify(actual) !== JSON.stringify(listed)) issues.push("download directory and manifest inventory differ");

for (const [name, record] of records) {
  const file = path.join(downloads, name);
  try {
    const details = await stat(file);
    const bytes = await readFile(file);
    const digest = createHash("sha256").update(bytes).digest("hex");
    if (details.size !== record.size) issues.push(`size mismatch: ${name}`);
    if (digest !== record.sha256) issues.push(`hash mismatch: ${name}`);
    if (details.size > 50 * 1024 * 1024) issues.push(`download exceeds 50 MB portal cap: ${name}`);
  } catch {
    issues.push(`missing download: ${name}`);
  }
}

const page = await readFile(path.join(root, "app", "page.tsx"), "utf8");
const layout = await readFile(path.join(root, "app", "layout.tsx"), "utf8");
const nextConfig = await readFile(path.join(root, "next.config.ts"), "utf8");
const robots = await readFile(path.join(root, "app", "robots.ts"), "utf8");
const sitemap = await readFile(path.join(root, "app", "sitemap.ts"), "utf8");
const visible = `${page}\n${await readFile(path.join(root, "content", "site-data.ts"), "utf8")}`;

for (const phrase of ["Kairali employee edition", "Reusable edition", "Install in five steps", "DONE WHEN", "Mac", "Windows", "Extract All", "Suspend", "Resume", "Uninstall", "Revoke access", "Troubleshooting", "Polite pushback, then a useful path forward", "nearest compliant next step", "SUSPENDED", "UNINSTALLED", "Plugin uninstall can also leave its connector connected", "Use the Setup Helper", "Use the smallest path that matches the effect.", "One document with 150 rows uploads intact", "Creating 150 GitHub issues", "No universal compliance shortcut.", "exact legal entity", "Historical charts", "Unanswered compliance questions block ACTIVE.", "separate worker folders and profiles", "One kind of data, one file of record", "gate-profile.json", "COMPLETED_LEDGER.md", "daily Email Importance Brief", "chosen-time daily email brief", "FULL DRIVE INDEX", "AI JSONL", "approved Sheet mirror", "relationship counts", "Weekly refresh is optional", "Saturday LinkedIn Message Assistant", "right-level local control", "human-only LinkedIn access and sending", "Available here. Live only after your proof.", "LIVE FOR ME", "TEST 25 proves setup only", "NOT ENABLED BY CHOICE", "@Computer", "YOUR TURN ON LINKEDIN", "The portal cannot grant computer access", "GitHub stays the approved source of truth", "CHECK FOR KAIRALI UPDATE", "CHECK FOR AI-HUMAN UPDATE", "UPDATE NOW", "Fetch/Pull", "read-only", "Monitor", "v2.1.0", "user-owned state preserved"]) {
  if (!visible.includes(phrase)) issues.push(`visible portal copy lacks: ${phrase}`);
}
if (!layout.includes("metadataBase: new URL(SITE_URL)") || !layout.includes('canonical: "/"')) issues.push("canonical metadata is missing");
if (!layout.includes("index: true") || !layout.includes("follow: true")) issues.push("metadata robots are not index and follow");
if (!robots.includes('allow: "/"') || robots.includes('disallow: "/"')) issues.push("robots.txt does not allow site crawling");
if (!robots.includes("sitemap:") || !robots.includes("host:")) issues.push("robots.txt lacks canonical sitemap or host");
if (!sitemap.includes("SITE_URL") || !sitemap.includes("MetadataRoute.Sitemap")) issues.push("sitemap source is missing or malformed");
if (!nextConfig.includes('source: "/downloads/:path*"') || !nextConfig.includes("X-Robots-Tag") || !nextConfig.includes("noindex")) issues.push("download-only X-Robots-Tag noindex header is missing");
const globalHeaderBlock = nextConfig.match(/const securityHeaders = \[([\s\S]*?)\];/)?.[1] ?? "";
if (globalHeaderBlock.includes("X-Robots-Tag")) issues.push("global X-Robots-Tag can block portal indexing");
for (const header of ["Content-Security-Policy", "Strict-Transport-Security", "Cross-Origin-Opener-Policy", "Cross-Origin-Resource-Policy", "X-Content-Type-Options", "X-Frame-Options", "Referrer-Policy", "Permissions-Policy"]) {
  if (!globalHeaderBlock.includes(header)) issues.push(`global security header is missing: ${header}`);
}
for (const directive of ["base-uri 'self'", "frame-ancestors 'none'", "object-src 'none'"]) {
  if (!globalHeaderBlock.includes(directive)) issues.push(`content security policy lacks: ${directive}`);
}
if (!nextConfig.includes('process.env.NODE_ENV === "development"') || !nextConfig.includes("'unsafe-eval'")) issues.push("development-only React debugging CSP exception is missing");
if (!nextConfig.includes(': "\'self\' \'unsafe-inline\'";')) issues.push("production script CSP does not remove unsafe-eval");
if (page.includes("`.ai-human`")) issues.push("visible portal copy renders literal Markdown backticks");
const assetAnchors = [...page.matchAll(/<a href=\{assetLink\([^>]+>/g)].map((match) => match[0]);
if (assetAnchors.length !== 2 || assetAnchors.some((anchor) => !anchor.includes('target="_blank"') || !anchor.includes('rel="noreferrer"'))) {
  issues.push("approved release asset links must open safely in a new tab");
}
if (visible.includes("—") || visible.includes("–")) issues.push("visible copy contains a prohibited long dash");

const hrefFiles = [...visible.matchAll(/(?:href:|href=)[{]?`?\"?\/downloads\/([^`\"}]+?)(?:`|\"|})/g)].map((match) => decodeURIComponent(match[1]));
for (const file of hrefFiles) {
  if (!records.has(file)) issues.push(`page links to an unmanifested download: ${file}`);
}
const primaryEditionLinks = hrefFiles.filter((file) => file.endsWith("EDITION-PUBLIC-KIT.zip"));
if (new Set(primaryEditionLinks).size !== 2) issues.push("portal must link exactly two primary edition ZIPs");
if (visible.includes("Download everything") || visible.includes("href=\"/downloads/KAIRALI-AI-METHOD-ROLLOUT-v151-PUBLIC-KIT.zip\"")) {
  issues.push("portal retains the ambiguous single-pack download path");
}

const personalPath = /(?:\/Users\/[^/\s]+\/|\/home\/[^/\s]+\/|[A-Za-z]:[\\]Users[\\][^\\\s]+[\\])/;
for (const candidate of [page, layout, nextConfig, robots, visible, JSON.stringify(manifest)]) {
  if (personalPath.test(candidate)) issues.push("portal source exposes a personal absolute path");
}

if (issues.length) {
  console.error("PORTAL VALIDATION: FAIL");
  for (const issue of issues) console.error(`- ${issue}`);
  process.exit(1);
}

console.log("PORTAL VALIDATION: PASS");
console.log(`- downloads verified: ${records.size}`);
console.log("- indexable metadata, canonical URL, robots.txt and sitemap present");
console.log("- download assets retain a scoped noindex response header");
console.log("- no personal absolute path or long dash in visible source");
