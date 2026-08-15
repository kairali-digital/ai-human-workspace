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
  tag_name: "v2.0.2",
  html_url: "https://github.com/kairali-digital/ai-human-workspace/releases/tag/v2.0.2",
  published_at: "2026-08-16T00:00:00Z",
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
          <span className="brand-mark" aria-hidden="true">AI</span>
          <span className="brand-name">AI-Human Workspace</span>
        </a>
        <nav aria-label="Portal navigation">
          <a href="#install">Install</a>
          <a href="#work-paths">How work runs</a>
          <a href="#gate-profile">Gate 0</a>
          <a href="#files">Files</a>
          <a href="#control">Turn off</a>
          <a href="#troubleshooting">Help</a>
        </nav>
      </header>

      <section className="hero" id="start">
        <div className="hero-copy">
          <p className="eyebrow">Released v2.0.2</p>
          <h1>Install it simply. Turn it off cleanly.</h1>
          <p className="hero-summary">Choose the correct edition, follow five visible steps and prove whether the system is ON, OFF or GONE.</p>
          <div className="hero-actions">
            <a className="button button-primary" href="/downloads/KAIRALI-AI-HUMAN-v202-EMPLOYEE-EDITION-PUBLIC-KIT.zip" download>
              Kairali employee edition
            </a>
            <a className="button button-secondary" href="/downloads/AI-HUMAN-v202-REUSABLE-EDITION-PUBLIC-KIT.zip" download>
              Reusable edition
            </a>
          </div>
          <p className="release-note">These are separate, verified public downloads. Configured v2.0.0 and held v2.0.1 workers can take the v2.0.2 correction at a safe checkpoint. Pre-v2 workers first use the guided exact-scope Gate 0 migration.</p>
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
          <span>Current public workspace</span>
          <strong>v2.0.2 RELEASED</strong>
        </div>
        <div>
          <span>Latest approved GitHub release</span>
          <strong>{release.tag_name}</strong>
        </div>
        <div>
          <span>Existing-worker update</span>
          <strong>v2.0.0 or held v2.0.1; pre-v2 migration</strong>
        </div>
        <a href={release.html_url} target="_blank" rel="noreferrer">View source release</a>
        {!live ? <p className="release-fallback">Live release check is temporarily unavailable. The last approved release is shown.</p> : null}
      </section>

      <section className="start-paths" id="editions" aria-labelledby="choose-heading">
        <div className="section-intro">
          <p className="eyebrow">Two clean downloads</p>
          <h2 id="choose-heading">Choose by who you are.</h2>
          <p>The editions are deliberately separate. Do not give the Kairali package to an outside user and do not give a Kairali employee the generic package.</p>
        </div>
        <div className="path-grid">
          <article className="path path-employee">
            <span>For Kairali employees</span>
            <h3>Company edition.</h3>
            <p>Includes the Kairali Setup Helper, employee role prompts, Daily Email, Full Drive Index, optional Saturday LinkedIn worker and governed opt-in skills.</p>
            <a href="/downloads/KAIRALI-AI-HUMAN-v202-EMPLOYEE-EDITION-PUBLIC-KIT.zip" download>Download Kairali employee edition</a>
          </article>
          <article className="path path-facilitator">
            <span>For everyone else</span>
            <h3>Reusable edition.</h3>
            <p>Contains only the company-neutral workspace, generic Setup Helper and reversible lifecycle controls. It is tested to contain no Kairali employee content.</p>
            <a href="/downloads/AI-HUMAN-v202-REUSABLE-EDITION-PUBLIC-KIT.zip" download>Download reusable edition</a>
          </article>
        </div>
      </section>

      <section className="install-flow" id="install" aria-labelledby="install-heading">
        <div className="section-intro">
          <p className="eyebrow">Install in five steps</p>
          <h2 id="install-heading">One action. One visible result.</h2>
          <p>No Terminal, PowerShell, Python, Git or typed command. The Setup Helper performs the internal work and gives you only an unavoidable click, login or permission.</p>
        </div>
        <div className="five-steps">
          <article><span>1</span><h3>Choose one edition.</h3><p>Click the Kairali employee download or reusable download above.</p><strong>DONE WHEN: the ZIP is in Downloads.</strong></article>
          <article><span>2</span><h3>Extract the ZIP.</h3><p>Mac: double-click the ZIP once. Windows: right-click it, select Extract All, then select Extract.</p><strong>DONE WHEN: the named edition folder appears.</strong></article>
          <article><span>3</span><h3>Open ChatGPT.</h3><p>Use the desktop app, sign in with the correct account and start a new chat.</p><strong>DONE WHEN: the new chat box is visible.</strong></article>
          <article><span>4</span><h3>Paste the Setup Helper message.</h3><p>It asks one question at a time for the exact company/entity, unit, jurisdictions, purpose, your relationship and compliance owner. It checks current sources before creating the working copy.</p><strong>DONE WHEN: Codex shows the correct local project and confirmed Gate 0 profile.</strong></article>
          <article><span>5</span><h3>Run the startup test.</h3><p>Paste the startup test from START-HERE.md. Change nothing until the identity, scope, Gate 0 and state readback is complete.</p><strong>DONE WHEN: the exact profile, ACTIVE and validator PASS are visible.</strong></article>
        </div>
        <div className="proof-banner"><strong>Installed is not enough.</strong><span>The final proof must name the exact legal entity, unit, jurisdictions, user relationship, compliance owner, purpose, Gate 0 profile/review date, version, actual mode and validator result.</span></div>
      </section>

      <section className="achievement-path" id="work-paths" aria-labelledby="work-paths-heading">
        <div className="section-intro">
          <p className="eyebrow">Fast for ordinary work</p>
          <h2 id="work-paths-heading">Use the smallest path that matches the effect.</h2>
          <p>v2.0.2 keeps real safety gates while removing ceremony from reading and reversible local work. A guardrail blocks only the conflicting part and helps the useful part finish.</p>
        </div>
        <div className="control-grid">
          <article><span>Read only</span><h3>Answer directly.</h3><p>A question or source review gets an answer without creating task state, facts, decisions or tool rows.</p><strong>PROOF: useful answer, no workspace diff.</strong></article>
          <article><span>Local reversible</span><h3>Create the requested result.</h3><p>A clear local file request uses standing worker-local permission. The lifecycle runs behind the scenes, reads back the artifact and keeps one usable undo.</p><strong>PROOF: artifact readback and validator PASS.</strong></article>
          <article><span>Mixed Gate 0</span><h3>Withhold narrowly.</h3><p>The worker reads the exact company gate, omits only the unsupported or unapproved part, finishes the safe local work and names the evidence or approval that would unblock the rest.</p><strong>PROOF: safe result exists; gated effect did not occur.</strong></article>
          <article><span>Assignment versus execution</span><h3>Count the real action.</h3><p>One document with 150 rows uploads intact as one artifact. Creating 150 GitHub issues is 150 external writes, so execution runs in batches of no more than 25 with a checkpoint between batches.</p><strong>PROOF: no truncated file and no hidden bulk execution.</strong></article>
        </div>
      </section>

      <section className="gate-profile" id="gate-profile" aria-labelledby="gate-profile-heading">
        <div className="section-intro">
          <p className="eyebrow">Gate 0 belongs to the exact company scope</p>
          <h2 id="gate-profile-heading">No universal compliance shortcut.</h2>
          <p>The shared system defines how gates are researched, confirmed, stored and enforced. The actual gates come from one private profile for the exact legal entity and work being set up.</p>
        </div>
        <div className="trouble-grid">
          <article><h3>1. Name the scope</h3><p>Company or group, exact legal entity, operating unit, jurisdictions, bounded purpose and your relationship to the company.</p></article>
          <article><h3>2. Check current authority</h3><p>Use current official or controlled authoritative sources. Historical charts and remembered rules are only unverified leads.</p></article>
          <article><h3>3. Define each stop</h3><p>Every gate names an ID, trigger, required action, source, approval owner and evidence needed.</p></article>
          <article><h3>4. Confirm it</h3><p>The named compliance owner reviews the proposed profile. Unanswered compliance questions block ACTIVE.</p></article>
          <article><h3>5. Keep scopes separate</h3><p>Different companies, or materially different entities, units, jurisdictions or purposes, use separate worker folders and profiles.</p></article>
          <article><h3>6. Verify every session</h3><p>The validator catches identity mismatch, overdue review, profile tampering and edited gate/source views.</p></article>
        </div>
        <p className="separation-note"><strong>Important:</strong> historical operations charts can help discover questions. They are not proof of current legal, certification, registration, tax, clinical or other compliance status.</p>
      </section>

      <section className="file-ownership" id="files" aria-labelledby="files-heading">
        <div className="section-intro">
          <p className="eyebrow">One kind of data, one file of record</p>
          <h2 id="files-heading">Know exactly where “done” lives.</h2>
          <p>The installed workspace includes a complete WORKSPACE-MAP.md. This is the short version.</p>
        </div>
        <div className="file-map-table">
          <table>
            <thead><tr><th scope="col">What</th><th scope="col">File of record</th><th scope="col">What it stores</th></tr></thead>
            <tbody>
              <tr><th scope="row">Identity and scope</th><td><code>COMPANY.md</code><br/><code>PARAMETERS.md</code><br/><code>ROLE.md</code></td><td>Exact company/entity/unit/jurisdictions, user relationship, purpose, responsibilities and exclusions.</td></tr>
              <tr><th scope="row">Storage map</th><td><code>WORKSPACE-MAP.md</code></td><td>The authoritative map that names which file owns each durable kind of information.</td></tr>
              <tr><th scope="row">Active Gate 0 and work locks</th><td><code>.ai-human/control/gate-profile.json</code><br/><code>GATES.md</code><br/><code>WORK-GATES.md</code><br/><code>COMPLIANCE-SOURCES.md</code></td><td>The machine profile, its generated human-readable gates and sources, plus separate task-specific operating locks that may narrow but never replace Gate 0.</td></tr>
              <tr><th scope="row">Truth and rulings</th><td><code>FACTS.md</code><br/><code>DECISIONS.md</code></td><td>Verified operational facts versus owner/compliance-owner decisions and supersession.</td></tr>
              <tr><th scope="row">Tools and unattended work</th><td><code>TOOLBOX.md</code><br/><code>AUTOMATIONS.md</code></td><td>Allowed tools/permissions and separately approved automations. Never credentials.</td></tr>
              <tr><th scope="row">Current and queued work</th><td><code>MASTER_CURSOR.md</code><br/><code>OPEN_REGISTER.md</code><br/><code>TODAY.md</code></td><td>The one live task, the backlog and today&apos;s bounded working set.</td></tr>
              <tr><th scope="row">Completion proof</th><td><code>COMPLETED_LEDGER.md</code><br/><code>EVIDENCE_LOG.md</code></td><td>The completion index plus detailed checks, result, artifact/readback and undo evidence.</td></tr>
              <tr><th scope="row">Shared system</th><td><code>.ai-human/system/</code><br/><code>AGENTS.md</code> and adapters</td><td>Managed shared rules and local onboarding adapters, not company facts, user state or secrets.</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="lifecycle-control" id="control" aria-labelledby="control-heading">
        <div className="section-intro">
          <p className="eyebrow">You stay in control</p>
          <h2 id="control-heading">Pause it, restore it or remove it.</h2>
          <p>The local system and external account access are separate. Choose the smallest action that matches what you want.</p>
        </div>
        <div className="active-guidance">
          <span>When ACTIVE</span>
          <h3>Polite pushback, then a useful path forward.</h3>
          <p>If a request crosses a declared boundary, the AI names it briefly, refuses only the conflicting part, preserves safe work and offers the nearest compliant next step or exact approval needed. It does not scold, lecture or turn one guardrail into a broad ban.</p>
        </div>
        <div className="control-grid">
          <article><span>Temporary</span><h3>Suspend</h3><p>Turns managed rules, automations and automatic updates off. Project files and account connections stay.</p><code>Temporarily suspend this AI-human system, preserve my files, then verify SUSPENDED with PASS.</code><strong>DONE WHEN: rules OFF, updates DISABLED.</strong></article>
          <article><span>Reversible</span><h3>Resume</h3><p>Turns the system back on and restores the automatic-update setting that existed before suspension.</p><code>Resume this AI-human system, then verify ACTIVE with PASS.</code><strong>DONE WHEN: rules ON, validator PASS.</strong></article>
          <article><span>Project</span><h3>Uninstall</h3><p>Archives <code>.ai-human</code> and its active local adapters. It preserves work files and does not delete the project.</p><code>Reversibly uninstall this AI-human system, preserve my work, then verify UNINSTALLED with PASS.</code><strong>DONE WHEN: system and adapters are absent.</strong></article>
          <article><span>Accounts</span><h3>Revoke access</h3><p>Open Plugins, use Installed, open the plugin and choose Uninstall plugin. Disconnect its connector separately. Review Computer Use permissions too.</p><a href="https://learn.chatgpt.com/docs/plugins" target="_blank" rel="noreferrer">Official plugin instructions</a><strong>DONE WHEN: a new chat cannot use that access.</strong></article>
        </div>
        <p className="separation-note"><strong>Important:</strong> suspend or uninstall does not disconnect Gmail, Drive, GitHub or computer permissions. Plugin uninstall can also leave its connector connected until that connection is managed separately.</p>
      </section>

      <section className="troubleshooting" id="troubleshooting" aria-labelledby="troubleshooting-heading">
        <div className="section-intro">
          <p className="eyebrow">Troubleshooting</p>
          <h2 id="troubleshooting-heading">Do not guess or reinstall repeatedly.</h2>
          <p>At the first failure, paste the complete Setup Helper message from your edition and add the exact visible error. It gives one action at a time and verifies the result.</p>
        </div>
        <div className="trouble-grid">
          <article><h3>ZIP does not open</h3><p>On Windows, select Extract All instead of opening files inside the compressed folder. On Mac, double-click the ZIP once. If that fails, keep it, download once more and let the helper compare the visible filename and checksum.</p></article>
          <article><h3>Codex cannot see files</h3><p>Make the extracted working folder the local project, not the ZIP or untouched source folder.</p></article>
          <article><h3>It says local candidate</h3><p>Stop. The package is not released and must not be installed for real work.</p></article>
          <article><h3>Suspend still feels restrictive</h3><p>Start a new chat in the same project and verify SUSPENDED. A stale chat is not proof.</p></article>
          <article><h3>Uninstall left instructions</h3><p>Verify UNINSTALLED. Any active AI-human adapter means removal failed and must be recovered from the receipt.</p></article>
          <article><h3>Plugin removed, account remains</h3><p>Disconnect the connector separately. Plugin removal alone is not account-access revocation.</p></article>
        </div>
      </section>

      <section className="workers" id="workers" aria-labelledby="workers-heading">
        <div className="section-intro">
          <p className="eyebrow">Kairali employee edition only</p>
          <h2 id="workers-heading">Available here. Live only after your proof.</h2>
          <p>Use the Setup Helper. The portal makes the approved starters available. It does not connect your accounts, choose your times or activate a worker. Each employee completes this readback in three separate local projects.</p>
        </div>
        <div className="worker-grid">
          <article>
            <span className="worker-status">Required</span>
            <h3>Daily Email Triage</h3>
            <p>The daily Email Importance Brief is live only after the approved Gmail account, daily time and time zone, read-only pilot, filing-mode ruling, automation card and validator agree. Then mark <strong>LIVE FOR ME</strong>.</p>
          </article>
          <article>
            <span className="worker-status">Required</span>
            <h3>Full Drive Index</h3>
            <p>Mark <strong>LIVE FOR ME</strong> only after every supported scope ends in checkpointed batches, and the CSV, summary, final cursor and validator agree. <strong>TEST 25 proves setup only.</strong></p>
          </article>
          <article>
            <span className="worker-status worker-status-optional">Optional</span>
            <h3>Saturday LinkedIn Message Assistant</h3>
            <p>If chosen, prove the schedule, right-level local control, <strong>YOUR TURN ON LINKEDIN</strong> handoff, manually supplied pilot and local queue. Otherwise record <strong>NOT ENABLED BY CHOICE</strong>.</p>
          </article>
        </div>
        <p className="worker-note">Downloaded, installed or connected alone does not mean live. Show the local report, cursor, evidence and validator.</p>
      </section>

      <section className="update-flow" id="updates" aria-labelledby="updates-heading">
        <div className="section-intro">
          <p className="eyebrow">Managed updates</p>
          <h2 id="updates-heading">A new release starts with a check, not an overwrite.</h2>
          <p>The release notice names the version and affected files. Open the existing worker and ask the Setup Helper to check. The check is read-only; applying waits for your approval at a safe checkpoint.</p>
        </div>
        <div className="update-steps">
          <article>
            <span>1</span>
            <h3>Open the existing worker.</h3>
            <p>Kairali users paste <strong>CHECK FOR KAIRALI UPDATE</strong>. Reusable users paste <strong>CHECK FOR AI-HUMAN UPDATE</strong>. You never type a command.</p>
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
            <h3>Prove the exact worker.</h3>
            <p>A configured v2.0.0 or held v2.0.1 worker moves to v2.0.2 with user-owned state preserved. A pre-v2 worker completes the guided Gate 0 migration first. Keep the version, validation receipt and preserved-state proof.</p>
          </article>
        </div>
        <div className="update-boundary">
          <p><strong>Automatic:</strong> the stable portal follows the approved release and a session may check for a newer version.</p>
          <p><strong>Manual:</strong> the user approves the apply. GitHub Desktop Fetch/Pull synchronizes only the selected repository; it does not install this managed update.</p>
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
            <h2 id="downloads-heading">Two editions, then supporting Kairali files.</h2>
            <p>Choose exactly one edition ZIP first. The remaining presentation, homework and facilitator files below belong to the Kairali training path.</p>
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
          <p>v2.0.2 is the approved public release. Its exact source, checksums and release evidence are published together. Fetch/Pull updates a repository checkout, not an installed worker; configured v2.0.0 or held v2.0.1 workers use the checked correction path and pre-v2 workers use the guided migration.</p>
        </div>
        <div className="technical-links">
          <a href={assetLink(release, "ai-human-workspace-")} target="_blank" rel="noreferrer">
            <span>Workspace core</span>
            <strong>Download latest approved ZIP</strong>
          </a>
          <a href={assetLink(release, "kairali-company-rollout-")} target="_blank" rel="noreferrer">
            <span>Company kit and opt-in skills</span>
            <strong>Download latest approved ZIP</strong>
          </a>
          <a href="https://github.com/kairali-digital/ai-human-workspace" target="_blank" rel="noreferrer">
            <span>Public repository</span>
            <strong>Review source and release history</strong>
          </a>
        </div>
      </section>

      <section className="update-policy" aria-labelledby="policy-heading">
        <h2 id="policy-heading">How the single link stays safe.</h2>
        <div className="policy-grid">
          <article>
            <h3>Amend in GitHub</h3>
            <p>Update the governed source and regenerate affected presentation or homework files.</p>
          </article>
          <article>
            <h3>Validate the release</h3>
            <p>Automated gates check the workspace, downloads, canonical indexing controls and production build.</p>
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
        <p>Public v2.0.2. Choose one edition, verify setup, and keep company Gate 0 profiles isolated.</p>
        <a href="#troubleshooting">Stuck? Start with troubleshooting.</a>
      </footer>
    </main>
  );
}
