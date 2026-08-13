#!/usr/bin/env python3
"""Build the narrated, captioned beginner homework video from safe title cards."""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[5]
TMP = WORKSPACE / "tmp" / "H-39-THREE-WORKER-LIVE" / "video-build"
OUTPUT = ROOT / "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO.mp4"
TRANSCRIPT = ROOT / "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO-TRANSCRIPT.txt"
SRT = ROOT / "EVERYONE-ELSE-AI-HUMAN-HOMEWORK-VIDEO-CAPTIONS.srt"
CONTACT_SHEET = TMP / "contact-sheet.png"

WIDTH, HEIGHT = 1920, 1080
NAVY = "#0B2545"
BLUE = "#2E74B5"
GOLD = "#B57A16"
INK = "#1F2937"
MUTED = "#667085"
PALE_BLUE = "#E8EEF5"
PALE_GOLD = "#FFF4D6"
WHITE = "#FFFFFF"
BG = "#F7F8FA"

FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_MONO = "/System/Library/Fonts/SFNSMono.ttf"

SCENES = [
    {
        "title": "No named homework page? Start here.",
        "label": "WHO THIS IS FOR",
        "actions": ["Required 01  ·  Email Triage", "Required 02  ·  Drive Inventory", "Optional 03  ·  Saturday LinkedIn Assistant"],
        "done": "All three are available; none is live for you until its proof passes.",
        "narration": "This is the homework for anyone from the meeting who did not receive a named start or homework page. The kit makes three starters available, but it does not activate your accounts or schedules. Email Triage and Full Drive Index are required. The Saturday LinkedIn Message Assistant is optional after both are complete.",
    },
    {
        "title": "See the whole loop first",
        "label": "THE OUTSKILL-STYLE LOOP",
        "actions": ["Find pack  →  copy one starter folder", "Open it as one local project  →  connect one app", "Paste prompt  →  show report  →  verify the daily job"],
        "done": "A visible result, active automation and validator pass are the finish line.",
        "narration": "Here is the whole loop before we begin. Find the pack. Copy one starter folder. Open that folder as its own local project. Connect only the app it needs. Paste the exact prompt. For Email, choose your daily time, prove the pilot and verify the daily automation. Stop when the result and validator pass are visible.",
    },
    {
        "title": "Keep the homework safe",
        "label": "SAFETY PROMISE",
        "actions": ["No Terminal  ·  No typed commands", "No Full access  ·  No password or one-time code", "No send, delete, attachment or silent Gmail filter change"],
        "done": "Ask for approval remains selected.",
        "narration": "You do not use Terminal or type commands. Keep Ask for approval. Never choose Full access or Always allow. Login happens on the provider screen. Never paste a password or one-time code into chat. Email begins with a read-only pilot. Later safe filing needs your approval and never sends, deletes or changes a permanent Gmail filter. Drive stays unchanged. For LinkedIn, Computer control may help inside the local project, but it stops before LinkedIn appears. You manually paste message text, review every draft and manually press Send.",
    },
    {
        "title": "If any screen looks different, stop",
        "label": "FIRST RESCUE",
        "actions": ["Open a normal ChatGPT chat", "Open COPY-PASTE-PROMPTS.txt", "Paste PROMPT 0 in full"],
        "done": "The helper gives one action, waits, then verifies it.",
        "narration": "If any button, app or folder is missing, stop. Open a normal Chat G P T chat. Open the prompt file in the pack. Copy Prompt Zero, the complete Setup Helper rescue. The helper gives you one action, waits, and verifies it before continuing.",
    },
    {
        "title": "Open the homework pack",
        "label": "ONE VISIBLE ACTION AT A TIME",
        "actions": ["Mac  ·  Finder  →  Downloads  →  double-click ZIP", "Windows  ·  File Explorer  →  Downloads", "Right-click ZIP  →  Extract All"],
        "done": "The normal folder shows the guide and AI-HUMAN-STARTERS.",
        "narration": "On a Mac, open Finder, click Downloads and double-click the zip. On Windows, open File Explorer, click Downloads, right-click the zip and choose Extract All. Done when the normal folder shows the guide and A I Human Starters.",
    },
    {
        "title": "Copy the two required starter folders",
        "label": "DOCUMENTS  ›  AI HUMANS",
        "actions": ["Make a folder named AI Humans", "Copy starter 01  ·  Email Triage", "Copy starter 02  ·  Drive Inventory"],
        "done": "The two copied folders sit beside each other.",
        "narration": "Inside Documents, make one folder named A I Humans. Copy starter zero one, Email Triage, into it. Then copy starter zero two, Drive Inventory, beside it. Keep the downloaded pack untouched. Done when the two copied folders are separate.",
    },
    {
        "title": "Open Email Triage in ChatGPT",
        "label": "PROJECT 01",
        "actions": ["Check whether the desktop app is already installed", "Open ChatGPT  →  Codex  →  Open folder", "Choose Documents  ›  AI Humans  ›  01 Email"],
        "done": "The Email project can see AGENTS.md.",
        "narration": "Check whether the Chat G P T desktop app is already installed. If it is, open it. Do not install it again. Choose Codex, open a folder, and select the Email Triage folder. Keep Ask for approval. Done when the Email project can see A G E N T S dot M D.",
    },
    {
        "title": "Connect only Gmail",
        "label": "CHECK  →  CONNECT IF NEEDED",
        "actions": ["Settings  →  Apps  →  Gmail", "Connect only if it is not connected  →  start a new chat", "Choose only the approved company account"],
        "done": "Codex verifies the Gmail connection.",
        "narration": "Open Settings, then Apps, and select Gmail. If it is already connected, return to the Email project. If it is not connected, choose Connect and complete the provider screen, then start a new chat in the Email project. Choose only the approved company account. Done when Codex verifies the connection.",
    },
    {
        "title": "Choose the time and run the Email pilot",
        "label": "PROMPT 1",
        "actions": ["Copy PROMPT 1  →  replace the name box  →  paste", "Answer: what local time should the daily brief run?", "Confirm time zone  →  run the read-only 25-message pilot"],
        "done": "EMAIL-TRIAGE-REPORT.md shows the read-only pilot.",
        "narration": "Open the prompt file. Copy all of Prompt One, replace the name box and paste it into the Email project. Do not shorten it. Codex asks what local time you want the daily brief and confirms the computer's time zone. It then runs a read-only pilot of no more than twenty-five Inbox messages. Done when the Email Triage Report is visible.",
    },
    {
        "title": "Approve and activate the daily brief",
        "label": "CONNECTED IS NOT DONE",
        "actions": ["Review the report + exact safe-filing rules", "Choose BRIEF ONLY or BRIEF + SAFE FILING", "Verify automation time + time zone + project + prompt"],
        "done": "The report and active Daily Email Importance Brief are visible.",
        "narration": "Read the pilot report and the safe filing rules. Choose Brief Only or Brief plus Safe Filing. Safe filing uses approved A I labels only; it never deletes, sends, unsubscribes or changes permanent Gmail filters. Codex then creates one daily Email Importance Brief at your chosen local time. Verify the automation card, time zone, Email project and prompt. The computer must be awake with Chat G P T running when the job is due.",
    },
    {
        "title": "Open Drive as a separate project",
        "label": "PROJECT 02",
        "actions": ["Add local project", "Choose Documents  ›  AI Humans  ›  02 Drive", "Start a new chat inside the Drive project"],
        "done": "Email and Drive appear as separate projects.",
        "narration": "Now add the Drive Inventory folder as a second local project. Do not add it to the Email project. Start a new chat inside the Drive project. Done when Email and Drive appear as separate projects.",
    },
    {
        "title": "Connect Drive and run Prompt 2",
        "label": "CHECK  →  CONNECT IF NEEDED",
        "actions": ["Settings  →  Apps  →  Google Drive", "Connect the approved company account only if needed", "PROMPT 2  ·  TEST 25 setup or FULL DRIVE homework"],
        "done": "TEST 25 proves setup; FULL DRIVE completes homework; every batch is at most 25.",
        "narration": "Open Settings, then Apps, and select Google Drive. If it is not connected, choose Connect and use the approved company account. Copy all of Prompt Two, replace the name box, and paste it into the Drive project. Test Twenty Five proves setup only. Choose Full Drive Index to complete the company homework. Every batch is no more than twenty-five items and ends with a saved checkpoint.",
    },
    {
        "title": "Check Drive proof",
        "label": "RESUMABLE METADATA INDEX",
        "actions": ["DRIVE-INDEX.csv + summary + cursor are visible", "Every batch ≤ 25  ·  IDs prevent duplicates", "Drive unchanged  ·  scope coverage recorded"],
        "done": "Full mode ends only when every supported scope has no next page.",
        "narration": "The Drive project creates a CSV index, a summary and a saved cursor. Test Twenty Five stops after one batch and says the full Drive was not indexed. Full Drive Index continues in checkpointed batches until every connector-visible scope has no next page. Missing facts say Unknown. Sensitive titles say Human Review. No file content is opened and Drive is not changed.",
    },
    {
        "title": "Optional: set up Saturday LinkedIn review",
        "label": "ONLY AFTER BOTH REQUIRED PROJECTS PASS",
        "actions": ["Copy starter 03  →  open it as a separate project", "Paste PROMPT 3  →  choose Saturday time + confirm time zone", "Close LinkedIn  ·  @Computer  ·  approve only this local task"],
        "done": "Codex names the handoff file; LinkedIn is outside the grant.",
        "narration": "The LinkedIn project is optional. Do it only after Email and Drive pass. Copy starter zero three, open it separately, and paste Prompt Three. Choose the local Saturday time and confirm the time zone. Close every LinkedIn tab. Choose Computer from the at tools menu and approve only this local project and current task. Keep Ask for approval. Never choose Full access or Always allow.",
    },
    {
        "title": "Prove the LinkedIn handoff",
        "label": "CONTROL STOPS BEFORE LINKEDIN",
        "actions": ["Codex stops Computer + Chrome", "YOUR TURN ON LINKEDIN  ·  you copy no more than 25", "Close LinkedIn  ·  return  ·  say BATCH READY"],
        "done": "The employee supplied the batch; no AI LinkedIn action occurred.",
        "narration": "Before LinkedIn opens, Codex stops Computer and Chrome control and shows Your Turn on LinkedIn. You alone open LinkedIn, check Focused and Other, copy no more than twenty-five conversations, close LinkedIn, return to the local project and say Batch Ready. While LinkedIn is visible, Codex does not inspect the screen, move the mouse, type, read, copy, paste, click or send.",
    },
    {
        "title": "Run the supervised Saturday review",
        "label": "LOCAL DRAFTS  ·  HUMAN LINKEDIN ACTIONS",
        "actions": ["Codex separates READY TO SEND from NEEDS YOUR DECISION", "Codex stops Computer + Chrome again", "You review + manually send  →  confirm every outcome"],
        "done": "The numbered queue is saved; Codex never accesses or sends through LinkedIn.",
        "narration": "After Batch Ready, Codex processes only the local text you supplied. It prepares routine drafts and keeps uncertain replies in a numbered decision queue. It stops Computer and Chrome again. You review every draft, manually paste and press Send in LinkedIn, close LinkedIn, then return and confirm what you sent, edited, skipped or kept.",
    },
    {
        "title": "Check what is live for you",
        "label": "THREE-WORKER GO-LIVE READBACK",
        "actions": ["Email  ·  LIVE FOR ME or exact blocker", "Full Drive  ·  LIVE FOR ME or exact blocker", "LinkedIn  ·  OPTIONAL LIVE, NOT ENABLED, or blocker"],
        "done": "Available in the kit is not live until the named proof passes.",
        "narration": "Bring the laptop or safe screenshots showing the Email report and active daily automation, plus the completed Full Drive Index, final cursor, evidence rows and validator passes. Test Twenty Five proves Drive setup only; it does not complete the company homework. Optional LinkedIn proof shows only the schedule, counts, queue headings and employee-confirmed outcomes, not message bodies. If you decline LinkedIn, record Not Enabled By Choice. Do not expose private content, passwords, codes, H R information or banking information.",
    },
    {
        "title": "Mission + judgment = you",
        "label": "YOUR AI HUMAN",
        "actions": ["Codex performs only the approved bounded work", "Start with Email  →  prove the daily brief", "Then build Drive  →  optional human-send LinkedIn comes last"],
        "done": "Two required live proofs and one optional status complete the readback.",
        "narration": "You provide the mission and judgment. Codex performs the approved work inside the boundaries. Start with Email and prove the daily automation. Then complete Full Drive Index. Add the Saturday LinkedIn assistant only if you choose it: task scoped control for the local worker, then human only LinkedIn access and sending. Finish with the three line go live readback.",
    },
]


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(path, size=size)


def wrap_pixels(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=face)[2] <= max_width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, face: ImageFont.FreeTypeFont,
                 fill: str, max_width: int, spacing: int = 10, max_lines: int | None = None) -> int:
    lines = wrap_pixels(draw, text, face, max_width)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    x, y = xy
    line_height = face.size + spacing
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += line_height
    return y


def render_scene(index: int, scene: dict[str, object], output: Path) -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH, 16), fill=GOLD)
    draw.text((112, 65), "KAIRALI AI METHOD", font=font(28, bold=True), fill=NAVY)
    draw.text((1580, 66), f"{index:02d} / {len(SCENES):02d}", font=font(25, mono=True), fill=MUTED)

    draw.rounded_rectangle((112, 130, 550, 186), radius=12, fill=PALE_BLUE)
    draw.text((138, 144), str(scene["label"]), font=font(24, bold=True), fill=BLUE)
    draw_wrapped(draw, (112, 218), str(scene["title"]), font(62, bold=True), NAVY, 1660, spacing=8, max_lines=2)

    y = 390
    for number, action in enumerate(scene["actions"], 1):
        draw.rounded_rectangle((112, y, 1808, y + 88), radius=16, fill=WHITE, outline="#D6DAE1", width=2)
        draw.ellipse((138, y + 20, 186, y + 68), fill=BLUE)
        num = str(number)
        bbox = draw.textbbox((0, 0), num, font=font(25, bold=True))
        draw.text((162 - (bbox[2] - bbox[0]) / 2, y + 27), num, font=font(25, bold=True), fill=WHITE)
        draw.text((216, y + 24), str(action), font=font(34, bold=True), fill=INK)
        y += 106

    done_y = 724
    draw.rounded_rectangle((112, done_y, 1808, done_y + 96), radius=18, fill=PALE_GOLD, outline="#E5C783", width=2)
    draw.text((142, done_y + 29), "DONE WHEN", font=font(28, bold=True), fill=GOLD)
    draw.text((366, done_y + 27), str(scene["done"]), font=font(32, bold=True), fill=NAVY)

    draw.rectangle((0, 866, WIDTH, HEIGHT), fill=NAVY)
    draw.text((112, 895), "NARRATION / CAPTIONS", font=font(21, bold=True), fill="#90B9E0")
    draw_wrapped(draw, (112, 932), str(scene["narration"]), font(27), WHITE, 1696, spacing=8, max_lines=3)
    image.save(output, quality=95)


def run(args: list[str]) -> None:
    subprocess.run(args, check=True)


def media_duration(ffmpeg: str, media: Path) -> float:
    result = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(media)],
        check=False,
        text=True,
        capture_output=True,
    )
    match = re.search(r"Duration:\s+(\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    if not match:
        raise RuntimeError(f"Could not read duration for {media}")
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def srt_time(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_contact_sheet(frames: list[Path]) -> None:
    thumb_w, thumb_h = 480, 270
    rows = (len(frames) + 3) // 4
    sheet = Image.new("RGB", (thumb_w * 4, thumb_h * rows), WHITE)
    for index, frame in enumerate(frames):
        shot = Image.open(frame).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(shot, ((index % 4) * thumb_w, (index // 4) * thumb_h))
    sheet.save(CONTACT_SHEET, quality=92)


def build() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    dependency_dir = WORKSPACE / "tmp" / "H-38-RIGHT-LEVEL-ACCESS" / "python-deps"
    sys.path.insert(0, str(dependency_dir))
    import imageio_ffmpeg  # type: ignore

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    frames: list[Path] = []
    segments: list[Path] = []
    durations: list[float] = []

    for index, scene in enumerate(SCENES, 1):
        frame = TMP / f"scene-{index:02d}.png"
        audio = TMP / f"scene-{index:02d}.aiff"
        segment = TMP / f"scene-{index:02d}.mp4"
        render_scene(index, scene, frame)
        run(["/usr/bin/say", "-v", "Aman", "-r", "155", "-o", str(audio), str(scene["narration"])])
        run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-loop", "1", "-framerate", "1", "-i", str(frame), "-i", str(audio),
            "-filter_complex", "[1:a]apad=pad_dur=0.8[a]", "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-tune", "stillimage", "-preset", "medium", "-r", "30",
            "-c:a", "aac", "-b:a", "160k", "-pix_fmt", "yuv420p", "-shortest", str(segment),
        ])
        frames.append(frame)
        segments.append(segment)
        durations.append(media_duration(ffmpeg, segment))

    concat_file = TMP / "segments.txt"
    concat_file.write_text("".join(f"file '{segment.name}'\n" for segment in segments), encoding="utf-8")
    run([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file), "-c", "copy", "-movflags", "+faststart", str(OUTPUT),
    ])

    transcript_lines = [
        "EVERYONE ELSE AI-HUMAN HOMEWORK - VIDEO TRANSCRIPT",
        "GENERAL-AI-HUMAN-HOMEWORK-001",
        "",
        "This transcript matches the narrated title-card video. No private employee data appears.",
        "",
    ]
    srt_lines: list[str] = []
    cursor = 0.0
    for index, (scene, duration) in enumerate(zip(SCENES, durations), 1):
        title = str(scene["title"])
        narration = str(scene["narration"])
        transcript_lines.extend([f"SCENE {index}: {title}", narration, f"DONE WHEN: {scene['done']}", ""])
        srt_lines.extend([str(index), f"{srt_time(cursor)} --> {srt_time(cursor + duration)}", narration, ""])
        cursor += duration
    TRANSCRIPT.write_text("\n".join(transcript_lines).rstrip() + "\n", encoding="utf-8")
    SRT.write_text("\n".join(srt_lines).rstrip() + "\n", encoding="utf-8")
    build_contact_sheet(frames)
    print(f"Video: {OUTPUT}")
    print(f"Duration: {cursor:.1f} seconds")
    print(f"Transcript: {TRANSCRIPT}")
    print(f"Captions: {SRT}")
    print(f"Contact sheet: {CONTACT_SHEET}")


if __name__ == "__main__":
    build()
