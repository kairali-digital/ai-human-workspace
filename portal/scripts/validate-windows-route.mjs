import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { platformReleases, windowsEditions, windowsVersion } from "../content/platform-releases.ts";

const github = "https://github.com/kairali-digital/ai-human-workspace";
const version = windowsVersion;
const tag = "v" + version;
const commit = "a".repeat(40);
const names = ["ai-human-workspace-" + version + ".zip", "kairali-company-rollout-" + version + ".zip",
  "RELEASE-NOTES-" + tag + ".md", "VET-" + tag + ".md", "release-proof.json", "SHA256SUMS"];
const hash = text => createHash("sha256").update(text).digest("hex");
const assets = names.map(name => ({ name, state: "uploaded", size: 1, digest: "sha256:" + hash(name),
  browser_download_url: github + "/releases/download/" + tag + "/" + name }));
const release = { author: { login: "AbhilashKairali" }, draft: false, prerelease: false, tag_name: tag,
  html_url: github + "/releases/tag/" + tag, assets };
const signed = { sha: commit, author: release.author, commit: { verification: { verified: true, reason: "valid" } } };
const inventory = JSON.parse(await readFile(new URL("../content/download-manifest.json", import.meta.url))).files;
const editions = new Set(Object.values(windowsEditions).flatMap(name => [name, name + ".sha256"]));
const entries = [...names.map(name => name + " " + hash(name)),
  ...inventory.filter(file => editions.has(file.name)).map(file => file.name + " " + file.sha256)];
assert.equal(entries.length, 10);
const packet = hash([commit, ...entries.sort()].join("\n") + "\n");

async function check(label, { approval = packet, inputs = inventory, releaseData = release, commitData = signed }, expected) {
  process.env.WINDOWS_V251_RELEASE_PACKET_SHA256 = approval;
  globalThis.fetch = async url => {
    assert.ok(!url.endsWith("/latest"));
    const data = url.endsWith("/commits/" + tag) ? commitData : url.endsWith("/releases/tags/" + tag) ? releaseData : null;
    return { ok: Boolean(data), json: async () => data };
  };
  assert.equal(Boolean((await platformReleases(inputs)).windows), expected, label);
}
await check("exact signed release", {}, true);
await check("unpublished", { releaseData: null }, false);
await check("missing packet", { approval: "" }, false);
await check("wrong commit", { commitData: { ...signed, sha: "b".repeat(40) } }, false);
await check("invalid signature", { commitData: { ...signed, commit: {} } }, false);
await check("wrong asset hash", { releaseData: { ...release, assets: assets.map(a => ({ ...a, digest: "sha256:" + hash("other") })) } }, false);
await check("wrong local ZIP", { inputs: inventory.map(f => editions.has(f.name) ? { ...f, sha256: hash("other") } : f) }, false);
await check("missing ZIP", { inputs: inventory.filter(f => f.name !== windowsEditions.employee) }, false);
console.log("Windows release routing passed eight cases.");
