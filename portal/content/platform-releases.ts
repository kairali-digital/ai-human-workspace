const repository = "kairali-digital/ai-human-workspace";
const github = "https://github.com/" + repository;
const api = "https://api.github.com/repos/" + repository;
const publisher = "AbhilashKairali";

export const commonVersion = "2.4.0";
export const macVersion = "2.5.0";
export const releasePage = (version: string) => github + "/releases/tag/v" + version;

export const macEditions = {
  employee: "KAIRALI-AI-HUMAN-v250-EMPLOYEE-EDITION-PUBLIC-KIT.zip",
  reusable: "AI-HUMAN-v250-REUSABLE-EDITION-PUBLIC-KIT.zip",
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

export async function platformReleases(files: ReadonlyArray<{ name: string }>) {
  const installed = new Set(files.map(file => file.name));
  const bothEditionsPresent = Object.values(macEditions).every(name =>
    installed.has(name) && installed.has(name + ".sha256"));
  const [common, mac] = await Promise.all([
    readRelease("/releases/latest", commonVersion),
    bothEditionsPresent ? readRelease("/releases/tags/v" + macVersion, macVersion) : null,
  ]);
  return { common, mac: common && mac ? mac : null };
}
