# Design principles for the build phase

Read this once before building a new UI. Each section gives the principle, why it matters, and what it means for code you are about to write. The SKILL.md rules are the short form of this file.

## Contents
1. Norman: the gulfs and the seven stages of action
2. Norman's discoverability toolkit
3. Nielsen's 10 heuristics as build guidelines
4. Information processing limits (Wickens' model)
5. Layout and visual grouping (Gestalt)
6. Text: a budget, not a default
7. The consistency system
8. Platform and context notes (web, desktop, dashboards, study interfaces, mobile, terminal)

---

## 1. Norman: the gulfs and the seven stages of action

A person using any interface goes through a loop: form a **goal** → **plan** an action → **specify** the exact control and input → **perform** it → **perceive** what changed → **interpret** it → **compare** against the goal.

- The **gulf of execution** is the distance between "I want X" and "I know which control does X and how to operate it" (plan, specify, perform).
- The **gulf of evaluation** is the distance between "something happened" and "I understand whether I got X" (perceive, interpret, compare).

Design questions per stage, to ask of every screen:

| Stage | Question for the design |
|---|---|
| Goal | Does the screen make clear what can be accomplished here? |
| Plan | Are the available actions visible without exploration? |
| Specify | Does each control's label/appearance say exactly what it does? Is the right input format obvious? |
| Perform | Is the control easy to hit and operate (size, position, keyboard)? |
| Perceive | Does something visible change, near where the user is looking, quickly? |
| Interpret | Does the change say what happened in the user's terms? |
| Compare | Can the user tell whether they're done, or what's left? |

Unclear controls are a gulf-of-execution failure. Silent actions, ambiguous state and "did that save?" moments are gulf-of-evaluation failures.

## 2. Norman's discoverability toolkit

- **Affordances / signifiers**: an affordance is what an element lets you do; a signifier is the cue that shows it. In software, signifiers are what matter. Buttons look pressable (fill or border, not plain text that happens to be clickable). Links look like links. Draggable things show a handle. Editable text shows a field boundary.
- **Mapping**: put controls where their effect is. A filter belongs above the table it filters; a "delete row" control belongs on the row; a slider's direction matches the value's direction.
- **Constraints**: make wrong actions impossible rather than reporting them. Date pickers instead of free-text dates; disable or omit options that can't apply; numeric inputs with min/max; steppers for small ranges.
- **Feedback**: every action produces a perceivable result, promptly. Aim for an acknowledgment within ~100 ms (pressed state, spinner), progress for anything over ~1 s, and a percent or step count for anything over ~10 s.
- **Conceptual model**: the UI should suggest a simple model of how the system works ("a list of participants, each with sessions"), and the layout should mirror that model. If explaining the model takes a paragraph, the layout isn't carrying it.

## 3. Nielsen's 10 heuristics as build guidelines

The same heuristics the evaluator checks against later (`heuristic-evaluation.md`), phrased as what to do while building. Designing to them up front is cheaper than fixing violations afterwards.

1. **Visibility of system status**: give every action a visible response. Show loading and progress, saved/unsaved state, the current page/step/tab, and active filters or modes.
2. **Match between system and the real world**: label things in the user's domain language, in the order of their real workflow. No code identifiers, raw enum values or internal error text on screen.
3. **User control and freedom**: give every flow a cancel or back. Make destructive actions undoable (or confirmed when undo is impossible), and let modals close.
4. **Consistency and standards**: same word, same look, same place for the same thing on every screen (see section 7). Follow the platform's conventions unless you have a clear reason not to.
5. **Error prevention**: constrain inputs (pickers, ranges, formats), use safe defaults, validate as the user goes, block double-submit, and keep destructive controls away from frequent ones.
6. **Recognition rather than recall**: show options, current values, formats and examples in place. Label icons. Don't use placeholders as labels, and don't make users carry information across screens.
7. **Flexibility and efficiency of use**: Enter submits, Tab order is logical, the last-used values are remembered, and frequent repetitive tasks get bulk actions or shortcuts. None of these should get in a novice's way.
8. **Aesthetic and minimalist design**: every element earns its place. Cut decorative text and visual noise, and give importance a visual hierarchy (see sections 5 and 6).
9. **Help users recognize, diagnose and recover from errors**: errors appear at the problem, say what's wrong and how to fix it in plain words, and keep the user's input.
10. **Help and documentation**: aim for a UI that needs none. Where an unfamiliar concept needs explaining, give a short, contextual hint at the point of use, not a manual up front.

## 4. Information processing limits (Wickens' model)

Wickens' stages: sensory processing → perception → working memory/cognition → response selection → response execution, with limited attention feeding all of them and feedback closing the loop. Each stage has a design implication:

- **Perception / attention**: attention goes to what is salient (contrast, size, motion, position). Make salience match importance: the primary action and the most important data should be the most visually prominent things on the screen. Decoration, borders and secondary info should be quiet. Status that needs noticing uses pre-attentive cues (color *plus* icon/shape/position, never color alone).
- **Working memory**: people hold only about four chunks at once (Cowan). Don't make users carry information between screens or from instructions to the place they act. Show current values, selections and context in place. Group related items into chunks with clear headings.
- **Response selection**: decision time grows with the number of equally weighted choices (Hick–Hyman). Reduce simultaneous options, give a sensible default, and make the recommended path visually obvious. Group and order options by frequency of use.
- **Response execution**: movement time grows with distance and shrinks with target size (Fitts). Frequent actions get large targets close to where the user's attention already is. Minimum target ~24×24 CSS px (WCAG 2.2 AA); 44 pt / 48 dp on touch. Keep destructive targets away from frequent ones.
- **Feedback loop**: the result of each response must be perceivable for the loop to close (see gulf of evaluation).

## 5. Layout and visual grouping (Gestalt)

Layout should communicate structure so text doesn't have to.

- **Proximity**: related items close together, unrelated items farther apart. Spacing between groups should be visibly larger than spacing within groups (e.g. 8 px within, 24 px between).
- **Similarity**: elements that do the same thing look the same; elements that do different things look different.
- **Common region**: cards or panels group content that belongs together. Don't nest boxes inside boxes inside boxes.
- **Alignment**: one or two strong left edges per screen. Labels and fields align consistently (all labels above fields, or all to the left, not mixed).
- **Hierarchy**: page title → section headings → content, with clearly distinct sizes. Scanning order (top-left first in left-to-right languages) should match importance order.
  - Build one clear focal point per screen: the primary action or the key data. Check it with a squint test (blur or shrink a screenshot; the first thing that stands out should be the most important thing).
  - Create hierarchy with a few strong contrasts (size, weight, color, whitespace), not many small ones. Everything bold means nothing is.
  - Secondary and destructive actions are visibly quieter than the primary. Labels are quieter than the data they label.
  - Keep the same hierarchy on every screen: the primary action looks and sits the same way each time.

## 6. Text: a budget, not a default

Claude-built UIs tend to over-explain. Treat every sentence on screen as a cost in reading time and attention.

- Instructions: the shortest wording that a first-time user needs at the moment they need it, placed at the point of action. One line beats a paragraph; a well-labeled control beats a line.
- No welcome banners, taglines, or "This dashboard lets you…" introductions in working tools.
- Helper text only when it adds information the label can't (format, units, constraint). Never restate the label ("Name: Enter your name").
- Front-load key words in labels, headings and menu items ("Export CSV", not "Click here to export your data as CSV").
- Use the user's vocabulary, not the code's (no `participant_id`, `null`, `submit_form`, HTTP codes, stack traces).
- Long reference content (methods, consent text, documentation) goes behind a disclosure, a separate page, or a help link, not inline in the working area.
- Error messages: what went wrong + how to fix it, in one or two short sentences, next to the problem.

Rough self-check: if a working screen has more than ~150 visible words of non-data text, look for text that layout, labels or defaults could replace. (Data, like table contents, doesn't count.)

## 7. The consistency system

Inconsistent layouts happen when each screen or component is styled independently. Prevent it by deciding the system first and building only from it.

Define as tokens in whatever the platform uses (CSS custom properties, a Tailwind config, a Python theme dict, a Qt stylesheet, a constants module):

- **Spacing scale**: e.g. 4, 8, 12, 16, 24, 32, 48. No ad-hoc values.
- **Type scale**: 3–4 sizes (e.g. 12/14/18/24) and 2 weights. Body text ≥ 14 px (≥ 16 px for participant-facing or reading-heavy UIs).
- **Color roles**: one primary (actions), one danger, one success, neutrals for text/borders/backgrounds. Text contrast ≥ 4.5:1 (3:1 for large text and UI component boundaries).
- **Components**: one definition each for primary / secondary / destructive button, text input, select, checkbox, card, table, toast/alert. Reuse, don't restyle.
- **Placement rules**: where the page title goes, where the primary action goes (e.g. bottom-right of forms, top-right of pages), where navigation lives, where feedback appears. Same on every screen.
- **Glossary**: one term per concept, used in every label, heading and message. Pick "session" or "run," not both.

Tog's corollary: things that behave differently should look different ("induced inconsistency"), and a changed screen should look changed.

When modifying an existing UI, the existing system *is* the system. Match it, even if you'd have chosen differently, unless the user asked for a redesign.

## 8. Platform and context notes

**Web apps / pages**: follow web conventions (logo/home top-left, nav top or left, links underlined or obviously styled, browser back works, forms submit on Enter). Responsive down to ~390 px wide unless clearly desktop-only. Keyboard focus visible. Read `web-interface-guidelines.md` (Vercel's guidelines, condensed) before building: it covers keyboard and focus, zoom and paste, forms, loading and empty states, layout shift, motion and more.

**Desktop GUIs (Tkinter, PyQt, Electron)**: follow the OS conventions (menu bar, keyboard shortcuts shown in menus, OK/Cancel order per platform, dialogs modal only when necessary). Use the toolkit's layout managers with consistent padding constants rather than per-widget magic numbers. Window resizes gracefully.

**Dashboards and analysis tools**: the most important number or chart top-left; filters grouped above or beside what they filter, with active filters visible; units and time range always shown; consistent scales across comparable charts. Defer chart design itself to a data-visualization skill if one is available.

**Study / experiment interfaces (participant-facing)**: participants are one-time, untrained users who skim. Design for zero learning:
- One task per screen; instructions on their own screen before the task, with an example or practice trial, not wall-of-text.
- Response mappings (which key = which response) visible during the trial if they must be remembered.
- Large targets, high contrast, ≥ 16 px text; no hover-only information.
- Clear progress ("Block 2 of 4") and clear end state.
- Prevent accidental advancement: no double-submit, debounce key presses, confirm only where data loss is possible.
- Required responses enforced by disabling "Continue" *with* a visible reason, not by an error after clicking.
- Researcher controls (condition assignment, debug info) hidden from participants.

**Mobile**: thumb-reachable primary actions (bottom of screen), 44 pt targets, no hover, single column.

**Terminal / TUI**: show available commands/keys on screen; confirm destructive actions; consistent prompt format; progress for long operations; errors say how to recover.
