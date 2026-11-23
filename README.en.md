# Revisión impecable ("flawless review")

English · [Español](README.md)

A Claude Code skill that reviews, tests and polishes any running web page or app. Like having a team of testers,
designers and developers go over everything, even overnight while you sleep.

It is not a linter or a list of best practices. It is a procedure:

1. **A script measures** whatever needs no judgment: contrast, touch-target size, small text, overflow, clipping,
   overlaps, native (factory) controls, glyphs used as icons, invisible focus, half-applied themes, console errors, and
   **how many different shapes each component has across the whole app** (the button that looks different in every
   sub-app). At 4 widths and 2 themes, in minutes.
2. **Parallel reviewers** cover what needs judgment: driving each feature end to end like a user (with the saved data
   as proof), design against Apple's rules, keyboard and screen readers, copy, edge states, data and permissions.
3. **Every finding is refuted** before it is accepted.
4. **Fixes land in the shared place**, so the change holds on every screen and sub-app, then everything is measured again.
5. **Every error becomes a check** that fails if it comes back.
6. **It learns from what it missed**, reading git history.

> The skill itself (its prompts, checks and invocation phrases such as "revisá todo") is written in Spanish, the language
> it reviews in. It is meant for apps in any language, but the skill's own text and its trigger phrases are Spanish.
> If you need English trigger phrases, ask for it by name: `/revision-impecable`.

## Requirements

- [Claude Code](https://claude.com/claude-code) (the skill loads from `~/.claude/skills/`).
- A recent Python 3 (tested with 3.14), `pip` and `git`.
- Playwright (`pip install -r skill/scripts/requirements.txt`) and a browser: Playwright's Chromium
  (`python -m playwright install chromium`) or, if you did not download it, the Chrome installed on the machine.
- An app you can start locally with **test** data (the skill never touches production).
- Windows, macOS or Linux.

## Try it in 5 minutes

There is a minimal project in [`ejemplos/proyecto-minimo/`](ejemplos/proyecto-minimo/): a page with a small button, a
native `<select>`, 12 px text and a low-contrast grey. It ships with its adapter (`.claude/revision/proyecto.json`).

1. Install the skill and dependencies (next section).
2. Run only the measurement, without Claude, from the root of this repo:

```bash
python skill/scripts/medir.py --config ejemplos/proyecto-minimo/.claude/revision/proyecto.json --rapido
```

   It starts `app.py` on port 8090, opens a headless browser, measures at 390 and 1366 px in light and dark, and writes
   `informe.md`, `informe.json` and screenshots under `ejemplos/proyecto-minimo/.claude/revision/salida/<date>/`. Expect
   about **36 measurements** grouped into four defects (contrast, native control, touch target, small text). The report
   is explained in [`ejemplos/informe-ejemplo-v2.md`](ejemplos/informe-ejemplo-v2.md) (in Spanish).
3. The full review, with reviewers and fixes: open Claude Code **inside `ejemplos/proyecto-minimo/`** and ask
   `revisá todo` (or `/revision-impecable`). It uses the adapter that is already there.

In your own project you do not write the adapter by hand: the first time, the skill generates it by reading your repo
(`skill/references/adaptador.md`) and only asks what it cannot observe.

## Install

Clone and **link** the `skill/` folder into your Claude Code skills. With a link (not a copy), `git pull` brings
everything the skill has learned.

**macOS / Linux**

```bash
git clone https://github.com/migueedlsantos97/revision-impecable ~/revision-impecable
mkdir -p ~/.claude/skills
ln -s ~/revision-impecable/skill ~/.claude/skills/revision-impecable
pip install -r ~/revision-impecable/skill/scripts/requirements.txt
python -m playwright install chromium
```

**Windows, no administrator needed (junction), in `cmd`**

```bat
git clone https://github.com/migueedlsantos97/revision-impecable "%USERPROFILE%\revision-impecable"
mkdir "%USERPROFILE%\.claude\skills"
mklink /J "%USERPROFILE%\.claude\skills\revision-impecable" "%USERPROFILE%\revision-impecable\skill"
pip install -r "%USERPROFILE%\revision-impecable\skill\scripts\requirements.txt"
python -m playwright install chromium
```

**Windows with a symbolic link** (PowerShell as administrator, or with Developer Mode on):

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\revision-impecable" -Target "$env:USERPROFILE\revision-impecable\skill"
```

**No links (any OS)**: copy the `skill/` folder to `~/.claude/skills/revision-impecable`. Simplest, but you have to copy
it again to update.

It loads in the next session. Then just ask: `revisá todo antes de mostrárselo al cliente` ("review everything before
showing it to the client"), or invoke `/revision-impecable`. For overnight: `revisá todo y dejalo corriendo toda la noche`.

### Update and uninstall

- **Update**: `git -C ~/revision-impecable pull` (Windows: `git -C "%USERPROFILE%\revision-impecable" pull`). With a link,
  every project is up to date. Check [`CHANGELOG.md`](CHANGELOG.md) in case the adapter format changed.
- **Uninstall**: remove the link, not its target: `rm ~/.claude/skills/revision-impecable` (macOS/Linux) or
  `rmdir "%USERPROFILE%\.claude\skills\revision-impecable"` (Windows; for a junction this only removes the link). Delete
  the clone if you want. Your projects' adapters (`.claude/revision/`) are yours and stay.

## What it runs and what it touches

Read this before installing: the skill **runs code and opens a browser** against your app.

- **Runs** `skill/scripts/medir.py` (Python + Playwright) and the start command from your project's adapter, to bring up
  a **test** instance. It opens a browser (headless by default) and walks the screens listed in the adapter. The
  reviewers Claude dispatches read your code and drive that instance.
- **Writes** only inside your project: `.claude/revision/` (adapter, and measurements in `salida/`, which you should
  git-ignore), `docs/revision-<date>.md` (the report) and the fixes in your code. In accompanied mode it shows big design
  changes before applying them.
- **Night mode**: works on its **own branch**, without asking. It never pushes to the main branch or force-pushes, never
  deploys, never writes to production, never uses real data, never deletes the person's data, never kills processes by
  name (only the ones the run started), and never writes secrets into the repo.
- **Network**: only GET reads of public sites (outgoing links, headers, `robots.txt`). The skill does not send your code
  or data to any service of its own; what Claude sees depends on the terms you already have with Claude Code.
- If your app only starts against real data, the skill **stops** and tells you what is missing instead of making
  something up.

## What it reviews

| | Who | Looks for |
|---|---|---|
| 0 | `scripts/medir.py` | everything measurable, at 390/768/1366/1920 and light/dark, and the shapes of each component across screens and sub-apps |
| 1 | Functions | each feature in the map, end to end, with the real effect as proof |
| 2 | Design and consistency | screenshots against Apple's rules, the project's references, and each other |
| 3 | Controls, keyboard, screen readers | what the system draws and what cannot be done without a mouse |
| 4 | Copy | two names for the same thing |
| 5 | Edge states and widths | empty, error, slow, overflowing, between breakpoints |
| 6 | Data, permissions, security | who can do what, what is lost, what is duplicated |
| 7 | Public web (if it is one) | Safari, performance, how it is shared, images |

## The problem it came from

A single reviewer, however careful, carries blind spots: they accept what they decided two hours ago. In the project
where this skill was born, a separate accessibility reviewer found that a "how we use your data" button lived inside
the consent checkbox's `<label>`, so a screen reader read both as one sentence. The same finding also claimed that
activating the button toggled the checkbox; that was false, and was reported as the worst issue until someone tried to
reproduce it. That is why every finding goes through a refutation step: more reviewers without refutation is only more
noise.

## How it learns

The measure of whether the skill works is not how many findings it produced. It is how many **escapes** there were:
defects someone found *after* the review said "done". Each run starts by looking for the previous run's escapes in git
history (`git log --oneline --since="<previous review date>" -- <paths it covered>`); any later commit that fixes
something the review should have caught is an escape.

Then the last step answers five questions by name, and **applies** the changes rather than proposing them: which
reviewer should have caught each escape, which false positive a badly worded brief induced, which check has not fired in
three runs, which technique was improvised, and which reviewer delivered little because its brief was vague. A check that
does not fire for three consecutive runs is deleted, with a note on why, so the skill sharpens instead of bloating.
Checks that came from an escape carry the mark `[caso real]` ("real case").

What is specific to a project stays in the project. What is useful for any app only enters this skill with an invented
minimal case and after passing the privacy filter: see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Does it work? The evals

`evals/` has two sets of cases with seeded defects: the three original pages (`a/b/c`, the measurable stuff) and the
`casos-v2/` cases D to J (functions, permissions, keyboard and screen readers, copy and regional data, consistency across
sub-apps, public web, plus one clean case to measure false alarms). Each case carries "golden" defects the skill had not
written down, to measure whether it **generalizes** rather than just remembers. Scoring separates general coverage,
attention to one specific correction (with and without a hint) and precision: [`evals/playbook.md`](evals/playbook.md)
(Spanish). There is not yet a full recorded run on the v2 cases.

## What it delivers

A markdown report at `docs/revision-<date>.md`, written to stand alone: someone opening it six months later, without
having been in the session, should know what was reviewed, what was found and what was decided. It separates four things
usually mixed together: what was fixed, what was discarded and why, what is left to the client's taste, and **where the
procedure is still blind**. See [`ejemplos/informe-ejemplo-v2.md`](ejemplos/informe-ejemplo-v2.md) (measurement output of
v2) and [`ejemplos/informe-ejemplo.md`](ejemplos/informe-ejemplo.md) (a full v1 report). Both are in Spanish.

## The rule underneath

It is not done when it works. It is done when **nothing looks accidental**: a value nobody chose, a control the operating
system drew, two similar things that are not equal. Each one is a rookie mistake a client notices without being able to
name it.

## Contributing, security, license

- [`CONTRIBUTING.md`](CONTRIBUTING.md) (Spanish): how to propose a check (reproducible evidence, minimal case, no project data).
- [`SECURITY.md`](SECURITY.md): how to report a security issue.
- [`CHANGELOG.md`](CHANGELOG.md): what changed between versions.
- MIT. See [LICENSE](LICENSE).
