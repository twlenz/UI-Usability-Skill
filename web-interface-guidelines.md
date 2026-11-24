# Web interface guidelines (Vercel)

Source: Vercel Web Interface Guidelines, https://vercel.com/design/guidelines. The items below are paraphrased and condensed. Use for **web UIs** (HTML, React, Streamlit, etc.). Skip for desktop, TUI and native mobile, where the platform's own conventions apply.

Used in two places: the builder applies them while writing code, and the evaluator treats violations as findings, filed under the closest Nielsen heuristic (noted in brackets) with a severity from the usual 0–4 scale. They are prompts for looking, not a checklist to tick: report only what you observe.

## How to use alongside the rest of the skill

- Most items are **code-checkable**, not visible in screenshots. The evaluator checks them in the code step and marks the finding source as `code`.
- Conflicts: where a guideline here disagrees with `design-principles.md` or the Nielsen set, the rules in the section below ("Where this set differs") decide.
- Excluded on purpose: Vercel's own brand copywriting preferences (Title Case, "&" for "and", second person), and most of its performance section. Only the user-visible parts of performance are kept (layout shift, latency feedback).

## Interactions [H1, H3, H4, H5, H7]

- Every flow works by keyboard and follows WAI-ARIA patterns. Focus is always visible (`:focus-visible`) and never hidden behind sticky or overlay elements. Overlays trap focus and return it on close.
- Hit areas match the visible target: 24 px minimum, 44 px on mobile. Inputs use at least 16 px font on mobile so iOS doesn't zoom.
- Never disable browser zoom. Never block paste into inputs.
- Anything that looks interactive is interactive, and anything interactive looks it (no dead zones).
- Navigation uses real links (`<a>`), so modifier-click and middle-click work.
- Keep state in the URL where it helps: filters, tabs, pagination and expanded panels are linkable, and refresh, Back and Forward behave. Back/Forward restores scroll position.
- Buttons that start work show a loading indicator and keep their label. Delay spinners briefly and keep them up for a minimum time, so they don't flicker.
- Optimistic updates reconcile with the server, and roll back or offer Undo on failure.
- Destructive actions ask for confirmation or offer Undo within a safe window.
- Menu items that open a follow-up step, and in-progress labels, end with an ellipsis ("Rename…", "Saving…").
- Drag has a click, tap or keyboard alternative. Gestures (swipe, pinch) have equivalents unless the gesture is essential.
- Toasts and inline validation are announced politely to assistive tech (live regions).
- Tooltips: the first in a group is delayed, neighbors appear immediately. Don't rely on tooltips for needed information.
- Set `overscroll-behavior: contain` deliberately in modals and drawers. Set `touch-action: manipulation` on controls to avoid double-tap zoom.

## Animation [H1, H8]

- Provide a reduced-motion variant.
- Animate only to clarify cause and effect, or for deliberate delight.
- Animate `transform` and `opacity`, not layout properties. Never `transition: all`; list the properties.
- Animations are interruptible by user input. Autoplaying motion over 5 seconds has pause/stop controls.
- Anchor motion where it physically starts (transform origin).

## Layout [H4, H8]

- Every element aligns to a grid, baseline, edge or optical center; adjust by about 1 px when perception differs from geometry.
- Test mobile, laptop and ultra-wide widths (zoom out to about 50% to simulate wide).
- Respect safe areas (notches, insets) with `env()`.
- Remove unneeded scrollbars. Prefer flex, grid and intrinsic sizing over JS measurement.

## Content and states [H1, H2, H6, H9, H10]

- Every screen offers a next step or a way out (no dead ends).
- Design empty, sparse, dense and error states, not just the populated one. Layouts hold up for very short and very long user content.
- Prefer inline explanation to tooltips.
- Skeleton loaders match the final content's dimensions, so nothing shifts when content arrives. Images have explicit dimensions.
- Page `<title>` reflects the current context.
- Never rely on color alone for status; add a text label. Icons get text labels or accessible names, and visually hidden labels still have accessible names.
- Use native elements before ARIA, hierarchical headings and a skip link.
- Use tabular numerals where numbers are compared. Avoid widows and orphans in headings. Use non-breaking spaces to keep units, shortcuts and names together. Use typographic quotes and the single ellipsis character.
- Localize dates, times, numbers and currency. Detect language from browser settings, never IP or GPS.
- Media: captions, transcripts, keyboard-operable controls.

## Forms [H3, H5, H6, H9]

- Every control has an associated label, and clicking the label focuses the control. Checkbox and radio share one generous hit target with their label.
- Enter submits when the field is the only control or the last one. In a textarea, Cmd/Ctrl+Enter submits and Enter adds a line.
- Don't block keystrokes. Accept the input, then show validation. (Constrain with the right control and `type`/`inputmode`, not by swallowing keys.)
- Errors appear beside the field, and the first error is focused on submit.
- Keep Submit enabled until sending starts, then disable it, show a spinner and send an idempotency key.
- Set `autocomplete` and meaningful `name` values. Use the correct input `type` and `inputmode`. Turn off spellcheck for emails, codes and usernames. Keep search and similar fields from triggering password managers.
- Placeholders show an example value or pattern and end in an ellipsis; they never replace a label.
- Warn before navigating away from unsaved data. Allow pasting one-time codes. Trim trailing whitespace from values.

## Visual design [H4, H8, Tog: Readability]

- Contrast: prefer APCA over WCAG 2 ratios as the judge, and keep WCAG 4.5:1 as the floor in this skill. Hover, active and focus states have more contrast than the resting state.
- Layer at least two shadows (ambient and direct light) and combine borders with shadows. Nested radii are smaller than the parent's and concentric.
- Tint borders, shadows and text toward the background's hue.
- Chart palettes are color-blind-friendly.
- Set `color-scheme` on `<html>` for dark themes, and `theme-color` to match the page background.
- Use background images, not CSS masks, for gradients, to avoid banding.

## User-visible performance [H1]

- Write requests (POST, PATCH, DELETE) should finish in under about 500 ms, or show progress.
- Lazy-load below-the-fold images and virtualize long lists. Avoid layout shift from images, fonts and skeletons.

## Where this set differs from the rest of the skill

| Topic | Vercel | This skill | Resolution |
|---|---|---|---|
| Disabled submit | Don't pre-disable it; let users submit to see errors | Constrain inputs and show why a control is disabled | General web forms: keep Submit enabled and show errors at the field. **Participant-facing study screens: keep the disabled "Continue" with a visible reason**, since one-time users shouldn't trigger errors at all |
| Blocking input | Never block typing | Prefer constraints over error messages | Use the right control (picker, `type`, `inputmode`) rather than swallowing keystrokes |
| Contrast metric | APCA preferred | WCAG 4.5:1 | Treat 4.5:1 as the minimum; use APCA to judge borderline text |
| Heading case | Title Case (brand rule) | Not specified | Follow the project's existing convention |
