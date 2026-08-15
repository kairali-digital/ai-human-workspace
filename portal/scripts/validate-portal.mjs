import { createHash } from "node:crypto";
import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const manifest = JSON.parse(await readFile(path.join(root, "content", "download-manifest.json"), "utf8"));
const issues = [];
const required = new Set([
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

const route = await readFile(path.join(root, "app", "route.ts"), "utf8");
const layout = await readFile(path.join(root, "app", "layout.tsx"), "utf8");
const nextConfig = await readFile(path.join(root, "next.config.ts"), "utf8");
const robots = await readFile(path.join(root, "app", "robots.ts"), "utf8");
const siteData = await readFile(path.join(root, "content", "site-data.ts"), "utf8");
const downloadLinkSources = siteData;
const redirectTarget = "https://abhilashkr.com/#ai-human-workspace";

if (!route.includes(redirectTarget) || !route.includes("status: 308") || !route.includes("Location: canonicalOverview")) issues.push(`root route does not emit a 308 redirect to: ${redirectTarget}`);
if (!route.includes('"X-Robots-Tag": noindexPolicy') || !route.includes("noindex")) issues.push("root redirect does not retain the X-Robots-Tag noindex policy");
if (!layout.includes("index: false") || !layout.includes("follow: false")) issues.push("metadata robots are not noindex and nofollow");
if (!nextConfig.includes("X-Robots-Tag") || !nextConfig.includes("noindex")) issues.push("X-Robots-Tag noindex header is missing");
if (!robots.includes('disallow: "/"')) issues.push("robots.txt does not disallow all crawling");
if (downloadLinkSources.includes("—") || downloadLinkSources.includes("–")) issues.push("portal source contains a prohibited long dash");

const hrefFiles = [...downloadLinkSources.matchAll(/(?:href:|href=)[{]?`?\"?\/downloads\/([^`\"}]+?)(?:`|\"|})/g)].map((match) => decodeURIComponent(match[1]));
for (const file of hrefFiles) {
  if (!records.has(file)) issues.push(`page links to an unmanifested download: ${file}`);
}

const personalPath = /(?:\/Users\/[^/\s]+\/|\/home\/[^/\s]+\/|[A-Za-z]:[\\]Users[\\][^\\\s]+[\\])/;
for (const candidate of [route, layout, nextConfig, robots, downloadLinkSources, JSON.stringify(manifest)]) {
  if (personalPath.test(candidate)) issues.push("portal source exposes a personal absolute path");
}

if (issues.length) {
  console.error("PORTAL VALIDATION: FAIL");
  for (const issue of issues) console.error(`- ${issue}`);
  process.exit(1);
}

console.log("PORTAL VALIDATION: PASS");
console.log(`- downloads verified: ${records.size}`);
console.log(`- root 308 redirect verified: ${redirectTarget}`);
console.log("- noindex metadata, response header and robots.txt present");
console.log("- no personal absolute path or long dash in portal source");
