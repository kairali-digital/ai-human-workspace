import Image from "next/image";
import { DownloadGroup } from "../components/download-group";
import { downloadGroups } from "../content/site-data";

type GithubAsset = {
  name: string;
  browser_download_url: string;
};

type GithubRelease = {
  tag_name: string;
  html_url: string;
  published_at: string;
  assets: GithubAsset[];
};

const fallbackRelease: GithubRelease = {
  tag_name: "v1.1.0",
  html_url: "https://github.com/kairali-digital/ai-human-workspace/releases/latest",
  published_at: "2026-08-12T00:00:00Z",
  assets: [],
};

async function getLatestRelease() {
  try {
    const response = await fetch(
      "https://api.github.com/repos/kairali-digital/ai-human-workspace/releases/latest",
      {
        headers: { Accept: "application/vnd.github+json" },
        next: { revalidate: 300 },
      },
    );
    if (!response.ok) return { release: fallbackRelease, live: false };
    return { release: (await response.json()) as GithubRelease, live: true };
  } catch {
    return { release: fallbackRelease, live: false };
  }
}

function assetLink(release: GithubRelease, prefix: string) {
  return release.assets.find((asset) => asset.name.startsWith(prefix))?.browser_download_url ?? release.html_url;
}

export default async function Home() {
  const { release, live } = await getLatestRelease();
  const releaseDate = new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(release.published_at));

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#start" aria-label="Kairali AI Method home">
          <span className="brand-mark" aria-hidden="true">K</span>
          <span>Kairali AI Method</span>
        </a>
        <nav aria-label="Portal navigation">
          <a href="#start">Start</a>
          <a href="#downloads">Downloads</a>
          <a href="#technical">Technical</a>
        </nav>
      </header>

      <section className="hero" id="start">
        <div className="hero-copy">
          <p className="eyebrow">Internal training portal</p>
          <h1>One link for the complete Kairali AI Method.</h1>
          <p className="hero-summary">Open the guide, get the approved files and begin without an account.</p>
          <div className="hero-actions">
            <a className="button button-primary" href="/downloads/KAIRALI-AI-METHOD-ROLLOUT-v11-PUBLIC-KIT.zip" download>
              Download everything
            </a>
            <a className="button button-secondary" href="/downloads/EMPLOYEE-SETUP-AND-PROOF-GUIDE-v3-PUBLIC-KIT.pdf">
              Read the start guide
            </a>
          </div>
        </div>
        <div className="hero-media">
          <Image
            src="/media/hero-workspace.png"
            alt="A calm desk with a laptop, printed pages and a folder ready for guided work"
            fill
            priority
            sizes="(max-width: 767px) 100vw, 48vw"
          />
        </div>
      </section>

      <section className="release-strip" aria-label="Current source status">
        <div>
          <span>Current approved GitHub release</span>
          <strong>{release.tag_name}</strong>
        </div>
        <div>
          <span>Published</span>
          <strong>{releaseDate}</strong>
        </div>
        <div>
          <span>Access</span>
          <strong>No login required</strong>
        </div>
        <a href={release.html_url} target="_blank" rel="noreferrer">View source release</a>
        {!live ? <p className="release-fallback">Live release check is temporarily unavailable. The last approved release is shown.</p> : null}
      </section>

      <section className="start-paths" aria-labelledby="choose-heading">
        <div className="section-intro">
          <h2 id="choose-heading">Choose the path that matches today.</h2>
          <p>Employees start with the guide. Facilitators prepare the room and use the presentation.</p>
        </div>
        <div className="path-grid">
          <article className="path path-employee">
            <span>For employees</span>
            <h3>Use the Setup Helper.</h3>
            <p>No Terminal, Git or command line. Complete Email and Drive homework first.</p>
            <a href="/downloads/EMPLOYEE-SETUP-AND-PROOF-GUIDE-v3-PUBLIC-KIT.pdf">Open employee guide</a>
          </article>
          <article className="path path-facilitator">
            <span>For facilitators</span>
            <h3>Prepare once. Share this portal.</h3>
            <p>Use the runbook, main presentation and print checklist. Keep the advanced clinic separate.</p>
            <a href="/downloads/FACILITATOR-RUNBOOK-v5-PUBLIC-KIT.pdf">Open facilitator runbook</a>
          </article>
        </div>
      </section>

      <section className="downloads" id="downloads" aria-labelledby="downloads-heading">
        <div className="download-visual">
          <div className="download-visual-image">
            <Image
              src="/media/guides-workspace.png"
              alt="Printed guides and presentation pages arranged beside a green folder"
              fill
              sizes="(max-width: 767px) 100vw, 42vw"
            />
          </div>
          <div>
            <h2 id="downloads-heading">Every approved file, in one place.</h2>
            <p>Use the PDF for reading, the editable file for approved updates, or the complete ZIP for an offline copy.</p>
          </div>
        </div>
        <div className="download-grid">
          {downloadGroups.map((group) => <DownloadGroup group={group} key={group.title} />)}
        </div>
      </section>

      <section className="technical" id="technical" aria-labelledby="technical-heading">
        <div>
          <p className="eyebrow">Technical and owner path</p>
          <h2 id="technical-heading">GitHub stays the approved source of truth.</h2>
          <p>The portal reads the latest approved public release. Training files update from GitHub only after validation and review.</p>
        </div>
        <div className="technical-links">
          <a href={assetLink(release, "ai-human-workspace-")}>
            <span>Workspace core</span>
            <strong>Download latest approved ZIP</strong>
          </a>
          <a href={assetLink(release, "kairali-company-rollout-")}>
            <span>Company kit and opt-in skills</span>
            <strong>Download latest approved ZIP</strong>
          </a>
          <a href="https://github.com/kairali-digital/ai-human-workspace" target="_blank" rel="noreferrer">
            <span>Public repository</span>
            <strong>Review source and release history</strong>
          </a>
        </div>
      </section>

      <section className="update-policy" aria-labelledby="updates-heading">
        <h2 id="updates-heading">How the single link stays safe.</h2>
        <div className="policy-grid">
          <article>
            <h3>Amend in GitHub</h3>
            <p>Update the governed source and regenerate affected presentation or homework files.</p>
          </article>
          <article>
            <h3>Validate the release</h3>
            <p>Automated gates check the workspace, downloads, noindex controls and production build.</p>
          </article>
          <article>
            <h3>Publish the approved result</h3>
            <p>Vercel updates this stable portal after the reviewed GitHub change reaches the production branch.</p>
          </article>
        </div>
      </section>

      <footer>
        <p>This portal is intentionally excluded from search engines. Anyone with the link can open it, so it must contain no confidential information.</p>
        <a href="/downloads/SETUP-HELPER-CARD-v3-PUBLIC-KIT.pdf">Stuck? Open the Setup Helper card.</a>
      </footer>
    </main>
  );
}
