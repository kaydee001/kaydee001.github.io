"""Generate index.html, projects.html and 3d.html with a shared sidebar/footer.

Gallery cards are lifted from the current 3d.html so render metadata stays as-is.
"""
import re
import sys
from html import escape
from pathlib import Path

root = Path(sys.argv[1])
# Render cards are read from the full gallery page
current = (root / "3d.html").read_text(encoding="utf-8")

# ---------------------------------------------------------------- gallery cards
cards = re.findall(r'            <article class="work-card[^"]*".*?</article>\n', current, flags=re.S)
assert len(cards) == 27, len(cards)
by_name = {}
for c in cards:
    name = re.search(r"images/work/(\w+)\.webp", c).group(1)
    label = re.search(r'<p class="card-label">(\w+)</p>', c).group(1).lower()
    category = {"prop": "props", "weapon": "weapons", "environment": "environments"}[label]
    c = re.sub(r'<article class="work-card[^>]*>', f'<article class="work-card" data-category="{category}">', c)
    by_name[name] = c

home_renders = ["room", "tori", "lofi", "axe", "skull", "onii"]
gallery_order = ["room", "tori", "lofi", "axe", "skull", "onii", "fire", "iceberg", "museum", "abstract",
                 "buster", "headphone"] + [n for n in by_name if n not in
                 {"room", "tori", "lofi", "axe", "skull", "onii", "fire", "iceberg", "museum", "abstract", "buster", "headphone"}]
assert sorted(gallery_order) == sorted(by_name)

# ---------------------------------------------------------------- builds
GH = "https://github.com/kaydee001/"
builds = [
    # name, category, image or glyph, line, stack, links
    ("Pipeline Tools @ HMX", "tools", "hmx", "File tools and Blender add-ons I built for the whole 3D team at HMX Media, to cut the repetitive work.",
     "Python · Blender API", []),
    ("PDF Q&A", "ai", "pdfqa.webp", "Drop in a PDF and ask it questions. Answers come back with the part of the document they came from.",
     "Python · FAISS · Groq · Streamlit", [("Live demo", "https://pdf-chatbot-rag-demo.streamlit.app/"), ("GitHub", GH + "pdf-chatbot-rag")]),
    ("Asset Viewer", "tools", "assetviewer.webp", "A 3D model viewer that runs on your own machine. Drop in a GLB, FBX or OBJ and inspect it: wireframe, grid, HDRI lighting. No uploads.",
     "Three.js · Flask · PyQt5", [("GitHub", GH + "asset-viewer")]),
    ("Git Client", "apps", "gitgui.webp", "My own Git GUI for staging, committing, pushing, pulling and switching branches, packaged as a Windows app.",
     "Python · PySide6 · PyInstaller", [("GitHub", GH + "git-gui")]),
    ("Asset Pipeline Dashboard", "tools", "dashboard.webp", "Scans a project folder and shows what's off: duplicates, bad names, oversized files and empty folders.",
     "Python · Flask", [("GitHub", GH + "asset-dashboard")]),
    ("QueryMate", "ai", "querymate.webp", "Ask a database a question in plain English and get back the SQL and the result. Read-only, so nothing breaks.",
     "Python · LLM · SQL · Streamlit", [("Live demo", "https://querymate-ai.streamlit.app/"), ("GitHub", GH + "sql-query-generator")]),
    ("Audio Spectrum Analyzer", "apps", "audio.webp", "Load a sound and see its waveform and frequency spectrum side by side, using FFT.",
     "Python · NumPy · Matplotlib", [("GitHub", GH + "Audio-Spectrum-Analyzer")]),
    ("Image Classifiers", "ai", "mlcv.webp", "Learning PyTorch by building: a CNN from scratch on CIFAR-10, then transfer learning on flowers.",
     "Python · PyTorch", [("GitHub", GH + "ML-CV-Projects")]),
    ("DevDocs AI", "ai", ".py → docs", "Upload Python code and get back a README, function docs and a documentation quality score.",
     "Python · FastAPI · LLM", [("Live demo", "https://devdocs-ai-jjof.onrender.com/docs"), ("GitHub", GH + "devdocs-ai")]),
    ("File Ingestor", "apps", "inbox/", "Watches a folder, checks every incoming file and sorts it into clean or quarantine, with a live log.",
     "Python · PySide6", [("GitHub", GH + "file-ingestor")]),
    ("Blender Tools", "tools", "bpy", "Python scripts and add-ons for everyday Blender asset work.",
     "Python · Blender API", [("GitHub", GH + "blender-tools")]),
    ("Asset Pipeline CLI", "tools", "scan ./", "A command-line tool that scans, filters and summarises 3D asset files across a project.",
     "Python", [("GitHub", GH + "asset-pipeline")]),
    ("Wi-Fi Usage Tracker", "apps", "wifi", "Tracks Wi-Fi usage in real time, logs it per day and graphs it.",
     "Python", [("GitHub", GH + "wifi-usage-tracker")]),
    ("Pomodoro Timer", "apps", "25:00", "A desktop Pomodoro timer.",
     "Python · PySide6", [("GitHub", GH + "pomodoro-timer")]),
    ("Neural Net Basics", "ai", "nn", "Small neural networks and CNNs, written while learning deep learning.",
     "Python", [("GitHub", GH + "AI-Learning-Projects")]),
    ("Drone Game", "apps", "2021", "An early C# game project from college.",
     "C#", [("GitHub", GH + "drone_game")]),
]
home_builds = ["PDF Q&A", "Asset Viewer", "Git Client"]
labels = {"ai": "AI", "tools": "Tool", "apps": "App"}


def build_card(b, indent="            "):
    name, cat, media, line, stack, links = b
    if media.endswith(".webp"):
        top = "media-top" if media == "gitgui.webp" else ""
        media_html = f'<div class="project-media {top}"><img src="images/projects/{media}" alt="{escape(name)} screenshot" loading="lazy" /></div>'.replace('project-media "', 'project-media"')
    else:
        media_html = f'<div class="project-media glyph"><strong>{escape(media)}</strong></div>'
    link_html = "".join(
        f'<a class="text-link" href="{u}" target="_blank" rel="noreferrer">{t} &#8599;</a>' for t, u in links
    )
    return (
        f'{indent}<article class="build-card" data-category="{cat}">\n'
        f"{indent}  {media_html}\n"
        f'{indent}  <div class="build-body">\n'
        f'{indent}    <p class="card-label">{labels[cat]}</p>\n'
        f"{indent}    <h3>{escape(name)}</h3>\n"
        f"{indent}    <p>{escape(line)}</p>\n"
        f'{indent}    <p class="feature-meta">{escape(stack)}</p>\n'
        f'{indent}    <div class="project-links">{link_html}</div>\n'
        f"{indent}  </div>\n"
        f"{indent}</article>\n"
    )


# ---------------------------------------------------------------- shared chrome
RESUME = "https://drive.google.com/file/d/1beKRxJsIhH8V-t0NbYfZ4qD8lMVYGmjG/view?usp=share_link"


def head(title, description):
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{description}" />
    <title>{title}</title>
    <link rel="icon" href="images/KD.png" />
    <script>
      // Set the theme before first paint: saved choice, else the OS preference
      try {{
        var saved = localStorage.getItem('theme')
        document.documentElement.dataset.theme =
          saved || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark')
      }} catch (e) {{}}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap"
    />
    <link rel="stylesheet" href="styles.css" />
  </head>
"""


def sidebar(active):
    def link(num, href, text, key):
        cls = "nav-link is-active" if key == active else "nav-link"
        return f'          <a class="{cls}" href="{href}"><span>{num}</span>{text}</a>\n'

    return f"""  <body>
    <div class="site-frame layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-top">
          <a class="brand" href="index.html" aria-label="Kartik Dhasmana home">
            <span class="brand-mark" aria-hidden="true">
              <img src="images/KD.png" alt="" width="32" height="32" />
            </span>
            <span class="brand-copy">
              <span class="brand-kicker">3D · Tools · AI</span>
              <span class="brand-name">Kartik Dhasmana</span>
            </span>
          </a>
          <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle light and dark theme">
            <svg class="icon-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
            <svg class="icon-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" /></svg>
          </button>
        </div>

        <nav class="site-nav" aria-label="Primary">
{link("01", "index.html#about", "About", "about")}{link("02", "projects.html", "Projects", "projects")}{link("03", "3d.html", "3D", "3d")}{link("04", "index.html#contact", "Contact", "contact")}          <a class="nav-link" href="{RESUME}" target="_blank" rel="noreferrer"><span>05</span>Resume &#8599;</a>
        </nav>

        <div class="sidebar-links">
          <a href="https://www.artstation.com/kaydee001" target="_blank" rel="noreferrer">ArtStation</a>
          <a href="https://github.com/kaydee001" target="_blank" rel="noreferrer">GitHub</a>
          <a href="https://www.linkedin.com/in/kartik-dhasmana-852331192/" target="_blank" rel="noreferrer">LinkedIn</a>
          <a href="https://www.instagram.com/kd_renders_3d/" target="_blank" rel="noreferrer">Instagram</a>
        </div>
      </aside>

      <div class="content">
      <main class="page-stack">
"""


FOOT = f"""      </main>

      <footer class="site-footer">
        <div class="footer-row">
          <p>&copy; <span id="year">2026</span> Kartik Dhasmana</p>
          <a class="text-link" href="#">Back to top &uarr;</a>
        </div>
      </footer>
      </div>
    </div>

    <dialog class="viewer" id="viewer" aria-label="Image viewer">
      <figure class="viewer-figure">
        <img id="viewer-image" alt="" />
        <div class="viewer-bar">
          <figcaption id="viewer-caption"></figcaption>
          <div class="viewer-controls">
            <button type="button" id="viewer-prev" aria-label="Previous image">&larr;</button>
            <button type="button" id="viewer-next" aria-label="Next image">&rarr;</button>
            <button type="button" id="viewer-close" aria-label="Close">&times;</button>
          </div>
        </div>
      </figure>
    </dialog>

    <script src="script.js"></script>
  </body>
</html>
"""

contact = f"""        <!-- Contact -->
        <section class="panel split-panel" id="contact">
          <div>
            <p class="section-label">Contact</p>
            <h2>Get in touch</h2>
            <p class="section-copy">
              Got a project, a job, or just want to talk 3D, tools or AI? I'm based
              in Pune, India. Send a message, or email me at
              <a class="inline-link" href="mailto:kartik.dhasmana001@gmail.com">kartik.dhasmana001@gmail.com</a>.
            </p>
            <p class="feature-meta">The formal version is on my <a class="inline-link" href="{RESUME}" target="_blank" rel="noreferrer">resume &#8599;</a></p>
          </div>

          <form class="contact-form" id="contact-form" method="post" action="https://api.web3forms.com/submit">
            <input type="hidden" name="access_key" value="fb73c820-dc81-48dd-b364-13fc17c859a2" />
            <input type="text" name="name" placeholder="Name" aria-label="Name" required />
            <input type="email" name="email" placeholder="Email" aria-label="Email" required />
            <textarea class="full" name="message" placeholder="Message" aria-label="Message" required></textarea>
            <div class="form-footer full">
              <button class="button button-primary" type="submit">Send message</button>
              <p class="form-status" id="form-status" role="status"></p>
            </div>
          </form>
        </section>

"""


def filters(label, options):
    btns = '              <button class="filter-button is-active" type="button" data-filter="all">All</button>\n'
    btns += "".join(
        f'              <button class="filter-button" type="button" data-filter="{k}">{v}</button>\n' for k, v in options
    )
    return f'            <div class="filter-row" role="group" aria-label="{label}">\n{btns}            </div>\n'


# ---------------------------------------------------------------- index.html
by_build = {b[0]: b for b in builds}
index = head(
    "Kartik Dhasmana",
    "Kartik Dhasmana: real-time artist from Pune. I make 3D stuff, tools, and whatever else I get curious about.",
) + sidebar("about") + f"""        <!-- About -->
        <section class="panel split-panel" id="about">
          <div class="about-copy">
            <p class="section-label">About</p>
            <h1>Hi, I'm Kartik.</h1>
            <p>
              I studied computer science with a focus on gaming tech at VIT Bhopal, and
              I've been doing 3D since college. First it was AR lessons for school
              students at Myracle.io (the product even made it onto Shark Tank India).
              Now I'm a real-time artist at HMX Media, making 3D for the web and AR.
            </p>
            <p>
              Somewhere along the way I started writing code around the art. Python
              scripts to skip the boring parts, then pipeline tools for the team, then
              desktop apps, then whatever else caught my eye. Right now that's AI:
              RAG apps, LLM tools, and teaching myself PyTorch.
            </p>
            <p>
              I learn best by building, so most of what I pick up turns into a project.
              Finished or not, it usually ends up on
              <a class="inline-link" href="https://github.com/kaydee001" target="_blank" rel="noreferrer">GitHub</a>.
            </p>
          </div>

          <aside class="side-list" aria-label="Off the clock">
            <p class="card-label">Off the clock</p>
            <dl>
              <div><dt>Music</dt><dd>all kinds, all the time</dd></div>
              <div><dt>Anime</dt><dd>always have something on</dd></div>
              <div><dt>Games</dt><dd>multiplayer FPS and strategy</dd></div>
              <div><dt>Shows</dt><dd><span class="the-boys">THE BOYS</span></dd></div>
            </dl>
          </aside>
        </section>

        <!-- Projects -->
        <section class="panel" id="work">
          <div class="section-head">
            <div>
              <p class="section-label">Projects</p>
              <h2>Recent builds</h2>
            </div>
            <a class="text-link" href="projects.html">All {len(builds)} projects &rarr;</a>
          </div>
          <div class="build-grid">
{"".join(build_card(by_build[n]) for n in home_builds)}          </div>
        </section>

        <!-- 3D -->
        <section class="panel" id="art">
          <div class="section-head">
            <div>
              <p class="section-label">3D</p>
              <h2>Renders</h2>
            </div>
            <a class="text-link" href="3d.html">All {len(by_name)} renders &rarr;</a>
          </div>
          <div class="work-grid">
{"".join(by_name[n] for n in home_renders)}          </div>
        </section>

{contact}""" + FOOT

# ---------------------------------------------------------------- projects.html
counts = {k: sum(1 for b in builds if b[1] == k) for k in labels}
projects = head(
    "Projects | Kartik Dhasmana",
    "Tools, apps and AI experiments by Kartik Dhasmana.",
) + sidebar("projects") + f"""        <section class="panel">
          <a class="back-link" href="index.html">&larr; Home</a>
          <div class="section-head">
            <div>
              <p class="section-label">Projects</p>
              <h1 class="page-title">Things I've made</h1>
              <p class="section-copy">Tools, apps and AI experiments. Some finished, some still in progress.</p>
            </div>
{filters("Filter projects", [("tools", "Tools"), ("apps", "Apps"), ("ai", "AI")])}          </div>
          <div class="build-grid">
{"".join(build_card(b) for b in builds)}          </div>
        </section>

""" + FOOT

# ---------------------------------------------------------------- 3d.html
gallery = head(
    "3D | Kartik Dhasmana",
    "3D props, weapons and environments by Kartik Dhasmana.",
) + sidebar("3d") + f"""        <section class="panel">
          <a class="back-link" href="index.html">&larr; Home</a>
          <div class="section-head">
            <div>
              <p class="section-label">3D</p>
              <h1 class="page-title">3D work</h1>
              <p class="section-copy">Props, weapons and environments. Click any render to see it full size.</p>
            </div>
{filters("Filter renders", [("props", "Props"), ("weapons", "Weapons"), ("environments", "Environments")])}          </div>
          <div class="work-grid">
{"".join(by_name[n] for n in gallery_order)}          </div>
          <div class="gallery-more">
            <a class="text-link" href="https://www.artstation.com/kaydee001" target="_blank" rel="noreferrer">More on ArtStation &#8599;</a>
          </div>
        </section>

""" + FOOT

for fname, html in [("index.html", index), ("projects.html", projects), ("3d.html", gallery)]:
    (root / fname).write_text(html, encoding="utf-8", newline="")
    print(fname, html.count("<div"), html.count("</div>"), html.count("<section"), html.count("</section>"))
