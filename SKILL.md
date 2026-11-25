---
name: ui-usability
description: Usability-first workflow for any interface Claude builds. Design with Norman's gulfs of execution/evaluation, information-processing limits and Nielsen/Tognazzini heuristics; then render screenshots, run an independent heuristic evaluation and cognitive walkthrough, revise, and report short findings. Use whenever the user asks to create, build, scaffold, prototype or substantially rework anything people will see or click — web pages, HTML/React/Vue apps, dashboards, Streamlit/Dash/Gradio/Shiny apps, Tkinter/PyQt/Electron GUIs, experiment or survey screens (jsPsych, PsychoPy), forms, settings panels, admin tools, mobile screens, interactive TUIs — even if they never mention usability, UX or design. Use alongside frontend-design, which handles visual style.
---

# UI usability

Claude-built interfaces tend to fail in three predictable ways: **unclear controls**, **too much text**, and **layouts that drift from screen to screen**. This skill counters them twice. First, design rules applied while building. Second, an independent evaluate-and-revise loop on the rendered UI, because what reads fine in code often doesn't work on screen.

## Scale the effort to the change

- **New UI, new screens or flows, or a substantial rework**: run the full workflow below.
- **Small change to an existing UI** (one control, a copy edit, a style tweak): apply the build rules to the change, make it match the existing UI's patterns, take one screenshot if it's cheap, and skip the subagent evaluation. Report in one line.
- **UI is incidental** (a script with one prompt, a quick plot window): apply the build rules only.

## Workflow

1. Brief → 2. Build → 3. Capture → 4. Evaluate (independent) → 5. Revise → 6. Report

For the full workflow, copy this checklist into your task list (a todo tool if you have one) and tick items off as you go. Steps are easiest to skip when a run is long, and the skipped ones (end screens, the independent evaluator) are often where problems hide.

```
- [ ] Brief: ui-brief.md with users, devices, 1–3 top tasks (step by step), primary action per screen
- [ ] Design tokens defined before the second screen
- [ ] Built: verb + object labels, one primary action per screen, text within budget
- [ ] Capture tools checked (capture_web.py --check), or code-only review chosen and noted
- [ ] Screenshots of every state: first view, populated, error, empty, and any start or end screen
- [ ] Mobile pass done (or skipped because the UI can't run on mobile); steps file for top task 1
- [ ] Fresh evaluator subagent spawned with paths only (or self-review fallback, noted in report)
- [ ] Every severity 3–4 finding fixed through the design system; word count not increased
- [ ] Re-captured and re-checked (max 2 rounds)
- [ ] Short report: fixed, remaining, assumptions, code-only if so
```

Keep review artifacts (brief, screenshots, findings) in a scratch directory outside the user's project, e.g. `/tmp/ui-review-<project>/`, so the repo isn't cluttered. Keep them only if the user asks.

### 1. Write a UI brief before writing code

About ten lines, saved as `ui-brief.md` in the review directory, because the evaluator needs it:

- **Users**: who, what they already know, how often they'll use this (one-time participant vs. daily expert), and their context (time pressure, environment).
- **Devices**: which ones the UI will really be used on (desktop, phone, tablet, kiosk). This decides whether mobile behavior is a requirement or a nice-to-have.
- **Top tasks** (1–3): the tasks that justify the UI. For each, the intended action sequence, one line per step (what the user sees → what they do).
- **Primary action** of each screen.
- **Conventions**: platform norms; the existing design system if modifying a UI.

Infer all of this from the request and the codebase. Ask the user only if the users or tasks are unclear in a way that would change the design. Otherwise state your assumptions in the final report, where the user can correct them.

### 2. Build

Read `references/design-principles.md` the first time you use this skill in a session. It's the full version of these rules, with platform notes (web, desktop, dashboards, study interfaces, mobile, terminal). For web UIs, also read `references/web-interface-guidelines.md` (Vercel's guidelines: keyboard and focus, forms, states, motion, layout shift).

**Close the gulf of execution: every control says what it does.**
- Label actions as verb + object ("Export CSV", "Add participant"), not "Submit", "OK", "Go" or "Process".
- Put text labels on icons unless the icon is universal (×, search), and give every icon an accessible name.
- One visually dominant primary action per screen or region. Secondary actions look secondary. Destructive actions look different and sit apart.
- Place controls next to what they affect.
- Prefer constraints to error messages: pickers, ranges, and omitting impossible options. If a control must be disabled, show why.

**Close the gulf of evaluation: every action shows its result.**
- Every action produces a visible change near where the user acted. Show a loading state for anything over ~1 s.
- Keep status visible where it matters: saved/unsaved, step 2 of 4, active filters, current tab.
- Errors appear at the field, in plain words, with how to fix them.

**Respect information-processing limits: less text, more structure.**
- Treat text as a budget. Say it once, briefly, key words first. Skip welcome banners, "This tool lets you…" intros, and helper text that restates the label. If the UI needs a paragraph to explain how to use it, fix the UI instead of writing the paragraph.
- Let layout carry meaning: proximity, alignment, grouping and visual hierarchy instead of explanatory prose.
- Keep simultaneous choices few and provide good defaults. Use progressive disclosure for advanced options, but don't hide what's needed every time.
- Recognition over recall: show current values, options and examples in place. Don't make users remember things from another screen.
- Salience follows importance: the most important data and the primary action are the most prominent things on screen. One focal point per screen, a few strong contrasts rather than many small ones, and the same hierarchy on every screen.
- Never use color as the only signal. Text contrast ≥ 4.5:1. Targets ≥ 24 px (44 pt on touch).

**Lock in consistency before the second screen.**
Define a small design system first, as tokens in whatever the platform uses (CSS variables, a theme dict, a Qt stylesheet, a constants module), and build only from it:
- a spacing scale, a 3–4 step type scale, color roles (primary, danger, success, neutrals)
- one definition each for primary / secondary / destructive button, input, card, alert
- placement rules for title, primary action, navigation and feedback, the same on every screen
- a glossary: one term per concept, everywhere

Things that behave the same look the same; things that behave differently look different. When modifying an existing UI, its existing system is the system.

If `frontend-design` or a similar style skill is also in use, let it set the visual style within these rules. Where style and clarity conflict, clarity wins.

### 3. Capture what users will actually see

Render the UI and take screenshots. Layout drift, buried controls and text overload are visual problems that code review misses.

- **Anything a browser can load** (HTML, React/Vite, Streamlit, Dash, Gradio, Shiny, Flask): run `scripts/capture_web.py` from this skill's folder.
  ```bash
  python <skill-dir>/scripts/capture_web.py --check        # Playwright + Chromium present?
  python <skill-dir>/scripts/capture_web.py <file-or-url> --out <review-dir>/shots
  ```
  The script needs Playwright and its Chromium build. If `--check` exits with code 3, it prints the install commands (`pip install playwright`, then `python -m playwright install chromium`). In a sandbox or cloud workspace, run them. On the user's own machine, ask before installing, and install into a virtual environment if the project uses one. If installing isn't possible, do the code-only review described below.
  It screenshots a desktop viewport, then loads the page again in real mobile emulation (touch input, no hover, mobile browser identity, phone pixel density), not just a narrow window. That's what reveals hover-only controls, missing viewport settings and touch-target problems. It writes `audit.json`: visible word counts and longest text blocks, unlabeled and icon-only controls, placeholder-only fields, small targets (24 px desktop, 44 px touch), low-contrast text, the number of distinct font sizes and button styles, horizontal overflow, console errors, and, for mobile, hover-only reveal rules, a missing viewport tag and form fields that make iOS zoom.
  - `--serve "<cmd>"` starts a dev server first. Use `--wait 4000` for Streamlit or React.
  - `--steps steps.json` clicks through a top task and screenshots each step (taps in mobile mode). These step screenshots are the cognitive walkthrough's raw material, so write a steps file for at least the first top task.
  - `--steps-on both` walks the task on desktop and mobile. Use it when the brief lists phones or tablets.
  - `--mobile-device "iPad (gen 7)"` emulates a different device. `--no-mobile` skips the mobile pass, for UIs that can't run on mobile at all.
- **Desktop GUIs, experiment software, native mobile apps (simulator/emulator), terminal UIs**: follow `references/capturing-screens.md`.
- Capture the states that matter: first view, populated, error, empty.
- If rendering isn't possible (missing hardware or credentials, dependencies you shouldn't install), fall back to a code-only review and say so in the report. Never present a code-only review as if it had seen the screen.

### 4. Evaluate with fresh eyes

Spawn a subagent whose instructions are `references/evaluator-brief.md`. Pass it the paths to `ui-brief.md`, the screenshot directory, `audit.json` and the source files, and tell it where the reference files are. Don't pass your design rationale and don't ask it to confirm the design works. The value comes from a reviewer who knows only what a user would know plus the intended tasks, the same reason heuristic evaluations use evaluators who didn't build the system.

The evaluator runs a cognitive walkthrough of each top task and a heuristic sweep (Nielsen's 10, Tognazzini's principles, a visual-hierarchy squint test, and for web UIs the Vercel guidelines). It checks the UI against the brief's users, tasks and primary actions. It doesn't see your reasons for design choices, so it can't check whether the build matches them. It returns its findings as its reply: each finding has evidence, a 0–4 severity and a specific fix. Save that reply as `findings.md` in the review directory. (Subagents are often told not to write report files, so the evaluator doesn't write it.) For a re-check, append the reply to `findings.md`.

If no subagent tool is available, do the evaluation yourself as a separate pass. Re-read only the brief, the screenshots and `audit.json`, follow the evaluator brief, and hunt for problems in your own work. Expect to be lenient toward it, and compensate.

### 5. Revise

- Fix every severity 3–4 finding. Fix 2s when the fix is small and doesn't add complexity. Leave 0–1s unless they're free.
- Fix through the design system (change the token or shared component), not with one-off overrides. One-off fixes are how layouts become inconsistent.
- A confusing control is usually fixed with a better label, placement or constraint, not with explanatory text next to it. Check that the revision didn't increase the word count.
- Re-capture. If you fixed any 3–4s, have the evaluator re-check those items and look for regressions against its "Keep" list. Stop after two revision rounds and report what remains.

### 6. Report briefly

After delivering the UI, add a short usability note so the user can see what was found and judge the evaluation themselves. Don't write a full audit:

```
**Usability check**: cognitive walkthrough (add participant, export data) + heuristic review, from screenshots
Fixed
- [3] Export was an unlabeled icon → "Export CSV" button (recognition over recall)
- [3] Saving gave no feedback → "Saved 14:02" appears beside the button (visibility of status)
- [2] Instructions paragraph (62 words) → removed; field labels carry it (minimalist design)
Remaining
- [1] Table header wraps at phone width
Assumed: users = research assistants, weekly use
```

List up to ~6 items, highest severity first. Numbers in brackets are Nielsen severity (0–4). Say if the review was code-only. Don't list the heuristics that passed.

## Reference files

| File | Read when |
|---|---|
| `references/design-principles.md` | Before building a new UI (once per session) |
| `references/capturing-screens.md` | The UI isn't loadable in a browser |
| `references/evaluator-brief.md` | Instructions for the evaluation subagent (or for your own evaluation pass) |
| `references/heuristic-evaluation.md` | Read by the evaluator: Nielsen's 10, Tognazzini, visual hierarchy, severity scale |
| `references/web-interface-guidelines.md` | Web UIs: read before building, and read by the evaluator |
| `references/cognitive-walkthrough.md` | Read by the evaluator: walkthrough procedure and the four questions |
| `scripts/capture_web.py` | Screenshots + automated audit for anything browser-loadable |
