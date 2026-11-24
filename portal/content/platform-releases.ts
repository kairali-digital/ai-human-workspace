import { createHash } from "node:crypto";

const repository = "kairali-digital/ai-human-workspace";
const github = "https://github.com/" + repository;
const api = "https://api.github.com/repos/" + repository;
const publisher = "AbhilashKairali";

export const commonVersion = "2.4.0";
export const windowsVersion = "2.5.1";
export const macVersion = "2.5.0";
export const releasePage = (version: string) => github + "/releases/tag/v" + version;

export const macEditions = {
  employee: "KAIRALI-AI-HUMAN-v250-EMPLOYEE-EDITION-PUBLIC-KIT.zip",
  reusable: "AI-HUMAN-v250-REUSABLE-EDITION-PUBLIC-KIT.zip",
};

export const windowsEditions = {
  employee: "KAIRALI-AI-HUMAN-v251-EMPLOYEE-EDITION-PUBLIC-KIT.zip",
  reusable: "AI-HUMAN-v251-REUSABLE-EDITION-PUBLIC-KIT.zip",
};

type Asset = { name: string; state: string; size: number; digest: string; browser_download_url: string };
export type Release = { tag_name: string; html_url: string; assets: Asset[] };

export function checkedRelease(data: unknown, version: string): Release | null {
  if (typeof data !== "object" || data === null) return null;
  const release = data as Partial<Release> & {
    author?: { login?: string }; draft?: boolean; prerelease?: boolean;
  };
  if (release.author?.login !== publisher || release.tag_name !== "v" + version ||
      release.html_url !== releasePage(version) || release.draft !== false ||
      release.prerelease !== false || !Array.isArray(release.assets)) return null;
  const assets = release.assets;
  const required = ["ai-human-workspace-" + version + ".zip", "kairali-company-rollout-" + version + ".zip",
    "RELEASE-NOTES-v" + version + ".md", "VET-v" + version + ".md", "release-proof.json", "SHA256SUMS"];
  for (const name of required) {
    const matching = assets.filter(asset => asset?.name === name);
    const asset = matching[0];
    if (matching.length !== 1 || asset.state !== "uploaded" || !(asset.size > 0) ||
        !/^sha256:[a-f0-9]{64}$/.test(asset.digest) ||
        asset.browser_download_url !== github + "/releases/download/v" + version + "/" + name) return null;
  }
  return { tag_name: "v" + version, html_url: releasePage(version), assets };
}

async function readRelease(endpoint: string, version: string) {
  try {
    const response = await fetch(api + endpoint, {
      headers: { Accept: "application/vnd.github+json" }, next: { revalidate: 300 },
    });
    return response.ok ? checkedRelease(await response.json(), version) : null;
  } catch {
    return null;
  }
}

type Download = { name: string; sha256: string };

// The release packet is produced after signing. Keeping its digest outside the
// source tree avoids making the release archive contain its own checksum.
async function approvedWindowsRelease(files: ReadonlyArray<Download>) {
  const approval = process.env.WINDOWS_V251_RELEASE_PACKET_SHA256;
  if (!approval || !/^[a-f0-9]{64}$/.test(approval)) return null;
  try {
    const [release, response] = await Promise.all([
      readRelease("/releases/tags/v" + windowsVersion, windowsVersion),
      fetch(api + "/commits/v" + windowsVersion, {
        headers: { Accept: "application/vnd.github+json" }, next: { revalidate: 300 },
      }),
    ]);
    if (!release || !response.ok || release.assets.length !== 6) return null;
    const commit = await response.json();
    if (!/^[a-f0-9]{40}$/.test(commit.sha) || commit.author?.login !== publisher ||
        commit.commit?.verification?.verified !== true || commit.commit.verification.reason !== "valid") return null;
    const entries = release.assets.map(asset => asset.name + " " + asset.digest.slice(7));
    for (const name of Object.values(windowsEditions)) {
      for (const filename of [name, name + ".sha256"]) {
        const matching = files.filter(file => file.name === filename);
        if (matching.length !== 1 || !/^[a-f0-9]{64}$/.test(matching[0].sha256)) return null;
        entries.push(filename + " " + matching[0].sha256);
      }
    }
    const packet = [commit.sha, ...entries.sort()].join("\n") + "\n";
    return createHash("sha256").update(packet).digest("hex") === approval ? release : null;
  } catch {
    return null;
  }
}

export async function platformReleases(files: ReadonlyArray<Download>) {
  const installed = new Set(files.map(file => file.name));
  const complete = (editions: typeof macEditions) => Object.values(editions).every(name =>
    installed.has(name) && installed.has(name + ".sha256"));
  const [common, mac, windows] = await Promise.all([
    readRelease("/releases/tags/v" + commonVersion, commonVersion),
    complete(macEditions) ? readRelease("/releases/tags/v" + macVersion, macVersion) : null,
    complete(windowsEditions) ? approvedWindowsRelease(files) : null,
  ]);
  return { common, mac, windows };
}
