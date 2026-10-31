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
# The model behind each AI project, shown in its badge
MODELS = {"PDF Q&A": "Llama 3.3 70B", "QueryMate": "Llama 3.3 70B", "DevDocs AI": "Llama 3.3 70B", "Image Classifiers": "ResNet18"}

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
             "For Dell and Lenovo alone, from model to interaction.", None),
            ("~35%", "lighter files", "Made models load faster",
             "Cleaned up UVs, baked AO and HDR lighting, and optimised meshes and textures.", None),
            ("4+", "team tools", "Took the busywork out of asset prep",
             "2 file tools and 2 Blender add-ons, used by the whole team. Built in Python, with AI as a co-pilot.", None),
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
        "summary": "Small tools I built around the 3D work at HMX Media, so the team spends less time on repetitive work and more on the actual 3D.",
        "image": None,
        "meta": [("type", "Work · tools"), ("stack", "Python · Blender API"), ("where", "HMX Media"),
                 ("used by", "the whole 3D team")],
        "what": [
            "Every 3D team has repetitive work that eats into the time for the actual 3D. "
            "I build small tools that take it off the team's plate.",
            "I write them with AI as a co-pilot. Knowing the 3D side means I know what to ask for "
            "and how to check what comes back, which makes them quick to build.",
        ],
        "steps_title": "What I built",
        # name, what it does, result
        "tools": [
            ("AR project setup tool", "Gets a new AR project set up and ready to work on.", "~30–40% less time"),
            ("Blender add-on for AR", "Brings common fixes for AR assets together in one place.", "~30–40% less time"),
            ("Blender add-on for real-time work", "Does the same for real-time assets.", "~30–40% less time"),
            ("File and screenshot tool", "Speeds up repetitive file work and screenshots.", "~30–40% less time"),
        ],
        "note": "Plus a steady stream of Blender Python scripts for my own work, whenever something repeats.",
        "facts_title": "In short",
        "facts": [("tools", "2 file tools and 2 Blender add-ons"), ("used by", "the whole 3D team"),
                  ("built with", "Python, the Blender API and AI"), ("why", "less repetitive work")],
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

# The resume: resume.pdf in the repo root once it's added (faster, never breaks), else the Drive copy
RESUME_DRIVE = "https://drive.google.com/file/d/1beKRxJsIhH8V-t0NbYfZ4qD8lMVYGmjG/view?usp=sharing"
RESUME = "resume.pdf" if (root / "resume.pdf").exists() else RESUME_DRIVE
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
    <link rel="icon" href="images/kd-icon.png" />
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
    <!-- The font loads without holding up the first paint; the mono fallback shows until it arrives -->
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&display=swap"
      media="print"
      onload="this.media='all'"
    />
    <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&display=swap" /></noscript>
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
    "home": '<path d="M3 11l9-7 9 7" /><path d="M5 9.5V20h14V9.5" /><path d="M10 20v-6h4v6" />',
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
        f'<span class="page-pos"><a class="page-home" href="index.html" aria-label="Home">{icon("home")}</a>{pos}</span>'
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
            link("3D", sec("#art"), "renders art blender", "04"),
            link("Contact", sec("#contact"), "message hire talk", "05"),
        ]),
        ("pages", [
            link("Client work @ HMX", "hmx-work.html", "hmx dell lenovo mclaren royal enfield seifert caps products", "page"),
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
        f'        <a class="nav-link{" is-active" if key == active else ""}" href="{href}" aria-label="{text}">{icon(key)}'
        f'<span class="nav-num">{n}</span><span class="rail-tip">{text}</span></a>\n'
        for n, href, text, key in items
    )
    return f"""    <header class="rail">
      <a class="rail-brand" href="index.html" aria-label="Kartik Dhasmana home">
        <img src="images/kd-80.webp" alt="" width="40" height="40" />
        <span class="rail-tip">Kartik Dhasmana</span>
      </a>

      <nav class="rail-nav" aria-label="Primary">
{nav}        <a class="nav-link" href="{RESUME}" target="_blank" rel="noreferrer" aria-label="Resume (opens in a new tab)">{icon("resume")}<span class="nav-num">06</span><span class="rail-tip">Resume &#8599;</span></a>
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
        <a class="btn" href="https://www.artstation.com/kaydee001" target="_blank" rel="noreferrer">More on ArtStation &#8599;</a>
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


CLIENT_WORK = {}


def builds_block(s):
    """Selected client work under the stats: a launcher that links to the full list on hmx-work.html."""
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
        return f'<button class="{cls}" type="button" {attrs}><img src="images/hmx/var/{img}.webp" alt="{escape(label)}" loading="lazy" /></button>'

    def range_row(n, b):
        model, work, count, unit, url, variants = CLIENT_RANGES[b]
        picks = "".join(pick_button(i, *v) for i, v in enumerate(variants))
        return f"""          <div class="work-group is-range"><h2><span>{n:02d}</span> {escape(b)}</h2>
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
        return f"""          <div class="work-group"><h2><span>{n:02d}</span> {escape(b)}<em>{sum(1 for it in items if it[2] == b)}</em></h2>
            <ul>{"".join(f"<li>{card(*it, cls='build-card is-small')}</li>" for it in items if it[2] == b)}</ul>
          </div>
"""

    rows = "".join((range_row if b in CLIENT_RANGES else grid_row)(n, b) for n, b in enumerate(brands, 1))
    # The full list goes on its own page (hmx-work.html), built after the index
    CLIENT_WORK.update(rows=rows, count=len(items), brands=brands, also=s["also"])
    # The launcher: a slow reel of the work behind the count, and the whole panel opens the gallery
    shots = [it for it in items[:BUILDS_SHOWN] if (root / "images" / "hmx" / f"{it[0]}.webp").exists()]
    frames = "".join(f'<img src="images/hmx/{it[0]}.webp" alt="{escape(it[1])}, 3D product viewer" loading="lazy" />' for it in shots)
    return f"""              <div class="xp-builds">
                <a class="work-reel" href="hmx-work.html">
                  <span class="work-reel-info">
                    <span class="work-reel-label">Selected work</span>
                    <span class="xp-stat">{len(items)}<span>products · {len(brands)} brands</span></span>
                    <span class="work-reel-brands">{" · ".join(escape(b) for b in brands)}</span>
                    <span class="work-reel-cta">See all client work <span aria-hidden="true">&rarr;</span></span>
                  </span>
                  <span class="work-reel-strip" aria-hidden="true"><span class="work-reel-track">{frames}{frames}</span></span>
                </a>
                <p class="xp-also">{also_html(s["also"])}</p>
              </div>
"""

# Line drawings for projects with no screenshot: what each one does, in a 320 x 180 box.
# Classes (styles.css): t-dim is the quiet line, t-soft a tinted fill, t-solid hides what's behind, t-dot a solid dot.
NN_LAYERS = [(90, [50, 90, 130]), (160, [39, 73, 107, 141]), (230, [70, 110])]
THUMBS = {
    "Pipeline Tools @ HMX": """
      <path class="t-dim t-solid" d="M56 48h30l14 14v50H56z" /><path class="t-dim t-solid" d="M64 56h30l14 14v50H64z" />
      <path class="t-solid" d="M72 64h30l14 14v50H72z" /><path d="M102 64v14h14M84 96h20M84 108h20M84 120h12" />
      <path class="t-dim" stroke-dasharray="4 6" d="M132 92h34" /><path d="M166 82l10 10-10 10" />
      <path class="t-soft" d="M230 48l38 22-38 22-38-22z" />
      <path d="M230 48l38 22v44l-38 22-38-22V70zM230 92v44M230 92l-38-22M230 92l38-22" />
      <circle class="t-dot" cx="230" cy="48" r="3" /><circle class="t-dot" cx="268" cy="70" r="3" /><circle class="t-dot" cx="192" cy="70" r="3" />
      <circle class="t-dot" cx="230" cy="92" r="3" /><circle class="t-dot" cx="268" cy="114" r="3" /><circle class="t-dot" cx="192" cy="114" r="3" /><circle class="t-dot" cx="230" cy="136" r="3" />""",
    "DevDocs AI": """
      <path class="t-soft" d="M60 46h44l18 18v70H60z" /><path d="M60 46h44l18 18v70H60zM104 46v18h18" />
      <text x="91" y="106" text-anchor="middle">.py</text>
      <path class="t-dim" stroke-dasharray="4 6" d="M140 90h30" /><path d="M170 80l10 10-10 10" />
      <rect x="198" y="40" width="72" height="100" rx="2" />
      <path d="M210 60h48M210 74h48" /><path class="t-dim" d="M210 88h48M210 102h32" /><path d="M212 122l7 7 13-15" />""",
    "File Ingestor": """
      <path class="t-soft" d="M44 62h28l12 12v44H44z" /><path d="M44 62h28l12 12v44H44zM72 62v12h12" />
      <path class="t-dim" d="M100 90h50M150 90c30 0 26-40 56-40M150 90c30 0 26 40 56 40" />
      <circle class="t-dot" cx="150" cy="90" r="5" />
      <rect x="212" y="30" width="64" height="40" rx="2" /><path d="M232 50l8 8 16-16" />
      <rect class="t-dim" stroke-dasharray="4 5" x="212" y="110" width="64" height="40" rx="2" /><path class="t-dim" d="M236 122l16 16M252 122l-16 16" />""",
    "Blender Tools": """
      <path class="t-soft" d="M133 74.5l27 15.5v31l-27-15.5z" />
      <path d="M160 28l54 31v62l-54 31-54-31V59zM160 90v62M160 90l-54-31M160 90l54-31" />
      <path class="t-dim" d="M133 43.5l54 31M187 43.5l-54 31M106 90l54 31M133 74.5v62M214 90l-54 31M187 74.5v62" />
      <circle class="t-dot" cx="160" cy="28" r="3" /><circle class="t-dot" cx="214" cy="59" r="3" /><circle class="t-dot" cx="106" cy="59" r="3" /><circle class="t-dot" cx="160" cy="90" r="3" />
      <circle class="t-dot" cx="214" cy="121" r="3" /><circle class="t-dot" cx="106" cy="121" r="3" /><circle class="t-dot" cx="160" cy="152" r="3" />""",
    "Asset Pipeline CLI": """
      <rect x="64" y="34" width="192" height="112" rx="3" /><path d="M64 52h192" />
      <circle class="t-dot" cx="75" cy="43" r="2" /><circle class="t-dot" cx="84" cy="43" r="2" /><circle class="t-dot" cx="93" cy="43" r="2" />
      <path d="M80 68l8 6-8 6M96 82h36" />
      <path class="t-dim" d="M80 100h96M80 114h132M80 128h64" /><path d="M192 100h28M226 114h8M162 128h36" />""",
    "Wi-Fi Usage Tracker": """
      <circle class="t-dot" cx="160" cy="84" r="4" />
      <path d="M142 66a26 26 0 0 1 36 0M128 52a46 46 0 0 1 64 0" /><path class="t-dim" d="M114 38a66 66 0 0 1 92 0" />
      <path class="t-dim" d="M64 148h192" /><path d="M64 138l24-8 24 5 24-14 24 9 24-6 24 7 24-13 24 4" />""",
    "Pomodoro Timer": """
      <circle class="t-dim" cx="160" cy="90" r="58" />
      <circle class="t-thick" cx="160" cy="90" r="58" pathLength="100" stroke-dasharray="72 100" transform="rotate(-90 160 90)" />
      <text x="160" y="100" text-anchor="middle">25:00</text>""",
    "Neural Net Basics": '<path class="t-dim" d="' + "".join(
        f"M{x1} {y1}L{x2} {y2}" for (x1, ys1), (x2, ys2) in zip(NN_LAYERS, NN_LAYERS[1:]) for y1 in ys1 for y2 in ys2
    ) + '" />' + "".join(
        f'<circle class="t-solid" cx="{x}" cy="{y}" r="9" />' for x, ys in NN_LAYERS for y in ys
    ),
    "Drone Game": """
      <path class="t-dim" stroke-dasharray="4 6" d="M30 156c40 14 58-4 74-22M216 46c24-24 50-22 74-8" />
      <path d="M118 56l84 68M202 56l-84 68" />
      <circle class="t-soft" cx="118" cy="56" r="24" /><circle class="t-soft" cx="202" cy="56" r="24" /><circle class="t-soft" cx="118" cy="124" r="24" /><circle class="t-soft" cx="202" cy="124" r="24" />
      <circle cx="118" cy="56" r="24" /><circle cx="202" cy="56" r="24" /><circle cx="118" cy="124" r="24" /><circle cx="202" cy="124" r="24" />
      <circle class="t-dot" cx="118" cy="56" r="3" /><circle class="t-dot" cx="202" cy="56" r="3" /><circle class="t-dot" cx="118" cy="124" r="3" /><circle class="t-dot" cx="202" cy="124" r="3" />
      <rect class="t-solid" x="144" y="76" width="32" height="28" rx="4" /><path class="t-dim" d="M152 84h16" />""",
}


SHOT_ALT = {
    "assetviewer.webp": "Asset Viewer showing a grey cube on a grid",
    "audio.webp": "Audio Spectrum Analyzer showing a waveform and a frequency spectrum",
    "dashboard.webp": "Asset Pipeline Dashboard showing file stats and duplicates",
    "gitgui.webp": "Git Client window showing a repository's status",
    "mlcv.webp": "Grid of flower photos with their predicted labels",
    "pdfqa.webp": "PDF Q&A app with a sample PDF uploaded",
    "querymate.webp": "QueryMate app with a database sidebar and a question box",
}


def feature_card(name, num, h="h3"):
    """A project card: screenshot on top (or a line drawing of what it does), then the pitch, the stack and the ways in."""
    b = by_build[name]
    case = CASES.get(name)
    href = f'{case["slug"]}.html' if case else b[5][0][1]
    out = "" if case else ' target="_blank" rel="noreferrer"'
    links = "".join(f'<a class="btn" href="{u}" target="_blank" rel="noreferrer">{t} &#8599;</a>' for t, u in b[5])
    if case:
        links = f'<a class="btn" href="{href}">Case study &rarr;</a>' + links
    if b[2].endswith(".webp"):
        shot = f'<img src="images/projects/{b[2]}" alt="{escape(SHOT_ALT[b[2]])}" loading="lazy" />'
        kind = ""
    else:
        shot = f'<svg class="thumb" viewBox="0 0 320 180" aria-hidden="true">{THUMBS[name]}</svg>'
        kind = " is-code"
    return f"""            <article class="feature panel reveal" data-category="{b[1]}">
              <a class="feature-shot{kind}" href="{href}"{out} tabindex="-1" aria-hidden="true">
                {shot}
              </a>
              <div class="feature-body">
                <p class="feature-tag"><span>{num:02d}</span> {labels[b[1]]}{f" <em>· {MODELS[name]}</em>" if name in MODELS else ""}</p>
                <{h}><a href="{href}"{out}>{escape(name)}</a></{h}>
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
FEATURED = ["Pipeline Tools @ HMX", "Asset Viewer", "Git Client", "PDF Q&A"]
home_renders = ["room", "onii", "fire", "tori", "skull", "lofi", "axe", "iceberg"]

index = head("Kartik Dhasmana", "Kartik Dhasmana: half 3D artist, half developer. I build 3D for the web and the tools that speed it up.") + rail(None) + f"""      <!-- Hero: live viewport with the intro laid over it -->
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
          <p class="lede">Half 3D artist, half developer. I make 3D stuff, tools and whatever else I get curious about.</p>
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
                I'm the kind of person who sees something cool and immediately needs to know how
                it works. The fastest way I've found to figure it out is to build my own version.
              </p>
              <p>
                So that's mostly what I do. Some of it is 3D: props and little worlds I'd want to
                stumble into in a game. Some of it is code: apps, tools, and whatever I've been
                curious about lately. A lot of it ends up on
                <a href="https://github.com/kaydee001" target="_blank" rel="noreferrer">GitHub</a>,
                and some of it ends up in my team's everyday workflow.
              </p>
              <p>
                When I'm not building, it's games, anime, sports with friends, and music pretty
                much always playing.
              </p>
              <p class="about-cta"><a class="btn btn-primary" href="{RESUME}" target="_blank" rel="noreferrer">{icon("resume")}View my resume &#8599;</a><span>The formal version: experience, skills and education.</span></p>
            </div>
          </div>

          <dl class="facts panel glow">
            <div><dt>Focus</dt><dd>🎯 3D, tools, code and AI</dd></div>
            <div><dt>Experience</dt><dd>🧊 4+ years in real-time 3D</dd></div>
            <div><dt>Open to</dt><dd>🤝 Roles where 3D, tools and code meet</dd></div>
            <div><dt>Learning</dt><dd>🧠 Whatever looks interesting this week</dd></div>
            <div><dt>Tools</dt><dd>🛠️ VS Code, Blender and Claude</dd></div>
            <div><dt>Music</dt><dd>🎧 All kinds, all the time</dd></div>
            <div><dt>Off hours</dt><dd>🎮 Games, anime and sports with my boys</dd></div>
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
              <a class="btn btn-primary stop-next" href="#contact">Next stop: open to what's next {icon("next")}</a>
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
            <a class="btn btn-primary" href="projects.html"><span class="more-count">{len(FEATURED)} of {len(builds)}</span> View all &rarr;</a>
          </div>
          <div class="features is-compact">
{"".join(feature_card(n, i) for i, n in enumerate(FEATURED, 1))}          </div>
          <div class="section-end"><a class="btn btn-primary" href="projects.html">View all &darr;</a></div>
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
              <a class="btn btn-primary" href="3d.html"><span class="more-count">{len(home_renders)} of {len(renders)}</span> View all &rarr;</a>
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
              <!-- Spam checks: a hidden box only bots tick, and an hCaptcha (loaded when the form comes into view) -->
              <input class="hp" type="checkbox" name="botcheck" tabindex="-1" autocomplete="off" aria-hidden="true" />
              <div class="form-captcha" id="captcha"></div>
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
{"".join(feature_card(b[0], i, "h2") for i, b in enumerate(builds, 1))}          </div>
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
          <a class="btn btn-primary" href="https://www.artstation.com/kaydee001" target="_blank" rel="noreferrer">More on ArtStation &#8599;</a>
        </div>
      </section>

""" + FOOT + LIBS + """  </body>
</html>
"""


# ---------------------------------------------------------------- case studies
def tool_block(name, does, result):
    """One tool on a case page: what it does and the result."""
    return f"""<article class="tool">
              <h3>{escape(name)}</h3>
              <dl class="case-facts panel"><div><dt>does</dt><dd>{escape(does)}</dd></div><div><dt>result</dt><dd>{escape(result)}</dd></div></dl>
            </article>"""


def case_page(name, prev, nxt, pos):
    c = CASES[name]
    _, cat, _, _, _, links = by_build[name]
    buttons = "".join(
        f'<a class="btn{" btn-primary" if i == 0 else ""}" href="{u}" target="_blank" rel="noreferrer">{t} &#8599;</a>'
        for i, (t, u) in enumerate(links)
    )
    meta = "".join(f"<div><dt>{k}</dt><dd>{escape(v)}</dd></div>" for k, v in c["meta"])
    what = "".join(f"<p>{escape(p)}</p>" for p in c["what"])
    if "tools" in c:
        steps = '<div class="tools">' + "".join(tool_block(*t) for t in c["tools"]) + "</div>"
    else:
        steps = '<ol class="steps">' + "".join(f"<li><b>{k}</b><span>{escape(v)}</span></li>" for k, v in c["steps"]) + "</ol>"
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
            {steps}
            {note}
          </div>

          <div class="case-block">
            <h2>{c["facts_title"]}</h2>
            <dl class="case-facts panel">{facts}</dl>
          </div>

          <a class="btn btn-primary" href="projects.html">&larr; All projects</a>
        </div>
      </section>

""" + FOOT + LIBS + fig_script + """  </body>
</html>
"""


# ---------------------------------------------------------------- client work
cw = CLIENT_WORK
client_page = head("Client work @ HMX | Kartik Dhasmana",
                   "3D web and AR product work at HMX Media for Dell, Lenovo, McLaren, Royal Enfield and C.L. Seifert.",
                   "hmx-work.html") + rail("experience") + page_head(
    "hmx media", ("index.html#experience", "Experience"), ("projects.html", "Projects"), "02", "client work", "Client work",
    f"{cw['count']} products I've worked on at HMX Media for {len(cw['brands'])} brands. Point at a colour to swap the view, "
    "or click through to the product page.", "",
) + f"""
      <section class="section is-tight">
        <div class="wrap">
          <div class="work-list">
{cw['rows']}          </div>
          <p class="xp-also">{also_html(cw['also'])}</p>
        </div>
      </section>

""" + FOOT + LIBS + """  </body>
</html>
"""

case_pages = [
    ("hmx-tools.html", case_page("Pipeline Tools @ HMX", ("projects.html", "Projects"), ("pdf-qa.html", "PDF Q&A"), "case 01 / 03")),
    ("pdf-qa.html", case_page("PDF Q&A", ("hmx-tools.html", "Pipeline Tools @ HMX"), ("asset-viewer.html", "Asset Viewer"), "case 02 / 03")),
    ("asset-viewer.html", case_page("Asset Viewer", ("pdf-qa.html", "PDF Q&A"), ("projects.html", "Projects"), "case 03 / 03")),
]

for fname, html in [("index.html", index), ("hmx-work.html", client_page), ("projects.html", projects), ("3d.html", gallery)] + case_pages:
    (out / fname).write_text(html, encoding="utf-8", newline="")
    print(fname, html.count("<section"), html.count("</section>"), html.count("<div"), html.count("</div>"))
