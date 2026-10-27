"""Generate the site: index, projects, 3d and the case study pages.

Layout: a slim icon rail on the left, a full-screen 3D hero, projects as cards,
renders as a carousel, and a terminal-style contact form.
Project data comes from build.py (the `builds` list); render data is parsed from the root 3d.html.
"""
import json, ast
import re
import sys
from html import escape
from pathlib import Path

root = Path(sys.argv[1])
out = root
out.mkdir(exist_ok=True)
scratch = Path(__file__).parent

# ---------------------------------------------------------------- data
build_src = (scratch / "build.py").read_text(encoding="utf-8")
GH = "https://github.com/kaydee001/"
builds = None
for node in ast.parse(build_src).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "builds":
        builds = eval(ast.get_source_segment(build_src, node.value), {"GH": GH})
assert builds and len(builds) == 16
by_build = {b[0]: b for b in builds}
labels = {"ai": "AI", "tools": "Tool", "apps": "App"}

# Experience as a journey. Each result reads: what I did, how it showed (measured by), how I did it.
# Everything here comes from the resume.
JOURNEY = [
    {
        "tag": "left",
        "mark": "M",
        "since": "2022-05",
        "until": "2024-02",
        "when": "May 2022 – Feb 2024",
        "role": "Spatial 3D Designer",
        "where": "Myracle.io · Berlin, remote",
        "why": "I built 3D models and animations for AR and VR science lessons, researched and prototyped each STEM topic, and taught it to students.",
        "wins": [
            ("20+", "lessons · 3 subjects", "Turned STEM lesson plans into 3D scenes",
             "Physics, chemistry and biology. Went through each topic with teachers and the curriculum before modelling it.", None),
            ("2", "platforms", "Prototyped and tested the AR and VR app",
             "Built 3D prototypes, tested the app with the whole team and fixed what didn't work.", None),
            ("300+", "students", "Ran workshops and taught Blender",
             "Led the sessions myself and tested the lessons live.", None),
            ("10M+", "viewers", "Featured on Shark Tank India",
             "Piloted first in 20+ government schools in Punjab, then pitched on the show. Built remotely with a small team across time zones.", None),
        ],
    },
    {
        "tag": "now",
        "mark": "H",
        "since": "2024-09",
        "until": None,
        "when": "Sep 2024 – now",
        "role": "Real-Time Artist",
        "where": "HMX Media · Pune",
        "why": "I get product models ready for web 3D: baking AO, lighting and rendering. I also build tools that make the pipeline faster.",
        "wins": [
            ("90+", "products", "Shipped 3D web and AR experiences",
             "For Dell and Lenovo alone. From model to interaction, using the in-house visual scripting tool.", None),
            ("~35%", "lighter files", "Made models load faster",
             "Cleaned up UVs, baked AO and HDR lighting, and optimised meshes and textures.", None),
            ("4+", "team tools", "Took the busywork out of asset prep",
             "2–3 file tools and 2 Blender add-ons, used by the whole team. Built in Python, with AI as a co-pilot.", None),
            ("5", "global brands", "Worked on products for big clients",
             "Dell, Lenovo, Royal Enfield, McLaren and C.L. Seifert.", None),
        ],
        "builds": "HMX_BUILDS",
        "also": "65+ more Dell and Lenovo products.",
    },
]

# Products built start to finish at HMX. Thumbnails are captures of the live viewers; links go to the
# official product pages (the viewers themselves are client deliverables and aren't linked).
HMX_BUILDS = [
    # Shown first: the other clients, then one of each kind from Lenovo, then Dell; the rest open with "Show all"
    ("var/mso-anniversaryorange", "McLaren Artura", "McLaren", "12 MSO Colours", "https://www.mclarentampabay.com/configure-artura.html"),
    ("var/re-k2f3-apexred", "Classic, Meteor & Guerrilla", "Royal Enfield", "6 Colourways", "https://makeityours.royalenfield.com/configurator/guerrilla-450/"),
    ("var/cap-dk", "C.L. Seifert Student Caps", "C.L. Seifert", "3 Countries", "https://clseifert.com/dk/wizard"),
    ("gb300", "Lenovo NVIDIA GB300 NVL72", "Lenovo", "AI Rack", "https://lenovopress.lenovo.com/lp2357-lenovo-nvidia-gb300-nvl72-rack-scale-ai"),
    ("sr850", "ThinkSystem SR850 V4", "Lenovo", "Server", "https://www.lenovo.com/us/en/p/servers-storage/servers/large-memory/lenovo-thinksystem-sr850-v4/7djsa007na"),
    ("xultra", "ThinkCentre X Ultra", "Lenovo", "Mini PC", "https://psref.lenovo.com/Product/ThinkCentre_X_Ultra"),
    ("neo55a", "ThinkCentre neo 55a Gen 6", "Lenovo", "All-in-One", "https://www.lenovo.com/gb/en/p/desktops/thinkcentre/thinkcentre-neo-series/thinkcentre-neo-55a-gen-6-24-inch-amd-all-in-one-/len102c0073"),
    ("t14s", "ThinkPad T14s Gen 7", "Lenovo", "Laptop", "https://www.lenovo.com/us/en/p/laptops/thinkpad/thinkpadt/lenovo-thinkpad-t14s-gen-7-14-inch-intel-/len101t0155"),
    ("maxtower", "Dell Pro Max Tower T2", "Dell", "Workstation", "https://www.dell.com/en-us/shop/desktop-computers/spd/dellpromaxtowert2fct2250"),
    ("m7725", "PowerEdge M7725", "Dell", "Compute Sled", "https://www.dell.com/en-us/shop/ipovw/poweredge-m7725"),
    ("p4326", "Dell Pro P 43 4K Conference Monitor", "Dell", "Conference Monitor", "https://www.dell.com/en-us/shop/dell-pro-p-43-4k-huddle-conferencing-monitor-p4326qeb/apd/210-bwxm/monitors-monitor-accessories"),
    ("oss25", "Dell Pro Slim All-in-One Stand", "Dell", "All-in-One Stand", "https://www.dell.com/en-ca/shop/dell-pro-slim-all-in-one-stand-oss25/apd/482-bbfm/pc-accessories"),
    ("maxslim", "Dell Pro Max Slim", "Dell", "Desktop", "https://www.dell.com/en-us/shop/desktop-computers/dell-pro-max-slim-desktop/spd/dell-pro-max-fcs1250-slim-desktop"),
    ("maxmicro", "Dell Pro Max Micro", "Dell", "Mini PC", "https://www.dell.com/en-us/shop/desktop-computers/dell-pro-max-micro-desktop/spd/dell-pro-max-fcm2250-micro"),
    ("pw9t2", "Dell Pro Precision 9 T2", "Dell", "Workstation", "https://www.dell.com/en-us/shop/desktop-computers/spd/dellproprecision9t2pw9t2260"),
    ("pw514", "Dell Pro Precision 5 14", "Dell", "Laptop", "https://www.dell.com/en-us/shop/laptop-computers/spd/dellproprecision514pw514261"),
    ("tb16p", "ThinkBook 16p Gen 6", "Lenovo", "Laptop", "https://psref.lenovo.com/Product/ThinkBook/ThinkBook_16p_G6_IAX"),
    ("db16", "Dell 16 Plus", "Dell", "Laptop", "https://www.dell.com/en-us/shop/laptop-computers/spd/dellplus16laptopdb16250"),
    ("aio24", "Dell Pro 24 All-in-One", "Dell", "All-in-One", "https://www.dell.com/en-us/shop/desktop-computers/dell-pro-24-all-in-one-35w-desktop/spd/dell-pro-qc24251-aio"),
    ("ec24", "Dell 24 All-in-One", "Dell", "All-in-One", "https://www.dell.com/en-us/shop/desktop-computers/spd/dell24allinoneec24260"),
    ("micro", "Dell Pro Micro Plus", "Dell", "Mini PC", "https://www.dell.com/en-us/shop/desktop-computers/dell-pro-micro-plus-desktop/spd/dell-pro-qbm1250-plus-micro"),
    ("slim", "Dell Pro Slim Plus", "Dell", "Desktop", "https://www.dell.com/en-us/shop/desktop-computers/dell-pro-slim-plus-desktop/spd/dell-pro-qbs1250-plus-slim-desktop"),
    ("qvt", "Dell Pro Tower Essential", "Dell", "Desktop", "https://www.dell.com/en-us/shop/desktop-computers/dell-pro-tower-essential-desktop/spd/dell-pro-qvt1260-desktop"),
    ("e2426", "Dell Pro 24 Video Conferencing Monitor", "Dell", "Monitor", "https://www.dell.com/en-us/shop/monitors/apd/dell-pro-24-video-conferencing-monitor-e2426hb/e2426hb/-"),
    ("p2226h", "Dell Pro P 22 Monitor", "Dell", "Monitor", "https://www.dell.com/en-us/shop/dell-pro-p-22-monitor-p2226h/apd/210-bvsl/monitors-monitor-accessories"),
    ("p1425", "Dell Pro 14 Plus Portable Monitor", "Dell", "Portable Monitor", "https://www.dell.com/en-us/shop/dell-pro-14-plus-portable-monitor-p1425/apd/210-bqjt/monitors-monitor-accessories"),
]
# Clients with a range of work: a feature row in the popup, with a big view that swaps as you point at each variant.
# Each is (model, work, count, unit, link, variants); a variant is (image in images/hmx/var, label, swatch colour or None).
CLIENT_RANGES = {
    "McLaren": ("Artura", "MSO Contrast Packs", "12", "MSO colours", "https://www.mclarentampabay.com/configure-artura.html", [
        ("mso-volcanored", "Volcano Red", "#9b1420"), ("mso-volcanoorange", "Volcano Orange", "#b8461a"),
        ("mso-anniversaryorange", "Anniversary Orange", "#e8800f"), ("mso-solaryellow", "Solar Yellow", "#f4c430"),
        ("mso-napiergreen", "Napier Green", "#8fc91c"), ("mso-xpgreen", "XP Green", "#0f4a44"),
        ("mso-tokyopearl", "Tokyo Pearl", "#2fd3cf"), ("mso-violaviola", "Viola Viola", "#4a2a5c"),
        ("mso-dovegrey", "Dove Grey", "#a8acae"), ("mso-sohogrey", "Soho Grey", "#5f6767"),
        ("mso-tarmacblack", "Tarmac Black", "#1c1d1f"), ("mso-alaskandiamond", "Alaskan Diamond", "#eef0f2"),
    ]),
    "Royal Enfield": ("Classic 350, Meteor 350 & Guerrilla 450", "Colourways", "6", "colourways",
                      "https://makeityours.royalenfield.com/configurator/guerrilla-450/", [
        ("re-k2f3-apexred", "Guerrilla 450 · Apex Red", None), ("re-k2f3-apexgreen", "Guerrilla 450 · Apex Green", None),
        ("re-k2f3-apexgrey", "Guerrilla 450 · Apex Grey", None), ("re-j1d5-halycon-black", "Meteor 350 · Halcyon Black", None),
        ("re-j1a5-redditch-grey", "Classic 350 · Redditch Grey", None), ("re-j1a5-chrome-bronze", "Classic 350 · Chrome Bronze", None),
    ]),
    "C.L. Seifert": ("Student caps", "Configurators", "3", "countries", "https://clseifert.com/dk/wizard", [
        ("cap-dk", "Denmark · Studenterhue", None), ("cap-se", "Sweden · Studentmössa", None),
        ("cap-fi", "Finland · Ylioppilaslakki", None),
    ]),
}

BUILDS_SHOWN = 12  # the rest open with "Show all"

# Case studies: short write-ups for the strongest projects. Content comes from each project's README.
CASES = {
    "Pipeline Tools @ HMX": {
        "slug": "hmx-tools",
        "summary": "Small tools I built around the 3D work at HMX Media, so the team spends less time on repetitive file work and more on the actual 3D.",
        "image": None,
        "meta": [("type", "Work · tools"), ("stack", "Python · Blender API"), ("where", "HMX Media"),
                 ("used by", "the whole 3D team")],
        "what": [
            "A lot of 3D production is file work: the same steps on every asset, for every client. "
            "I build small tools that take those steps off the team's plate.",
            "I write them with AI as a co-pilot. I know the pipeline, so I know exactly what to ask for "
            "and how to check what comes back. That's what makes them quick to build.",
        ],
        "steps_title": "What I built",
        "steps": [
            ("files", "2–3 tools for file operations that the team used to do by hand."),
            ("add-ons", "2 Blender add-ons, built into the team's everyday Blender setup."),
            ("scripts", "A steady stream of Blender Python scripts for my own work, whenever something repeats."),
        ],
        "facts_title": "In short",
        "facts": [("tools", "2–3 file tools and 2 Blender add-ons"), ("used by", "the whole 3D team"),
                  ("built with", "Python, the Blender API and AI"), ("why", "less repetitive work on every asset")],
        "note": "",
    },
    "PDF Q&A": {
        "slug": "pdf-qa",
        "summary": "Drop in a PDF and ask it questions in plain English. Every answer comes with the passages it was based on, so you can check it.",
        "image": ("pdfqa.webp", "PDF Q&A: asking a question about an uploaded document"),
        "meta": [("type", "AI app"), ("stack", "Python · Streamlit · FAISS · sentence-transformers · Groq"),
                 ("model", "Llama 3.3 70B"), ("hosted", "Streamlit Cloud")],
        "what": [
            "Upload a PDF of up to about 200 pages and ask anything about it. The app finds the parts of the document "
            "that matter for your question, hands them to an LLM and shows the answer next to the exact chunks it used.",
            "It also remembers the conversation, so follow-up questions work the way you'd expect.",
        ],
        "steps_title": "How it works",
        "steps": [
            ("read", "Pulls the text out of the PDF with PyPDF2 and cleans it up."),
            ("split", "Cuts it into ~1000-character chunks with 200 characters of overlap, breaking on sentence boundaries so ideas don't get cut in half."),
            ("embed", "Turns every chunk into a 384-dimension vector with a small sentence-transformers model (MiniLM)."),
            ("index", "Stores the vectors in a FAISS index for exact similarity search."),
            ("search", "Embeds the question the same way and pulls the 3 closest chunks."),
            ("answer", "Sends those chunks and the question to Llama 3.3 70B through the Groq API, then shows the answer with its sources."),
        ],
        "facts_title": "Numbers",
        "facts": [("answers", "under 2 seconds per question"), ("indexing", "30–60 seconds per document, on CPU"),
                  ("size", "up to ~200 pages"), ("chunks", "about 40–60 per document")],
        "note": "The code is split into small modules that each do one job: config, PDF processing, chunking, "
                "embeddings, the vector store, retrieval, LLM calls and one that ties them together.",
    },
    "Asset Viewer": {
        "slug": "asset-viewer",
        "summary": "A 3D model viewer that runs on your own machine. Drop in a model and inspect it: no uploads, no accounts.",
        "image": ("assetviewer.webp", "Asset Viewer with a model loaded"),
        "meta": [("type", "Tool"), ("stack", "Three.js · Flask · PyQt5 · PyInstaller"), ("runs on", "Windows (.exe)")],
        "what": [
            "Drag in a GLB, GLTF, FBX or OBJ and it loads straight away. It shows the mesh stats you usually go looking for "
            "and gives you the basic inspection tools: orbit and pan, wireframe, a grid and HDRI lighting with presets or your own HDRI.",
            "It ships as a standalone Windows app, so nobody needs Python installed to use it.",
        ],
        "steps_title": "How it's built",
        "steps": [
            ("render", "Three.js does the 3D: loading the formats, lighting, orbit controls, wireframe and grid."),
            ("serve", "A small Flask server hosts the viewer locally, so files never leave the machine."),
            ("wrap", "PyQt5's QWebEngine turns it into a desktop window instead of a browser tab."),
            ("ship", "PyInstaller packages everything (the viewer, HDRIs and sample models) into a folder with an .exe."),
        ],
        "facts_title": "Features",
        "facts": [("formats", "GLB · GLTF · FBX · OBJ"), ("stats", "objects, vertices, faces, triangles, file size"),
                  ("lighting", "HDRI presets or upload your own"), ("view", "orbit, pan, auto-rotate, wireframe, grid"),
                  ("themes", "light and dark")],
        "note": "",
    },
}

# The 27 renders, in gallery order: name (images/work/<name>.webp), title, kind, tags and thumbnail size
renders = json.loads((root / "_build" / "renders.json").read_text(encoding="utf-8"))
assert len(renders) == 27
by_render = {r["name"]: r for r in renders}
cat_of = {"Prop": "props", "Weapon": "weapons", "Environment": "environments"}

RESUME = "https://drive.google.com/file/d/1beKRxJsIhH8V-t0NbYfZ4qD8lMVYGmjG/view?usp=share_link"
# Email is split so the address never appears whole in the HTML; script.js assembles it
EMAIL_USER, EMAIL_DOMAIN = "kartik.dhasmana001", "gmail.com"
TOOLS = ["Blender", "Substance 3D", "ZBrush", "Maya", "Unity", "Unreal Engine", "Python", "C#", "PySide6",
         "Flask", "FastAPI", "PyTorch", "FAISS", "Streamlit", "GitHub Actions", "Pytest"]
SOCIALS = [("GitHub", "https://github.com/kaydee001"), ("ArtStation", "https://www.artstation.com/kaydee001"),
           ("LinkedIn", "https://www.linkedin.com/in/kartik-dhasmana-852331192/"),
           ("Instagram", "https://www.instagram.com/kd_renders_3d/")]

LIBS = """    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
    <script src="https://unpkg.com/lenis@1.1.13/dist/lenis.min.js" defer></script>
    <script src="script.js" defer></script>
"""


# ---------------------------------------------------------------- chrome
# Where the site is published (GitHub Pages); link previews need absolute URLs
SITE = "https://kaydee001.github.io/"


def head(title, desc, path=""):
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{desc}" />
    <title>{title}</title>
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Kartik Dhasmana" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{desc}" />
    <meta property="og:url" content="{SITE}{path}" />
    <meta property="og:image" content="{SITE}images/og.png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <link rel="icon" href="images/KD.png" />
    <script>
      // Theme before first paint: saved choice, else the OS preference
      try {{
        var saved = localStorage.getItem('theme')
        document.documentElement.dataset.theme =
          saved || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')
        // Boot sequence plays once per browser session
        if (!sessionStorage.getItem('booted') && !matchMedia('(prefers-reduced-motion: reduce)').matches)
          document.documentElement.classList.add('is-booting')
      }} catch (e) {{}}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&display=swap"
    />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <canvas class="bg-field" id="bg-field" aria-hidden="true"></canvas>
    <div class="boot" id="boot" aria-hidden="true">
      <pre id="boot-log"></pre>
    </div>
"""


ICONS = {
    "about": '<circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" />',
    "projects": '<path d="m8 8-5 4 5 4M16 8l5 4-5 4M14 4l-4 16" />',
    "3d": '<path d="M12 2 3 7v10l9 5 9-5V7z" /><path d="m3 7 9 5 9-5M12 12v10" />',
    "contact": '<rect x="3" y="5" width="18" height="14" rx="1" /><path d="m3 7 9 6 9-6" />',
    "experience": '<rect x="3" y="7" width="18" height="13" rx="1" /><path d="M9 7V4h6v3M3 12h18" />',
    "resume": '<path d="M14 3H6v18h12V7z" /><path d="M14 3v4h4M9 13h6M9 17h6" />',
    "prev": '<path d="M19 12H5M11 6l-6 6 6 6" />',
    "next": '<path d="M5 12h14M13 6l6 6-6 6" />',
    "out": '<path d="M7 17 17 7M8 7h9v9" />',
    "search": '<circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />',
    "sun": '<circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />',
    "moon": '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />',
}


def icon(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def pager(prev, nxt, pos):
    """Small previous / next bar at the top of the sub-pages."""
    (ph, pt), (nh, nt) = prev, nxt
    return (
        f'<nav class="page-nav" aria-label="Pages">'
        f'<a href="{ph}" aria-label="Previous: {pt}">{icon("prev")}<span>{pt}</span></a>'
        f'<span class="page-pos">{pos}</span>'
        f'<a href="{nh}" aria-label="Next: {nt}"><span>{nt}</span>{icon("next")}</a>'
        f"</nav>"
    )


def telemetry():
    return """<div class="telemetry" aria-label="Status">
            <p class="status"><span class="pulse" aria-hidden="true"></span>Based in Pune, India</p>
            <dl>
              <div><dt>loc</dt><dd>18.52&deg;N 73.86&deg;E</dd></div>
              <div><dt>ist</dt><dd id="clock">--:--:--</dd></div>
              <div><dt>sys</dt><dd>online<span class="blink">_</span></dd></div>
            </dl>
          </div>"""


def palette(home):
    """Ctrl+K menu: jump to a section or page, or run an action. Links match the page it sits on."""
    sec = (lambda h: h) if home else (lambda h: "index.html" + h)

    def link(text, href, keys="", hint="", out=False):
        target = ' target="_blank" rel="noreferrer"' if out else ""
        return (f'        <li><a class="cmdk-item" href="{href}"{target} data-keys="{keys}">'
                f'{escape(text)}<span>{hint}{" &#8599;" if out else ""}</span></a></li>\n')

    def action(text, name, keys="", hint="", extra=""):
        return (f'        <li><button class="cmdk-item" type="button" data-action="{name}" data-keys="{keys}"{extra}>'
                f'{escape(text)}<span>{hint}</span></button></li>\n')

    groups = [
        ("go to", [
            link("About", sec("#about"), "me bio facts", "01"),
            link("Experience", sec("#experience"), "work jobs journey hmx myracle", "02"),
            link("Projects", sec("#work"), "builds code", "03"),
            link("Renders", sec("#art"), "3d art blender", "04"),
            link("Contact", sec("#contact"), "message hire talk", "05"),
        ]),
        ("pages", [
            link("All projects", "projects.html", "tools apps ai list", "page"),
            link("3D work", "3d.html", "renders art props weapons environments gallery", "page"),
            link("Pipeline Tools @ HMX", "hmx-tools.html", "case study blender add-ons", "case"),
            link("PDF Q&A", "pdf-qa.html", "case study rag ai", "case"),
            link("Asset Viewer", "asset-viewer.html", "case study three.js", "case"),
        ]),
        ("do", [
            action("Toggle theme", "theme", "light dark mode", "light / dark"),
            action("Copy email address", "email", "mail contact", "copy",
                   f' data-user="{EMAIL_USER}" data-domain="{EMAIL_DOMAIN}"'),
            link("Resume", RESUME, "cv pdf", "", out=True),
        ]),
        ("elsewhere", [link(t, u, "social", "", out=True) for t, u in SOCIALS]),
    ]
    items = "".join(f'        <li class="cmdk-group" role="presentation">{name}</li>\n' + "".join(rows) for name, rows in groups)
    return f"""
    <dialog data-lenis-prevent class="cmdk panel" id="cmdk" aria-label="Command menu">
      <label class="cmdk-input"><span aria-hidden="true">&gt;</span><input id="cmdk-q" type="text" placeholder="Jump to..." autocomplete="off" spellcheck="false" /><kbd>esc</kbd></label>
      <ul class="cmdk-list" id="cmdk-list">
{items}      </ul>
      <p class="cmdk-empty" id="cmdk-empty" hidden>Nothing matches that.</p>
      <p class="cmdk-foot"><span><kbd>&uarr;</kbd><kbd>&darr;</kbd> move</span><span><kbd>enter</kbd> open</span><span><kbd>ctrl</kbd><kbd>k</kbd> toggle</span></p>
    </dialog>
"""


def rail(active):
    """Slim icon rail with a number under each icon; the label shows as a tooltip on hover or keyboard focus.

    On the homepage every link scrolls to its section; on the sub-pages Projects and 3D are the pages themselves.
    """
    home = active is None
    items = [("01", "#about" if home else "index.html#about", "About", "about"),
             ("02", "#experience" if home else "index.html#experience", "Experience", "experience"),
             ("03", "#work" if home else "projects.html", "Projects", "projects"),
             ("04", "#art" if home else "3d.html", "3D", "3d"),
             ("05", "#contact" if home else "index.html#contact", "Contact", "contact")]
    nav = "".join(
        f'        <a class="nav-link{" is-active" if key == active else ""}" href="{href}">{icon(key)}'
        f'<span class="nav-num">{n}</span><span class="rail-tip">{text}</span></a>\n'
        for n, href, text, key in items
    )
    return f"""    <header class="rail">
      <a class="rail-brand" href="index.html" aria-label="Kartik Dhasmana home">
        <img src="images/KD.png" alt="" width="40" height="40" />
        <span class="rail-tip">Kartik Dhasmana</span>
      </a>

      <nav class="rail-nav" aria-label="Primary">
{nav}        <a class="nav-link" href="{RESUME}" target="_blank" rel="noreferrer">{icon("resume")}<span class="nav-num">06</span><span class="rail-tip">Resume &#8599;</span></a>
      </nav>

      <button class="nav-link cmdk-btn" id="cmdk-open" type="button" aria-label="Open the command menu (Ctrl K)">
        {icon("search")}<span class="rail-tip">Menu &middot; Ctrl K</span>
      </button>

      <button class="nav-link theme-btn" id="theme-toggle" type="button" aria-label="Toggle light and dark theme">
        {icon("sun", "icon icon-sun")}{icon("moon", "icon icon-moon")}<span class="rail-tip">Theme</span>
      </button>
    </header>
{palette(home)}
    <main class="main">
"""


social_links = "".join(f'<a href="{u}" target="_blank" rel="noreferrer">{t}</a>' for t, u in SOCIALS)

FOOT = f"""      <footer class="foot">
        <p>&copy; <span id="year">2026</span> Kartik Dhasmana</p>
        <div class="foot-links">{social_links}</div>
        <a href="#" data-top>Back to top &uarr;</a>
      </footer>
    </main>


    <dialog data-lenis-prevent class="viewer" id="viewer" aria-label="Image viewer">
      <div class="viewer-stage"><img id="viewer-image" alt="" /></div>
      <aside class="viewer-info">
        <p class="label"><span id="viewer-count">[01 / 01]</span> <span id="viewer-what">render</span></p>
        <h3 id="viewer-title"></h3>
        <p class="viewer-kind" id="viewer-kind"></p>
        <p class="viewer-sub" id="viewer-sub">Made with</p>
        <ul class="viewer-tags" id="viewer-tags"></ul>
        <a class="more" href="https://www.artstation.com/kaydee001" target="_blank" rel="noreferrer">More on ArtStation &#8599;</a>
        <div class="viewer-controls">
          <button type="button" id="viewer-prev" aria-label="Previous image">&larr;</button>
          <button type="button" id="viewer-next" aria-label="Next image">&rarr;</button>
          <button type="button" id="viewer-close" aria-label="Close">esc</button>
        </div>
        <p class="viewer-hint">Arrow keys to browse</p>
      </aside>
    </dialog>

"""


def section_label(num, text):
    return f'<p class="label"><span>[{num}]</span> {text}</p>'


def journey_stop(s):
    """One stop on the track: a monogram node, the role and why, then the results."""
    def win(stat, unit, what, how, link):
        return f"""                <li>
                  <p class="xp-stat">{escape(stat)}<span>{escape(unit)}</span></p>
                  <p class="xp-what">{escape(what)}</p>
                  <p class="xp-how">{escape(how)}</p>
                </li>
"""

    wins = "".join(win(*w) for w in s["wins"])
    now = s["tag"] == "now"
    until = f' data-until="{s["until"]}"' if s["until"] else ""
    return f"""            <li class="stop{" is-now" if now else ""} reveal">
              <span class="stop-node" aria-hidden="true">{s["mark"]}</span>
              <div class="stop-card panel">
              <div class="stop-meta">
                <p class="xp-when"><span class="xp-dates">{escape(s["when"])}</span><span class="xp-span" data-since="{s["since"]}"{until}></span></p>
                <h3>{escape(s["role"])}</h3>
                <p class="stop-where"><strong>{escape(s["where"].split(" · ")[0])}</strong> · {escape(s["where"].split(" · ")[1])}</p>
                <p class="stop-why">{escape(s["why"])}</p>
              </div>
              <ul class="xp-wins">
{wins}              </ul>
{builds_block(s)}              </div>
            </li>
"""


def also_html(text):
    """The closing line, with its leading count picked out in the accent."""
    count, rest = text.split(" ", 1)
    return f"<b>{escape(count)}</b> {escape(rest)}"


def thumb(slug, name):
    """The product shot, or a terminal tile with the name until a shot is added to images/hmx/."""
    if (root / "images" / "hmx" / f"{slug}.webp").exists():
        return f'<img src="images/hmx/{slug}.webp" alt="{escape(name)}, 3D product viewer" loading="lazy" />'
    return f'<span class="build-blank" aria-hidden="true">&gt; {escape(slug)}</span>'


def builds_block(s):
    """Selected client work under the stats: one card of each kind, and "Show all" opens the full list in a popup."""
    if not s.get("builds"):
        return ""
    items = globals()[s["builds"]]

    def card(slug, name, brand, scope, url, cls="build-card"):
        return (f'<a class="{cls}" href="{url}" target="_blank" rel="noreferrer">{thumb(slug, name)}'
                f'<span class="build-name">{escape(name)}</span>'
                f'<span class="build-meta">{brand} · {scope} <span aria-hidden="true">&#8599;</span></span></a>')

    # The popup: one row per client, like the skills list
    order = ["McLaren", "Royal Enfield", "C.L. Seifert", "Lenovo", "Dell"]
    brands = sorted({it[2] for it in items}, key=lambda b: order.index(b) if b in order else len(order))
    def pick_button(i, img, label, sw):
        cls = "range-pick" + (" is-on" if i == 0 else "") + (" is-swatch" if sw else "")
        attrs = f'data-src="images/hmx/var/{img}.webp" data-label="{escape(label)}" aria-label="{escape(label)}" title="{escape(label)}"'
        if sw:
            return f'<button class="{cls}" type="button" {attrs} style="--sw: {sw}"></button>'
        return f'<button class="{cls}" type="button" {attrs}><img src="images/hmx/var/{img}.webp" alt="" loading="lazy" /></button>'

    def range_row(n, b):
        model, work, count, unit, url, variants = CLIENT_RANGES[b]
        picks = "".join(pick_button(i, *v) for i, v in enumerate(variants))
        return f"""          <div class="work-group is-range"><h3><span>{n:02d}</span> {escape(b)}</h3>
            <div class="range">
              <a class="range-view" href="{url}" target="_blank" rel="noreferrer">
                <img src="images/hmx/var/{variants[0][0]}.webp" alt="{escape(b)} {escape(model)}" loading="lazy" />
                <span class="range-label">{escape(variants[0][1])}</span>
              </a>
              <div class="range-side">
                <p class="range-model">{escape(model)}<span>{escape(work)} &#8599;</span></p>
                <p class="xp-stat">{count}<span>{escape(unit)}</span></p>
                <div class="range-picks" role="group" aria-label="{escape(b)} variants">{picks}</div>
              </div>
            </div>
          </div>
"""

    def grid_row(n, b):
        return f"""          <div class="work-group"><h3><span>{n:02d}</span> {escape(b)}<em>{sum(1 for it in items if it[2] == b)}</em></h3>
            <ul>{"".join(f"<li>{card(*it, cls='build-card is-small')}</li>" for it in items if it[2] == b)}</ul>
          </div>
"""

    rows = "".join((range_row if b in CLIENT_RANGES else grid_row)(n, b) for n, b in enumerate(brands, 1))
    # The launcher: a slow reel of the work behind the count, and the whole panel opens the gallery
    shots = [it for it in items[:BUILDS_SHOWN] if (root / "images" / "hmx" / f"{it[0]}.webp").exists()]
    frames = "".join(f'<img src="images/hmx/{it[0]}.webp" alt="" loading="lazy" />' for it in shots)
    return f"""              <div class="xp-builds">
                <button class="work-reel" id="work-open" type="button" aria-haspopup="dialog">
                  <span class="work-reel-info">
                    <span class="work-reel-label">Selected work</span>
                    <span class="xp-stat">{len(items)}<span>products · {len(brands)} brands</span></span>
                    <span class="work-reel-brands">{" · ".join(escape(b) for b in brands)}</span>
                    <span class="work-reel-cta">Open gallery <span aria-hidden="true">&rarr;</span></span>
                  </span>
                  <span class="work-reel-strip" aria-hidden="true"><span class="work-reel-track">{frames}{frames}</span></span>
                </button>
                <p class="xp-also">{also_html(s["also"])}</p>
              </div>
              <dialog data-lenis-prevent class="skills panel work-all" id="work-all" aria-labelledby="work-title">
                <div class="skills-head">
                  <p class="label"><span>[~]</span> hmx media</p>
                  <button class="icon-btn" id="work-close" type="button" aria-label="Close">&times;</button>
                </div>
                <h2 id="work-title" tabindex="-1">All client work</h2>
                <div class="work-list">
{rows}                </div>
              </dialog>
"""

def feature_card(name, num):
    """A project card: screenshot on top (or a terminal tile with its tag), then the pitch, the stack and the ways in."""
    b = by_build[name]
    case = CASES.get(name)
    href = f'{case["slug"]}.html' if case else b[5][0][1]
    out = "" if case else ' target="_blank" rel="noreferrer"'
    links = "".join(f'<a class="btn" href="{u}" target="_blank" rel="noreferrer">{t} &#8599;</a>' for t, u in b[5])
    if case:
        links = f'<a class="btn" href="{href}">Case study &rarr;</a>' + links
    if b[2].endswith(".webp"):
        shot = f'<img src="images/projects/{b[2]}" alt="" loading="lazy" />'
        kind = ""
    else:
        shot = f"<span>{escape(b[2])}</span>"
        kind = " is-code"
    return f"""            <article class="feature panel reveal" data-category="{b[1]}">
              <a class="feature-shot{kind}" href="{href}"{out} tabindex="-1" aria-hidden="true">
                {shot}
              </a>
              <div class="feature-body">
                <p class="feature-tag"><span>{num:02d}</span> {labels[b[1]]}</p>
                <h3><a href="{href}"{out}>{escape(name)}</a></h3>
                <p class="muted">{escape(b[3])}</p>
                <p class="feature-stack">{"".join(f"<span>{escape(t)}</span>" for t in b[4].split(" · "))}</p>
                <div class="actions">{links}</div>
              </div>
            </article>
"""


def render_tile(r):
    return f"""            <figure class="tile reveal" data-category="{cat_of[r['kind']]}">
              <a class="tile-link" href="images/work/{r['name']}.webp" data-title="{escape(r['title'])}" data-kind="{r['kind']}" data-tags="{escape(r['tags'])}">
                <img src="images/work/thumbs/{r['name']}.webp" alt="{escape(r['title'])}" width="{r['w']}" height="{r['h']}" loading="lazy" />
              </a>
              <figcaption><span>{escape(r['title'])}</span><span>{r['kind']}</span></figcaption>
            </figure>
"""


def strip_panel(r, num):
    return f"""            <figure class="strip-item">
              <a class="tile-link" href="images/work/{r['name']}.webp" data-title="{escape(r['title'])}" data-kind="{r['kind']}" data-tags="{escape(r['tags'])}">
                <img src="images/work/thumbs/{r['name']}.webp" alt="{escape(r['title'])}" width="{r['w']}" height="{r['h']}" loading="lazy" />
              </a>
              <figcaption><span>{num:02d}</span>{escape(r['title'])}<span>{r['kind']}</span></figcaption>
            </figure>
"""


def chips(options, label):
    btns = '<button class="chip is-active" type="button" data-filter="all">All</button>'
    btns += "".join(f'<button class="chip" type="button" data-filter="{k}">{v}</button>' for k, v in options)
    return f'<div class="chips" role="group" aria-label="{label}">{btns}</div>'


marquee_items = "".join(f"<span>{t}</span>" for t in TOOLS)

# Full skill list for the "what i know" popup, grouped as on the resume
SKILLS = [
    ("3D", ["Blender", "Substance 3D", "ZBrush", "Maya", "Marmoset Toolbag", "Octane", "Cycles / EEVEE"]),
    ("Engines", ["Unity", "Unreal Engine"]),
    ("Code", ["Python", "C#", "C++", "SQL", "Blender Python API", "PySide6", "Flask", "FastAPI", "REST APIs"]),
    ("AI / ML", ["PyTorch", "Computer Vision", "LLM Apps", "RAG", "FAISS", "Groq API", "Streamlit"]),
    ("Workflow", ["Git", "GitHub Actions", "Pytest", "CI Pipelines", "Jira", "ClickUp", "Trello", "ftrack"]),
]
skill_groups = "".join(
    f'          <div class="skill-group"><h3><span>{n:02d}</span> {g}</h3><ul>'
    + "".join(f'<li class="tag">{escape(i)}</li>' for i in items)
    + "</ul></div>\n"
    for n, (g, items) in enumerate(SKILLS, 1)
)
skills_dialog = f"""    <dialog data-lenis-prevent class="skills panel" id="skills" aria-labelledby="skills-title">
      <div class="skills-head">
        <p class="label"><span>[~]</span> skills</p>
        <button class="icon-btn" id="skills-close" type="button" aria-label="Close">&times;</button>
      </div>
      <h2 id="skills-title" tabindex="-1">What I know</h2>
      <div class="skill-grid">
{skill_groups}      </div>
    </dialog>

"""

MADE_WITH = ["Blender", "ZBrush", "Substance 3D Painter", "Marmoset Toolbag"]
made_with = ('<p class="made-with"><span>Made with</span>'
             + "".join(f'<span class="tag">{t}</span>' for t in MADE_WITH) + "</p>")

# ---------------------------------------------------------------- index
FEATURED = ["PDF Q&A", "Asset Viewer", "Git Client", "QueryMate"]
home_renders = ["room", "onii", "fire", "tori", "skull", "lofi", "axe", "iceberg"]

index = head("Kartik Dhasmana", "Kartik Dhasmana: real-time artist from Pune. I make 3D stuff, tools and whatever else I get curious about.") + rail(None) + f"""      <!-- Hero: live viewport with the intro laid over it -->
      <section class="hero frame" id="top">
        <div class="viewport" id="viewport" aria-hidden="true">
          <canvas id="viewport-canvas"></canvas>
          <span class="hud hud-tl">iso · ortho</span>
          <div class="hud hud-tr">
            <span>kd_mesh.001</span>
            <span id="hud-stats">verts 0 · faces 0</span>
            <span id="hud-fps">-- fps</span>
          </div>
        </div>

        <div class="hero-copy">
          {section_label("00", "hello world")}
          <h1 class="console" id="hero-title">Hi, I'm Kartik :)</h1>
          <p class="lede">I make 3D stuff, tools and whatever else I get curious about.</p>
          <div class="actions">
            <a class="btn btn-primary" href="projects.html">See what I've made</a>
            <a class="btn" href="#contact">Get in touch</a>
          </div>
        </div>

        <div class="hero-side">
          {telemetry()}
        </div>

        <a class="scroll-hint" href="#about" aria-label="Scroll to About">scroll <span aria-hidden="true">&darr;</span></a>
      </section>

      <div class="skillbar">
        <button class="skill-open" id="skills-open" type="button" aria-haspopup="dialog">
          <span>what i know</span>{icon("next")}
        </button>
        <div class="marquee" aria-hidden="true">
          <div class="marquee-track">{marquee_items}{marquee_items}</div>
        </div>
      </div>

      <!-- About -->
      <section class="section" id="about" data-num="01">
        <div class="wrap about">
          <div>
            {section_label("01", "about")}
            <h2 data-scramble>A bit about me</h2>
            <div class="prose">
              <p>
                I'm a real-time artist. I make 3D for the web and AR, and I build tools that
                help teams work faster. Outside of work, I make small apps and AI projects,
                mostly to see how things work.
              </p>
              <p>
                I studied computer science, with a focus on gaming tech, at VIT Bhopal. My first
                job was making AR lessons for school kids at Myracle.io, which was featured on
                Shark Tank India. I've been doing 3D since college, and I started coding to skip
                the boring parts.
              </p>
              <p>
                If I see something cool, I try to make my own version. Most of it ends up on
                <a href="https://github.com/kaydee001" target="_blank" rel="noreferrer">GitHub</a>.
              </p>
              <p class="small">The formal version is on my <a href="{RESUME}" target="_blank" rel="noreferrer">resume</a>.</p>
            </div>
          </div>

          <dl class="facts panel glow">
            <div><dt>Focus</dt><dd>3D, tools, code and AI</dd></div>
            <div><dt>Experience</dt><dd>4+ years in real-time 3D</dd></div>
            <div><dt>Open to</dt><dd>Roles where 3D, tools and code meet</dd></div>
            <div><dt>Learning</dt><dd>Whatever looks interesting this week</dd></div>
            <div><dt>Tools</dt><dd>VS Code, Blender and Claude</dd></div>
            <div><dt>Music</dt><dd>All kinds, all the time</dd></div>
            <div><dt>Off hours</dt><dd>Games, anime and sports with my boys</dd></div>
          </dl>
        </div>
      </section>

      <!-- Experience: the journey so far -->
      <section class="section" id="experience" data-num="02">
        <div class="wrap">
          <div class="section-top">
            <div>
              {section_label("02", "experience")}
              <h2 data-scramble>The journey so far</h2>
            </div>
          </div>
          <ol class="journey">
            <li class="stop is-next">
              <span class="stop-node" aria-hidden="true">?</span>
              <a class="stop-next" href="#contact">Next stop: open to what's next {icon("next")}</a>
            </li>
{"".join(journey_stop(s) for s in reversed(JOURNEY))}          </ol>
        </div>
      </section>

      <!-- Projects: the lead cards -->
      <section class="section" id="work" data-num="03">
        <div class="wrap">
          <div class="section-top">
            <div>
              {section_label("03", "projects")}
              <h2 data-scramble>Recent builds</h2>
            </div>
            <a class="more" href="projects.html"><span class="more-count">{len(FEATURED)} of {len(builds)}</span> View all &rarr;</a>
          </div>
          <div class="features">
{"".join(feature_card(n, i) for i, n in enumerate(FEATURED, 1))}          </div>
        </div>
      </section>

      <!-- 3D: carousel inside the page margins (autoplays; swipe, drag or the arrow buttons) -->
      <section class="section strip" id="art" data-num="04">
        <div class="wrap">
          <div class="section-top">
            <div>
              {section_label("04", "3d")}
              <h2 data-scramble>Renders</h2>
              {made_with}
            </div>
            <div class="strip-controls">
              <a class="more" href="3d.html"><span class="more-count">{len(home_renders)} of {len(renders)}</span> View all &rarr;</a>
              <button class="icon-btn" id="strip-prev" type="button" aria-label="Previous render">{icon("prev")}</button>
              <button class="icon-btn" id="strip-next" type="button" aria-label="Next render">{icon("next")}</button>
            </div>
          </div>
          <div class="strip-view">
            <div class="strip-track">
{"".join(strip_panel(by_render[n], i) for i, n in enumerate(home_renders, 1))}            </div>
          </div>
        </div>
      </section>

      <!-- Contact: terminal -->
      <section class="section" id="contact" data-num="05">
        <div class="wrap contact">
          <div>
            {section_label("05", "contact")}
            <h2 data-scramble>Get in touch</h2>
            <p class="muted">Got a project or a job, or just want to talk 3D, tools or AI? Send me a message or an email.</p>
            <div class="mail-row">
              <a class="mail" href="#contact" data-user="{EMAIL_USER}" data-domain="{EMAIL_DOMAIN}">Email me <span aria-hidden="true">&#8599;</span></a>
              <button class="copy-mail" id="copy-mail" type="button">Copy address</button>
            </div>
          </div>

          <div class="term panel">
            <div class="term-bar" aria-hidden="true">
              <span class="term-dots"><i></i><i></i><i></i></span>
              <span>~/contact</span>
              <span class="term-state" id="term-state">0/3</span>
            </div>
            <form class="term-form" id="contact-form" method="post" action="https://api.web3forms.com/submit">
              <input type="hidden" name="access_key" value="fb73c820-dc81-48dd-b364-13fc17c859a2" />
              <p class="term-note">// Leave a message and I'll get back to you.</p>
              <label class="term-line"><span>&gt; Name:</span><input type="text" name="name" autocomplete="name" required /></label>
              <label class="term-line"><span>&gt; Email:</span><input type="email" name="email" autocomplete="email" required /></label>
              <label class="term-line is-multi"><span>&gt; Message:</span><textarea name="message" rows="4" required></textarea></label>
              <div class="form-end">
                <button class="btn btn-primary" type="submit">[ Send ]</button>
                <p class="form-status" id="form-status" role="status"></p>
              </div>
            </form>
          </div>
        </div>
      </section>

""" + FOOT + skills_dialog + LIBS + """    <script type="importmap">
      { "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js", "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/" } }
    </script>
    <script type="module" src="viewport.js"></script>
  </body>
</html>
"""


def page_head(pos, prev, nxt, num, label, title, blurb, chip_html):
    return f"""      <section class="section page-head">
        <div class="wrap">
          {pager(prev, nxt, pos)}
          <div class="page-head-grid">
            <div>
              {section_label(num, label)}
              <h1 data-scramble>{title}</h1>
              <p class="muted">{blurb}</p>
              {chip_html}
            </div>
          </div>
        </div>
      </section>
"""


# ---------------------------------------------------------------- projects
projects = head("Projects | Kartik Dhasmana", "Tools, apps and AI experiments by Kartik Dhasmana.", "projects.html") + rail("projects") + page_head(
    "03 / 04", ("index.html", "Home"), ("3d.html", "3D work"), "03", "projects", "Things I've made",
    "Tools, apps and AI experiments. Some finished, some still in progress.",
    chips([("tools", "Tools"), ("apps", "Apps"), ("ai", "AI")], "Filter projects"),
) + f"""
      <section class="section is-tight">
        <div class="wrap">
          <div class="features is-dense">
{"".join(feature_card(b[0], i) for i, b in enumerate(builds, 1))}          </div>
        </div>
      </section>

""" + FOOT + LIBS + """  </body>
</html>
"""

# ---------------------------------------------------------------- 3d
order = ["room", "tori", "lofi", "axe", "skull", "onii", "fire", "iceberg", "museum", "abstract", "buster", "headphone"]
order += [r["name"] for r in renders if r["name"] not in order]
gallery = head("3D | Kartik Dhasmana", "3D props, weapons and environments by Kartik Dhasmana.", "3d.html") + rail("3d") + page_head(
    "04 / 04", ("projects.html", "Projects"), ("index.html#contact", "Contact"), "04", "3d", "3D work",
    "Props, weapons and environments. Click any render to see it full size.",
    made_with + chips([("props", "Props"), ("weapons", "Weapons"), ("environments", "Environments")], "Filter renders"),
) + f"""
      <section class="section is-tight">
        <div class="wrap">
          <div class="tiles is-masonry">
{"".join(render_tile(by_render[n]) for n in order)}          </div>
          <a class="more" href="https://www.artstation.com/kaydee001" target="_blank" rel="noreferrer">More on ArtStation &#8599;</a>
        </div>
      </section>

""" + FOOT + LIBS + """  </body>
</html>
"""


# ---------------------------------------------------------------- case studies
def case_page(name, prev, nxt, pos):
    c = CASES[name]
    _, cat, _, _, _, links = by_build[name]
    buttons = "".join(
        f'<a class="btn{" btn-primary" if i == 0 else ""}" href="{u}" target="_blank" rel="noreferrer">{t} &#8599;</a>'
        for i, (t, u) in enumerate(links)
    )
    meta = "".join(f"<div><dt>{k}</dt><dd>{escape(v)}</dd></div>" for k, v in c["meta"])
    what = "".join(f"<p>{escape(p)}</p>" for p in c["what"])
    steps = "".join(f"<li><b>{k}</b><span>{escape(v)}</span></li>" for k, v in c["steps"])
    facts = "".join(f"<div><dt>{k}</dt><dd>{escape(v)}</dd></div>" for k, v in c["facts"])
    note = f'<p class="case-note">{escape(c["note"])}</p>' if c["note"] else ""
    fig_block, fig_script = "", ""
    if c.get("figure"):
        fragment, script, heading = c["figure"]
        fig_block = f"""<div class="case-block case-fig">
            <h2>{heading}</h2>
            {(out / fragment).read_text(encoding="utf-8")}
          </div>"""
        fig_script = f'    <script type="module" src="{script}"></script>\n'
    shot = ""
    if c["image"]:
        img, alt = c["image"]
        shot = f"""<figure class="case-shot">
            <a class="tile-link" href="images/projects/{img}" data-title="{escape(name)}" data-kind="{escape(dict(c["meta"]).get("type", ""))}" data-tags="{escape(dict(c["meta"]).get("stack", ""))}" data-label="screenshot" data-sub="Built with">
              <img src="images/projects/{img}" alt="{escape(alt)}" />
            </a>
          </figure>"""
    return head(f"{name} | Kartik Dhasmana", c["summary"], f'{c["slug"]}.html') + rail("projects") + f"""      <section class="section page-head">
        <div class="wrap">
          {pager(prev, nxt, pos)}
          <div class="case-head">
            <div>
              {section_label("03", f"{labels[cat]} · case study")}
              <h1 data-scramble>{escape(name)}</h1>
              <p class="lede">{escape(c["summary"])}</p>
              <div class="actions">{buttons}</div>
            </div>
            <dl class="case-meta panel">{meta}</dl>
          </div>
        </div>
      </section>

      <section class="section is-tight">
        <div class="wrap case">
          {shot}

          <div class="case-block">
            <h2>What it does</h2>
            {what}
          </div>

          {fig_block}

          <div class="case-block">
            <h2>{c["steps_title"]}</h2>
            <ol class="steps">{steps}</ol>
            {note}
          </div>

          <div class="case-block">
            <h2>{c["facts_title"]}</h2>
            <dl class="case-facts panel">{facts}</dl>
          </div>

          <a class="more" href="projects.html">&larr; All projects</a>
        </div>
      </section>

""" + FOOT + LIBS + fig_script + """  </body>
</html>
"""


case_pages = [
    ("hmx-tools.html", case_page("Pipeline Tools @ HMX", ("projects.html", "Projects"), ("pdf-qa.html", "PDF Q&A"), "case 01 / 03")),
    ("pdf-qa.html", case_page("PDF Q&A", ("hmx-tools.html", "Pipeline Tools @ HMX"), ("asset-viewer.html", "Asset Viewer"), "case 02 / 03")),
    ("asset-viewer.html", case_page("Asset Viewer", ("pdf-qa.html", "PDF Q&A"), ("projects.html", "Projects"), "case 03 / 03")),
]

for fname, html in [("index.html", index), ("projects.html", projects), ("3d.html", gallery)] + case_pages:
    (out / fname).write_text(html, encoding="utf-8", newline="")
    print(fname, html.count("<section"), html.count("</section>"), html.count("<div"), html.count("</div>"))
