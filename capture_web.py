#!/usr/bin/env python3
"""Render a web UI, screenshot it at several viewports, and run an automated audit.

Works for anything a browser can load: a local .html file, a dev server
(React/Vite, Streamlit, Dash, Gradio, Shiny, Flask...), or any URL.

Usage:
  python capture_web.py index.html --out /tmp/ui-review/shots
  python capture_web.py http://localhost:8501 --out shots \
      --serve "streamlit run app.py --server.headless true --server.port 8501" --wait 4000
  python capture_web.py index.html --out shots --steps steps.json

steps.json (optional) walks through a task and screenshots after every step:
  [
    {"name": "open-add-form", "action": "click", "selector": "text=Add participant"},
    {"action": "fill", "selector": "#participant-id", "value": "P01"},
    {"action": "select", "selector": "#condition", "value": "B"},
    {"action": "press", "selector": "#participant-id", "value": "Enter"},
    {"action": "wait", "value": 500},
    {"action": "hover", "selector": "text=Export"}
  ]
Selectors are Playwright selectors (CSS, text=..., role=button[name="..."]).
If a step's selector can't be found, the walk stops and the failure is recorded,
which is itself useful walkthrough evidence ("the control for step 3 isn't there").

Mobile: besides the desktop viewport(s), the page is loaded in real mobile emulation
(default "iPhone 13": touch events, no hover, mobile user agent, 3x pixel density),
not just a narrow window, so mobile-specific layouts and touch behavior are what
gets captured. In mobile mode clicks in steps become taps, targets are checked
against 44 px, and the audit lists :hover-only reveal rules (unreachable on touch)
and form fields under 16 px font (iOS zooms the page when they're focused).
Use --steps-on both when the UI will be used on phones or tablets.

Outputs in --out:
  desktop-<W>x<H>.png       full-page screenshot per desktop viewport
  mobile-<device>.png       full-page screenshot in mobile emulation
  <mode>-step-NN-<name>.png one per step
  audit.json                automated checks per view + step results + console errors
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

AUDIT_JS = r"""
(opts) => {
  const minTarget = (opts && opts.minTarget) || 24;
  const isVisible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' &&
           s.display !== 'none' && parseFloat(s.opacity || '1') > 0.05;
  };
  const describe = (el) => {
    let d = el.tagName.toLowerCase();
    if (el.id) d += '#' + el.id;
    else if (el.classList.length) d += '.' + [...el.classList].slice(0, 2).join('.');
    const t = (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ');
    if (t) d += ` "${t.slice(0, 40)}"`;
    return d;
  };
  const parseColor = (c) => {
    const m = c && c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
  };
  const lum = ({ r, g, b }) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const effectiveBg = (el) => {
    let n = el;
    while (n && n.nodeType === 1) {
      const s = getComputedStyle(n);
      if (s.backgroundImage && s.backgroundImage !== 'none') return null; // can't judge over images/gradients
      const c = parseColor(s.backgroundColor);
      if (c && c.a > 0.5) return c;
      n = n.parentElement;
    }
    return { r: 255, g: 255, b: 255, a: 1 };
  };
  const ratio = (a, b) => { const la = lum(a), lb = lum(b); return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05); };

  // ---- Text volume, type scale, contrast ----
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let words = 0;
  const blockWords = new Map();
  const fontSizes = {};
  const fontFamilies = {};
  const checked = new Set();
  const lowContrast = [];
  let n;
  while ((n = walker.nextNode())) {
    const t = n.textContent.trim();
    if (!t) continue;
    const el = n.parentElement;
    if (!el || ['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(el.tagName) || !isVisible(el)) continue;
    const w = t.split(/\s+/).length;
    words += w;
    const block = el.closest('p,li,td,th,label,div,section,article,span,h1,h2,h3,h4,h5,h6,button,a') || el;
    blockWords.set(block, (blockWords.get(block) || 0) + w);
    const s = getComputedStyle(el);
    fontSizes[s.fontSize] = (fontSizes[s.fontSize] || 0) + w;
    const fam = s.fontFamily.split(',')[0].trim();
    fontFamilies[fam] = (fontFamilies[fam] || 0) + w;
    // WCAG exempts disabled (inactive) controls from contrast requirements.
    const disabled = el.closest('button:disabled, input:disabled, select:disabled, textarea:disabled, fieldset:disabled, [aria-disabled="true"]');
    if (!checked.has(el) && !disabled) {
      checked.add(el);
      const fg = parseColor(s.color), bg = effectiveBg(el);
      if (fg && bg) {
        const r = ratio(fg, bg);
        const px = parseFloat(s.fontSize), bold = parseInt(s.fontWeight) >= 700;
        const large = px >= 24 || (bold && px >= 18.66);
        const need = large ? 3 : 4.5;
        if (r < need) lowContrast.push({ element: describe(el), ratio: +r.toFixed(2), required: need });
      }
    }
  }
  const longestBlocks = [...blockWords.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5)
    .map(([el, w]) => ({ element: describe(el), words: w }));

  // ---- Controls: names, labels, target size, button style variety ----
  const ctrlSel = 'button, a[href], input, select, textarea, summary, [role=button], [role=link], [role=tab], [role=checkbox], [role=radio], [role=switch], [role=menuitem], [onclick], [tabindex]:not([tabindex="-1"])';
  const controls = [...document.querySelectorAll(ctrlSel)].filter(isVisible);
  const unnamed = [], iconOnly = [], placeholderOnly = [], smallTargets = [], smallFieldFont = [];
  const buttonStyles = {};
  for (const el of controls) {
    const tag = el.tagName;
    const type = (el.getAttribute('type') || '').toLowerCase();
    const isField = (tag === 'INPUT' && !['button', 'submit', 'reset', 'image', 'hidden'].includes(type)) || tag === 'SELECT' || tag === 'TEXTAREA';
    const visibleText = (el.innerText || '').trim() || (tag === 'INPUT' && ['button', 'submit', 'reset'].includes(type) ? el.value : '');
    const aria = el.getAttribute('aria-label') ||
      (el.getAttribute('aria-labelledby') || '').split(' ').map(id => document.getElementById(id)?.innerText || '').join(' ').trim();
    const title = el.getAttribute('title');
    const imgAlt = el.querySelector('img[alt]')?.getAttribute('alt');
    if (isField) {
      const hasLabel = (el.labels && el.labels.length > 0) || aria || title;
      if (!hasLabel && el.getAttribute('placeholder')) placeholderOnly.push(describe(el) + ` placeholder="${el.getAttribute('placeholder')}"`);
      else if (!hasLabel && type !== 'checkbox' && type !== 'radio') unnamed.push(describe(el));
      else if (!hasLabel) unnamed.push(describe(el));
    } else {
      // A lone glyph (✓, ⋮, →, emoji) is an icon, not a label.
      const hasWords = /[\p{L}\p{N}]/u.test(visibleText);
      if (!visibleText && !aria && !title && !imgAlt) unnamed.push(describe(el));
      else if (!hasWords) iconOnly.push(describe(el) + (aria ? ` aria-label="${aria}"` : title ? ` title="${title}"` : ' (no accessible name)'));
    }
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    const inlineLink = tag === 'A' && s.display === 'inline';
    if (!inlineLink && type !== 'hidden' && (r.width < minTarget || r.height < minTarget))
      smallTargets.push({ element: describe(el), size: `${Math.round(r.width)}x${Math.round(r.height)}` });
    if (isField && parseFloat(s.fontSize) < 16) smallFieldFont.push(describe(el) + ` ${s.fontSize}`);
    const looksLikeButton = tag === 'BUTTON' || el.getAttribute('role') === 'button' ||
      (tag === 'INPUT' && ['button', 'submit', 'reset'].includes(type)) ||
      (tag === 'A' && (parseColor(s.backgroundColor)?.a || 0) > 0.5);
    if (looksLikeButton) {
      const sig = [s.backgroundColor, s.color, s.borderRadius, s.fontSize, s.fontWeight, `${s.paddingTop} ${s.paddingLeft}`, s.borderTopWidth + ' ' + s.borderTopColor].join(' | ');
      (buttonStyles[sig] = buttonStyles[sig] || []).push(describe(el));
    }
  }
  const buttonStyleList = Object.entries(buttonStyles).sort((a, b) => b[1].length - a[1].length)
    .map(([sig, els]) => ({ style: sig, count: els.length, examples: els.slice(0, 3) }));

  const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(isVisible)
    .map(h => `${h.tagName}: ${(h.innerText || '').trim().slice(0, 60)}`);

  // CSS rules that reveal or show something only on :hover. Touch screens have no hover,
  // so anything revealed this way is unreachable or invisible on phones and tablets
  // (unless the rule sits inside an @media (hover: hover) block).
  const hoverReveal = [];
  const scanRules = (rules, inHoverMedia) => {
    for (const rule of rules) {
      if (rule.cssRules && rule.media) {
        scanRules(rule.cssRules, inHoverMedia || /hover:\s*hover/.test(rule.media.mediaText));
      } else if (rule.selectorText && rule.selectorText.includes(':hover') && !inHoverMedia) {
        const st = rule.style;
        const reveals = (st.display && st.display !== 'none') || st.visibility === 'visible' ||
          (st.opacity && parseFloat(st.opacity) > 0.5) || st.pointerEvents === 'auto';
        if (reveals) hoverReveal.push(rule.selectorText.slice(0, 120));
      }
    }
  };
  for (const sheet of document.styleSheets) {
    try { scanRules(sheet.cssRules, false); } catch (e) { /* cross-origin sheet */ }
  }

  // Containers that scroll sideways (e.g. a wide table in an overflow-x:auto wrapper). The page
  // itself doesn't overflow, but on a narrow screen columns are hidden off to the side.
  const innerHScroll = [];
  for (const el of document.querySelectorAll('body *')) {
    if (!isVisible(el)) continue;
    const ox = getComputedStyle(el).overflowX;
    if ((ox === 'auto' || ox === 'scroll') && el.scrollWidth > el.clientWidth + 4)
      innerHScroll.push({ element: describe(el), visible_px: el.clientWidth, content_px: el.scrollWidth });
  }
  const vpMeta = document.querySelector('meta[name="viewport"]');
  return {
    viewport: `${innerWidth}x${innerHeight}`,
    // Without a viewport meta tag, phones lay the page out ~980px wide and shrink it,
    // so text and targets become tiny. Only meaningful in the mobile-emulation pass.
    viewport_meta: vpMeta ? vpMeta.getAttribute('content') : null,
    // Vercel guideline: never disable browser zoom (user-scalable=no or maximum-scale=1).
    zoom_disabled: !!(vpMeta && /user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?\b/i.test(vpMeta.getAttribute('content') || '')),
    page_height: document.documentElement.scrollHeight,
    // On a phone, content wider than the screen means sideways scrolling or a zoomed-out page.
    content_width: document.documentElement.scrollWidth,
    horizontal_overflow: document.documentElement.scrollWidth > ((opts && opts.mobile) ? screen.width : innerWidth) + 1,
    sideways_scroll_containers: innerHScroll.slice(0, 8),
    text: {
      visible_words: words,
      longest_blocks: longestBlocks,
      distinct_font_sizes: Object.keys(fontSizes).length,
      font_sizes_by_words: fontSizes,
      font_families: fontFamilies,
      low_contrast_text: lowContrast.slice(0, 15),
      low_contrast_count: lowContrast.length,
    },
    controls: {
      total_visible: controls.length,
      unnamed: unnamed.slice(0, 15),
      icon_only_or_hidden_label: iconOnly.slice(0, 15),
      fields_with_placeholder_as_only_label: placeholderOnly.slice(0, 15),
      min_target_px: minTarget,
      targets_under_min: smallTargets.slice(0, 15),
      small_target_count: smallTargets.length,
      fields_under_16px_font: smallFieldFont.slice(0, 10),
      hover_only_reveal_rules: hoverReveal.slice(0, 10),
      distinct_button_styles: buttonStyleList.length,
      button_styles: buttonStyleList.slice(0, 8),
    },
    headings: headings.slice(0, 30),
  };
}
"""


def wait_for_url(url, timeout):
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=3)
            return True
        except Exception:
            time.sleep(0.5)
    return False


def to_url(target):
    if target.startswith(("http://", "https://", "file://")):
        return target
    p = Path(target).resolve()
    if not p.exists():
        sys.exit(f"Not found: {target}")
    return p.as_uri()


def settle(page, wait_ms):
    try:
        page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    page.wait_for_timeout(wait_ms)


def run_step(page, step, touch=False):
    action = step.get("action")
    sel = step.get("selector")
    val = step.get("value")
    timeout = step.get("timeout", 5000)
    if action == "click":
        if touch:
            page.locator(sel).first.tap(timeout=timeout)
        else:
            page.locator(sel).first.click(timeout=timeout)
    elif action == "fill":
        page.locator(sel).first.fill(str(val), timeout=timeout)
    elif action == "select":
        page.locator(sel).first.select_option(str(val), timeout=timeout)
    elif action == "check":
        page.locator(sel).first.check(timeout=timeout)
    elif action == "press":
        if sel:
            page.locator(sel).first.press(str(val), timeout=timeout)
        else:
            page.keyboard.press(str(val))
    elif action == "hover":
        page.locator(sel).first.hover(timeout=timeout)
    elif action == "goto":
        page.goto(to_url(val))
    elif action == "wait":
        page.wait_for_timeout(int(val or 500))
    elif action == "scroll":
        page.mouse.wheel(0, int(val or 600))
    else:
        raise ValueError(f"Unknown action: {action}")


def slug(s):
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in s)[:40]


def walk_steps(page, steps, out, prefix, full_page, touch, report):
    results = []
    for n, step in enumerate(steps, 1):
        label = step.get("name") or f"{step.get('action')}"
        fname = f"{prefix}-step-{n:02d}-{slug(label)}.png"
        entry = {"n": n, **step, "screenshot": fname}
        try:
            run_step(page, step, touch=touch)
            page.wait_for_timeout(step.get("settle", 400))
            page.screenshot(path=str(out / fname), full_page=full_page)
            entry["ok"] = True
            results.append(entry)
        except Exception as e:
            entry["ok"] = False
            entry["error"] = str(e).splitlines()[0][:300]
            try:
                page.screenshot(path=str(out / fname), full_page=full_page)
            except Exception:
                pass
            results.append(entry)
            break
    report["steps"][prefix] = results
    report[f"after_steps_audit_{prefix}"] = page.evaluate(AUDIT_JS, {"minTarget": 44 if touch else 24, "mobile": touch})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="Path to .html file or URL")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--viewports", default="1440x900", help="Desktop viewports, comma list of WxH (default 1440x900)")
    ap.add_argument("--mobile-device", default="iPhone 13",
                    help='Playwright device to emulate for the mobile pass (e.g. "iPhone 13", "Pixel 7", "iPad (gen 7)")')
    ap.add_argument("--no-mobile", action="store_true", help="Skip the mobile-emulation pass (desktop-only UIs)")
    ap.add_argument("--wait", type=int, default=800, help="Extra ms to wait after load (raise for Streamlit/React)")
    ap.add_argument("--steps", help="JSON file of task steps to click through and screenshot")
    ap.add_argument("--steps-on", choices=["desktop", "mobile", "both"], default="desktop",
                    help="Where to walk the steps (use both for UIs used on phones/tablets)")
    ap.add_argument("--serve", help="Shell command that starts a dev server before capture; killed afterwards")
    ap.add_argument("--serve-timeout", type=int, default=60)
    ap.add_argument("--no-full-page", action="store_true", help="Viewport-only screenshots")
    ap.add_argument("--tall", type=int, default=0,
                    help="Viewport height in px for every view. Use for apps that scroll inside their own "
                         "container (Streamlit, many SPAs), where full-page screenshots get cut at the window height")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    url = to_url(args.target)
    full_page = not args.no_full_page
    steps = json.loads(Path(args.steps).read_text()) if args.steps else None

    server = None
    if args.serve:
        server = subprocess.Popen(args.serve, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not wait_for_url(url, args.serve_timeout):
            server.terminate()
            sys.exit(f"Server did not respond at {url} within {args.serve_timeout}s")

    report = {"target": args.target, "views": {}, "steps": {}, "console_errors": []}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            views = []
            for i, v in enumerate(args.viewports.split(",")):
                w, h = map(int, v.lower().split("x"))
                views.append((f"desktop-{w}x{h}", {"viewport": {"width": w, "height": h}}, False, i == 0))
            if not args.no_mobile:
                if args.mobile_device not in p.devices:
                    sys.exit(f"Unknown device {args.mobile_device!r}. Examples: iPhone 13, Pixel 7, iPad (gen 7)")
                views.append((f"mobile-{slug(args.mobile_device)}", dict(p.devices[args.mobile_device]), True, True))
            if args.tall:
                for _, opts, _, _ in views:
                    opts["viewport"] = {"width": opts["viewport"]["width"], "height": args.tall}

            for name, ctx_opts, is_mobile, steps_allowed in views:
                ctx = browser.new_context(**ctx_opts)
                page = ctx.new_page()
                page.on("console", lambda m: m.type == "error" and report["console_errors"].append(m.text[:300]))
                page.on("pageerror", lambda e: report["console_errors"].append(str(e)[:300]))
                page.goto(url)
                settle(page, args.wait)
                shot = out / f"{name}.png"
                page.screenshot(path=str(shot), full_page=full_page)
                report["views"][name] = {"screenshot": shot.name, "mobile_emulation": is_mobile,
                                         **page.evaluate(AUDIT_JS, {"minTarget": 44 if is_mobile else 24, "mobile": is_mobile})}
                want = args.steps_on == "both" or (args.steps_on == "mobile") == is_mobile
                if steps and steps_allowed and want:
                    walk_steps(page, steps, out, "mobile" if is_mobile else "desktop", full_page, is_mobile, report)
                ctx.close()
            browser.close()
    finally:
        if server:
            server.terminate()
            try:
                server.wait(timeout=5)
            except Exception:
                server.kill()

    (out / "audit.json").write_text(json.dumps(report, indent=2))

    # Compact summary for the terminal
    print(f"Saved screenshots and audit.json to {out}")
    for vp, a in report["views"].items():
        t, c = a["text"], a["controls"]
        extra = ""
        if a["mobile_emulation"]:
            extra = (f" viewport_meta={'yes' if a['viewport_meta'] else 'MISSING'}"
                     f" zoom_disabled={a['zoom_disabled']}"
                     f" content_width={a['content_width']}"
                     f" hover_only_rules={len(c['hover_only_reveal_rules'])}"
                     f" fields_under_16px={len(c['fields_under_16px_font'])}")
        print(f"[{vp}] words={t['visible_words']} font_sizes={t['distinct_font_sizes']} "
              f"button_styles={c['distinct_button_styles']} unnamed={len(c['unnamed'])} "
              f"icon_only={len(c['icon_only_or_hidden_label'])} placeholder_only={len(c['fields_with_placeholder_as_only_label'])} "
              f"targets_under_{c['min_target_px']}px={c['small_target_count']} low_contrast={t['low_contrast_count']} "
              f"h_overflow={a['horizontal_overflow']} sideways_scroll_boxes={len(a['sideways_scroll_containers'])}{extra}")
    for mode, res in report["steps"].items():
        failed = [s for s in res if not s.get("ok")]
        print(f"{mode} steps: {len(res)} run, {len(failed)} failed" +
              (f" -> step {failed[0]['n']}: {failed[0]['error']}" if failed else ""))
    if report["console_errors"]:
        print(f"console errors: {len(report['console_errors'])} (see audit.json)")


if __name__ == "__main__":
    main()
