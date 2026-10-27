"""Capture the 3D canvas of a product viewer as a PNG (headless Edge, via the anatomy skill's drive.mjs).

Usage: python -I _build/capture_viewer.py <out dir> name=url [name=url ...] [--menu LABEL --options A,B,C] [--size 1440x900]

Each viewer gets 15 s to load. Intro overlays with an "Explore product" style button are clicked away, everything
but the largest canvas is hidden, and only that canvas is shot. With --menu/--options, the menu is opened (only if
closed) and each option is clicked and shot as name-option.png.
"""
import json, os, subprocess, sys
from pathlib import Path

args = sys.argv[1:]
menu, options = None, []
if "--menu" in args:
    i = args.index("--menu"); menu = args[i + 1]; del args[i:i + 2]
if "--options" in args:
    i = args.index("--options"); options = args[i + 1].split(","); del args[i:i + 2]
size = ["1440", "900"]
if "--size" in args:
    i = args.index("--size"); size = args[i + 1].split("x"); del args[i:i + 2]
out = Path(args[0]); out.mkdir(parents=True, exist_ok=True)
drive = Path.home() / ".claude/skills/anatomy/scripts/drive.mjs"
env = dict(os.environ, CHROME_PATH=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def click(label):
    want = json.dumps(label.lower())
    return ("(()=>{const want=%s;const els=[...document.querySelectorAll('button,a,li,div,span,p,label,img')]"
            ".filter(e=>e.offsetParent&&((e.children.length===0&&(e.textContent||'').trim().toLowerCase()===want)"
            "||(e.alt||e.title||'').toLowerCase()===want));if(!els.length) return 'missing '+want;"
            "(els[0].closest('button,a,[role=button]')||els[0]).click();return 'clicked '+want})()") % want


intro = ("[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&/explore (the )?product|explore in 3d|get started/i"
         ".test(e.textContent)).forEach(e=>(e.closest('button,a,[role=button]')||e).click());'ok'")
tag = ("(()=>{const c=[...document.querySelectorAll('canvas')].sort((a,b)=>b.clientWidth*b.clientHeight-a.clientWidth*a.clientHeight)[0];"
       "if(!c) return 'no canvas';c.id='__big';return c.clientWidth+'x'+c.clientHeight})()")
hide = ("(()=>{const c=document.getElementById('__big');document.querySelectorAll('body *').forEach(e=>{if(e!==c&&!e.contains(c))"
        "e.style.setProperty('visibility','hidden','important')});return 'hidden'})()")
show = "(()=>{document.querySelectorAll('body *').forEach(e=>e.style.removeProperty('visibility'));return 'shown'})()"

for spec in args[1:]:
    name, url = spec.split("=", 1)
    acts = [["wait", 15000], ["eval", intro], ["wait", 4000], ["eval", tag]]
    if menu:
        for opt in options:
            opener = "(()=>{const r=%s;if(!r.startsWith('missing')) return r;return %s})()" % (click(opt), click(menu))
            acts += [["eval", show], ["eval", opener], ["wait", 900], ["eval", click(opt)], ["wait", 3500], ["eval", hide],
                     ["wait", 400], ["shot", str(out / f"{name}-{opt.lower().replace('_', '-').lstrip('0123456789-')}.png"), "#__big"]]
    else:
        acts += [["eval", hide], ["wait", 600], ["shot", str(out / f"{name}.png"), "#__big"]]
    plan = out / "_actions.json"
    plan.write_text(json.dumps(acts), encoding="utf-8")
    r = subprocess.run(["node", str(drive), url, "--actions", str(plan), "--width", size[0], "--height", size[1]],
                       capture_output=True, text=True, env=env, timeout=900)
    notes = [l for l in r.stdout.splitlines() if "missing" in l or "no canvas" in l]
    print(name, "ok" if not notes else notes)
