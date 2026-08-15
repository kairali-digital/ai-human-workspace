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
  tag_name: "v1.5.1",
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

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#start">
          <span className="brand-mark" aria-hidden="true">K</span>
          <span className="brand-name">Kairali AI Method</span>
        </a>
        <nav aria-label="Portal navigation">
          <a href="#start">Start</a>
          <a href="#workers">Workers</a>
          <a href="#updates">Updates</a>
          <a href="#access">Access</a>
          <a href="#downloads">Downloads</a>
          <a href="#technical">Technical</a>
        </nav>
      </header>

      <section className="hero" id="start">
        <div className="hero-copy">
          <p className="eyebrow">Public AI-Human Workspace portal</p>
          <h1>One link for the complete Kairali AI Method.</h1>
          <p className="hero-summary">Open the guide, get the approved files and begin without an account.</p>
          <div className="hero-actions">
            <a className="button button-primary" href="/downloads/KAIRALI-AI-METHOD-ROLLOUT-v151-PUBLIC-KIT.zip" download>
              Download everything
            </a>
            <a className="button button-secondary" href="/downloads/EMPLOYEE-SETUP-AND-PROOF-GUIDE-v7-PUBLIC-KIT.pdf">
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
          <span>Current portal package</span>
          <strong>v1.5.1</strong>
        </div>
        <div>
          <span>Latest approved GitHub release</span>
          <strong>{release.tag_name}</strong>
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
            <p>No Terminal, Git or command line. Set your daily Email Importance Brief, complete the Full Drive Index, then optionally add Saturday LinkedIn drafts with right-level local control and human-only LinkedIn access and sending.</p>
            <a href="/downloads/EMPLOYEE-SETUP-AND-PROOF-GUIDE-v7-PUBLIC-KIT.pdf">Open employee guide</a>
          </article>
          <article className="path path-facilitator">
            <span>For facilitators</span>
            <h3>Prepare once. Share this portal.</h3>
            <p>Use the runbook, main presentation and print checklist. Keep the advanced clinic separate.</p>
            <a href="/downloads/FACILITATOR-RUNBOOK-v9-PUBLIC-KIT.pdf">Open facilitator runbook</a>
          </article>
        </div>
      </section>

      <section className="workers" id="workers" aria-labelledby="workers-heading">
        <div className="section-intro">
          <p className="eyebrow">Three-worker rollout</p>
          <h2 id="workers-heading">Available here. Live only after your proof.</h2>
          <p>The portal makes the approved starters available. It does not connect your accounts, choose your times or activate a worker. Each employee completes this readback in three separate local projects.</p>
        </div>
        <div className="worker-grid">
          <article>
            <span className="worker-status">Required</span>
            <h3>Daily Email Triage</h3>
            <p>Mark <strong>LIVE FOR ME</strong> only after the approved Gmail account, daily time and time zone, read-only pilot, filing-mode ruling, automation card and validator agree.</p>
          </article>
          <article>
            <span className="worker-status">Required</span>
            <h3>Full Drive Index</h3>
            <p>Mark <strong>LIVE FOR ME</strong> only after every supported scope ends in checkpointed batches, and the CSV, summary, final cursor and validator agree. <strong>TEST 25 proves setup only.</strong></p>
          </article>
          <article>
            <span className="worker-status worker-status-optional">Optional</span>
            <h3>Saturday LinkedIn Message Assistant</h3>
            <p>If chosen, prove the schedule, scoped local control, <strong>YOUR TURN ON LINKEDIN</strong> handoff, manually supplied pilot and local queue. Otherwise record <strong>NOT ENABLED BY CHOICE</strong>.</p>
          </article>
        </div>
        <p className="worker-note">Downloaded, installed or connected alone does not mean live. Show the local report, cursor, evidence and validator.</p>
      </section>

      <section className="update-flow" id="updates" aria-labelledby="updates-heading">
        <div className="section-intro">
          <p className="eyebrow">Managed updates</p>
          <h2 id="updates-heading">A new release starts with a check, not an overwrite.</h2>
          <p>The company notice names the version and affected files. Open the existing worker and ask the Setup Helper to check. The check is read-only; applying waits for your approval at a safe checkpoint.</p>
        </div>
        <div className="update-steps">
          <article>
            <span>1</span>
            <h3>Open the existing worker.</h3>
            <p>Start a new Codex chat and paste <strong>CHECK FOR KAIRALI UPDATE</strong>. You never type a command.</p>
          </article>
          <article>
            <span>2</span>
            <h3>Read the check.</h3>
            <p>The helper shows installed and latest versions, changes, live-task status, managed files and preserved employee state. No file changes yet.</p>
          </article>
          <article>
            <span>3</span>
            <h3>Approve at a checkpoint.</h3>
            <p>A live task defers the update. Otherwise, say <strong>UPDATE NOW</strong>. The helper backs up, verifies hashes, applies only managed files and validates.</p>
          </article>
          <article>
            <span>4</span>
            <h3>Prove every worker.</h3>
            <p>Employee-owned state stays preserved. The employee keeps the version, validation receipt and preserved-state proof. Monitor reports missing, deferred or mismatched workers without rewriting them.</p>
          </article>
        </div>
        <div className="update-boundary">
          <p><strong>Automatic:</strong> the stable portal follows the approved release and a session may check for a newer version.</p>
          <p><strong>Manual:</strong> the employee approves the apply. GitHub Desktop Fetch/Pull synchronizes only the selected repository; it does not install this managed update.</p>
        </div>
        <a className="access-link" href="/downloads/KAIRALI-MANAGED-UPDATE-WORKFLOW.md" download>Download the exact check prompt and recovery workflow</a>
      </section>

      <section className="access-boundary" id="access" aria-labelledby="access-heading">
        <div className="section-intro">
          <p className="eyebrow">Right-level access</p>
          <h2 id="access-heading">Mouse and browser control, with a hard LinkedIn handoff.</h2>
          <p>The portal cannot grant computer access. The real permission prompt appears inside ChatGPT when the employee starts an approved Computer or Chrome task.</p>
        </div>
        <div className="access-grid">
          <article>
            <span>1</span>
            <h3>Choose Computer.</h3>
            <p>Close LinkedIn. Start the local request with <code>@Computer</code>. Approve only the visible local project and current task. Keep Ask for approval. Never choose Full access or Always allow.</p>
          </article>
          <article>
            <span>2</span>
            <h3>Stop before LinkedIn.</h3>
            <p>Computer and Chrome control stop first. Codex shows <strong>YOUR TURN ON LINKEDIN</strong> and makes no screen, mouse, keyboard or browser action while LinkedIn is visible.</p>
          </article>
          <article>
            <span>3</span>
            <h3>You take over.</h3>
            <p>You copy no more than 25 conversations, close LinkedIn, return to the local project and say BATCH READY. You also review, paste and send every approved reply yourself.</p>
          </article>
        </div>
        <a className="access-link" href="https://learn.chatgpt.com/use-cases/use-your-computer-with-codex" target="_blank" rel="noreferrer">Read the official Computer Use guide</a>
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
          <p>The portal reads the latest approved public release. Training files update from GitHub only after validation and review. Fetch/Pull updates a repository checkout, not an installed worker.</p>
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
            <p>Automated gates check the workspace, downloads, indexing controls and production build.</p>
          </article>
          <article>
            <h3>Publish the approved result</h3>
            <p>Vercel updates this stable portal after the reviewed GitHub change reaches the production branch.</p>
          </article>
          <article>
            <h3>Announce and prove the batch</h3>
            <p>The company sends the exact check prompt to no more than 25 employees. Setup Helper receipts and Monitor readback prove completion.</p>
          </article>
        </div>
      </section>

      <footer>
        <p>This public portal is designed for discovery and contains no confidential information, credentials, private evidence, or live employee work.</p>
        <a href="/downloads/SETUP-HELPER-CARD-v7-PUBLIC-KIT.pdf">Stuck? Open the Setup Helper card.</a>
      </footer>
    </main>
  );
}
