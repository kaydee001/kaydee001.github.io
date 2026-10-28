// Theme toggle (initial theme is set inline in <head>)
document.getElementById('theme-toggle').addEventListener('click', () => {
  const root = document.documentElement
  const next = root.dataset.theme === 'light' ? 'dark' : 'light'
  root.dataset.theme = next
  try {
    localStorage.setItem('theme', next)
  } catch (e) {}
  window.dispatchEvent(new Event('themechange'))
})

const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches

// Boot sequence: types a short system log, then fades out. Any click or key skips it.
const boot = document.getElementById('boot')
if (document.documentElement.classList.contains('is-booting')) {
  const log = document.getElementById('boot-log')
  const lines = [
    ['kd_os v3.0 // kartik dhasmana', ''],
    ['> mounting /3d/renders ............', ' ok'],
    ['> loading /tools /apps /ai ........', ' ok'],
    ['> calibrating viewport ............', ' ok'],
    ['> entering the grid ...............', ' ok'],
    ['> establishing uplink: pune, in ...', ' ok'],
    ['> welcome.', '']
  ]
  let i = 0
  const finish = () => {
    if (boot.classList.contains('is-done')) return
    boot.classList.add('is-done')
    try {
      sessionStorage.setItem('booted', '1')
    } catch (e) {}
    setTimeout(() => {
      document.documentElement.classList.remove('is-booting')
      dispatchEvent(new Event('booted'))
    }, 500)
  }
  const next = () => {
    if (i >= lines.length) return setTimeout(finish, 250)
    const [text, status] = lines[i++]
    log.insertAdjacentHTML('beforeend', `<span class="${i === 1 ? 'dim' : ''}">${text}</span><span class="ok">${status}</span>\n`)
    setTimeout(next, 170)
  }
  next()
  addEventListener('pointerdown', finish, { once: true })
  addEventListener('keydown', finish, { once: true })
}

// Hero headline types out like console output, right after the boot log if it's playing
const heroTitle = document.getElementById('hero-title')
if (heroTitle && !reduceMotion) {
  const text = heroTitle.textContent
  heroTitle.setAttribute('aria-label', text)
  heroTitle.textContent = ''
  const type = (i = 0) => {
    heroTitle.textContent = text.slice(0, i)
    if (i < text.length) setTimeout(() => type(i + 1), i === 0 ? 0 : 70 + Math.random() * 60)
  }
  if (document.documentElement.classList.contains('is-booting')) addEventListener('booted', () => type(), { once: true })
  else setTimeout(type, 350)
}

// Live IST clock in the telemetry
const clock = document.getElementById('clock')
if (clock) {
  const tick = () => {
    clock.textContent = new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Kolkata' })
  }
  tick()
  setInterval(tick, 1000)
}


// Background dot field: a slow, soft wave drifts across it and dots twinkle gently on their own.
// The glow fades in over a base dot, so nothing flickers.
const field = document.getElementById('bg-field')
if (field) {
  const ctx = field.getContext('2d')
  // Phones and low-core machines get a sparser field drawn at 30 fps; it looks the same and costs about a third
  const light = matchMedia('(max-width: 700px)').matches || (navigator.hardwareConcurrency || 8) <= 4
  const SPACING = light ? 38 : 30
  const FRAME = light ? 1000 / 30 : 0
  let dots = []
  let colors = {}
  let dpr = 1

  const readColors = () => {
    const css = getComputedStyle(document.documentElement)
    colors = { dot: css.getPropertyValue('--line-2').trim(), accent: css.getPropertyValue('--accent').trim() }
  }

  const layout = () => {
    dpr = Math.min(devicePixelRatio, 2)
    field.width = innerWidth * dpr
    field.height = innerHeight * dpr
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    dots = []
    for (let y = SPACING / 2; y < innerHeight; y += SPACING) {
      for (let x = SPACING / 2; x < innerWidth; x += SPACING) dots.push({ x, y, phase: Math.random() * Math.PI * 2 })
    }
  }

  const smooth = (v) => v * v * (3 - 2 * v)
  // Snap to whole device pixels so the dots stay crisp
  const snap = (v) => Math.round(v * dpr) / dpr

  let last = 0
  const draw = (t) => {
    last = t
    ctx.clearRect(0, 0, innerWidth, innerHeight)

    const lit = []
    ctx.fillStyle = colors.dot
    ctx.globalAlpha = 0.5
    for (const d of dots) {
      const x = snap(d.x)
      const y = snap(d.y)
      ctx.fillRect(x - 0.6, y - 0.6, 1.2, 1.2)
      if (reduceMotion) continue
      // A broad diagonal swell, eased at both edges
      const wave = smooth((Math.sin((d.x + d.y) * 0.004 - t * 0.00035) + 1) / 2) ** 4
      // Each dot breathes in now and then on its own slow rhythm
      const twinkle = ((Math.sin(t * 0.0006 + d.phase * 7) + 1) / 2) ** 60
      const glow = Math.max(wave * 0.55, twinkle * 0.85)
      if (glow > 0.01) lit.push(x, y, glow)
    }

    ctx.fillStyle = colors.accent
    for (let i = 0; i < lit.length; i += 3) {
      const glow = lit[i + 2]
      const size = 1.2 + glow * 1.4
      ctx.globalAlpha = Math.min(1, glow * 1.1)
      ctx.fillRect(lit[i] - size / 2, lit[i + 1] - size / 2, size, size)
    }
    ctx.globalAlpha = 1
  }

  const loop = (t) => {
    if (t - last >= FRAME - 1) draw(t)
    if (!reduceMotion) requestAnimationFrame(loop)
  }

  readColors()
  layout()
  // Still frames (reduced motion) need a redraw when the window or theme changes
  addEventListener('resize', () => {
    layout()
    if (reduceMotion) draw(0)
  })
  addEventListener('themechange', () => {
    readColors()
    if (reduceMotion) draw(0)
  })
  requestAnimationFrame(loop)
}

// Text scramble: headings resolve from random glyphs, like terminal output
const GLYPHS = '!<>-_\\/[]{}=+*^?#01'

function scramble(el) {
  const target = el.dataset.text || el.textContent
  el.dataset.text = target
  let frame = 0
  const total = 22
  const tick = () => {
    const done = Math.floor((frame / total) * target.length)
    el.textContent = target
      .split('')
      .map((ch, i) => (i < done || ch === ' ' ? ch : GLYPHS[Math.floor(Math.random() * GLYPHS.length)]))
      .join('')
    if (frame++ < total) requestAnimationFrame(tick)
    else el.textContent = target
  }
  tick()
}

// Smooth scrolling (Lenis) and scroll reveals (GSAP), when the libraries loaded
let lenis = null
if (!reduceMotion && window.Lenis && window.gsap && window.ScrollTrigger) {
  gsap.registerPlugin(ScrollTrigger)
  lenis = new Lenis({ lerp: 0.1 })
  lenis.on('scroll', ScrollTrigger.update)
  gsap.ticker.add((time) => lenis.raf(time * 1000))
  gsap.ticker.lagSmoothing(0)

  if (document.querySelector('.reveal')) {
    gsap.set('.reveal', { opacity: 0, y: 24 })
    ScrollTrigger.batch('.reveal', {
      start: 'top 90%',
      once: true,
      onEnter: (batch) => gsap.to(batch, { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out', stagger: 0.08 })
    })
  }

  document.querySelectorAll('[data-scramble]').forEach((el) => {
    ScrollTrigger.create({ trigger: el, start: 'top 92%', once: true, onEnter: () => scramble(el) })
  })

  // Homepage only: the hero intro rises in
  if (document.querySelector('.hero-copy')) {
    gsap.from('.hero-copy > *, .hero-side', { opacity: 0, y: 20, duration: 0.9, ease: 'power3.out', stagger: 0.08 })
  }
}

// 3D carousel: an endless strip that drifts slowly left; it never holds up the page scroll.
// It slows under the cursor and stops while focused or off screen. Arrows step one render; mouse or touch can drag it.
const stripView = document.querySelector('.strip-view')
if (stripView) {
  const track = stripView.querySelector('.strip-track')
  const originals = [...track.children]
  // A copy of the renders follows the originals, so the loop has no visible seam
  originals.forEach((item) => {
    const copy = item.cloneNode(true)
    copy.dataset.clone = ''
    copy.setAttribute('aria-hidden', 'true')
    copy.querySelectorAll('a').forEach((a) => a.setAttribute('tabindex', '-1'))
    track.append(copy)
  })
  const items = [...track.children]
  const SPEED = 40 // px per second

  let starts = []
  let loop = 0 // width of one full set of renders
  const measure = () => {
    starts = items.map((item) => item.offsetLeft - items[0].offsetLeft)
    loop = starts[originals.length]
  }
  measure()
  addEventListener('resize', measure)

  let x = 0
  let target = null // set by the arrows; x eases toward it
  let speed = SPEED
  let hovered = false
  let focused = false
  let onScreen = false
  let drag = null
  let last = 0

  const frame = (now) => {
    requestAnimationFrame(frame)
    const dt = Math.min(64, now - (last || now))
    last = now
    if (!onScreen || !loop) return
    if (target !== null) {
      x += (target - x) * 0.12
      if (Math.abs(target - x) < 0.5) {
        x = target
        target = null
      }
    } else {
      // Ease toward the wanted speed: full drift, slower under the cursor, stopped while dragged or focused
      const want = drag || focused || reduceMotion || document.hidden ? 0 : hovered ? SPEED * 0.3 : SPEED
      speed += (want - speed) * 0.05
      x += (speed * dt) / 1000
    }
    // Keep x inside one set; shift the arrow target with it
    const wrapped = ((x % loop) + loop) % loop
    if (target !== null) target += wrapped - x
    x = wrapped
    track.style.transform = `translate3d(${-x}px, 0, 0)`
  }
  requestAnimationFrame(frame)

  new IntersectionObserver(([entry]) => (onScreen = entry.isIntersecting)).observe(stripView)
  stripView.addEventListener('pointerenter', () => (hovered = true))
  stripView.addEventListener('pointerleave', () => (hovered = false))
  stripView.addEventListener('focusin', () => (focused = true))
  stripView.addEventListener('focusout', () => (focused = false))

  // Arrows: ease to the start of the next / previous render
  const step = (dir) => {
    const from = target ?? x
    const all = [...starts.map((s) => s - loop), ...starts]
    target = dir > 0 ? all.find((s) => s > from + 1) : all.filter((s) => s < from - 1).pop()
  }
  document.getElementById('strip-prev').addEventListener('click', () => step(-1))
  document.getElementById('strip-next').addEventListener('click', () => step(1))

  // Drag with mouse or touch (vertical swipes still scroll the page)
  stripView.addEventListener('dragstart', (event) => event.preventDefault())
  stripView.addEventListener('pointerdown', (event) => {
    if (event.button !== 0) return
    drag = { start: event.clientX, x, moved: false }
    target = null
  })
  addEventListener('pointermove', (event) => {
    if (!drag) return
    const dx = event.clientX - drag.start
    if (!drag.moved && Math.abs(dx) > 5) {
      drag.moved = true
      stripView.classList.add('is-dragging')
    }
    if (drag.moved) x = drag.x - dx
  })
  const endDrag = () => {
    if (!drag) return
    const moved = drag.moved
    drag = null
    // Wait until the click from this release has passed, so it doesn't open the render
    if (moved) setTimeout(() => stripView.classList.remove('is-dragging'))
  }
  addEventListener('pointerup', endDrag)
  addEventListener('pointercancel', endDrag)
}

// In-page anchors scroll through Lenis so they stay smooth
document.querySelectorAll('a[href^="#"], a[href*="index.html#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const url = new URL(link.href)
    // "/v2/" and "/v2/index.html" are the same page
    const page = (path) => path.replace(/index\.html$/, '')
    if (page(url.pathname) !== page(location.pathname)) return
    const target = link.hasAttribute('data-top') ? 0 : document.querySelector(url.hash)
    if (target === null) return
    event.preventDefault()
    if (lenis) lenis.scrollTo(target)
    else if (target === 0) scrollTo({ top: 0 })
    else target.scrollIntoView()
    history.replaceState(null, '', target === 0 ? location.pathname : url.hash)
  })
})

// Arriving from another page with a #section: land on it once the layout has settled
if (location.hash) {
  addEventListener('load', () => {
    const target = document.querySelector(location.hash)
    if (!target) return
    if (lenis) lenis.scrollTo(target, { immediate: true, force: true })
    else target.scrollIntoView()
  })
}

// Spotlight: panels with .glow track the cursor
document.querySelectorAll('.glow').forEach((el) => {
  el.addEventListener('pointermove', (event) => {
    const rect = el.getBoundingClientRect()
    el.style.setProperty('--mx', `${event.clientX - rect.left}px`)
    el.style.setProperty('--my', `${event.clientY - rect.top}px`)
  })
})

// Filter chips on the Projects and 3D pages
const chips = document.querySelectorAll('.chip')
const filterItems = [...document.querySelectorAll('.feature[data-category], .tile[data-category]')]

chips.forEach((chip) => {
  const filter = chip.dataset.filter
  const count = filter === 'all'
    ? filterItems.length
    : filterItems.filter((item) => item.dataset.category === filter).length
  chip.insertAdjacentHTML('beforeend', `<sup>${count}</sup>`)

  chip.addEventListener('click', () => {
    chips.forEach((c) => c.classList.toggle('is-active', c === chip))
    filterItems.forEach((item) => {
      item.hidden = filter !== 'all' && item.dataset.category !== filter
      if (!item.hidden && window.gsap) gsap.set(item, { opacity: 1, y: 0 })
    })
    window.ScrollTrigger?.refresh()
  })
})

// Image viewer for 3D tiles
const viewer = document.getElementById('viewer')
const viewerImage = document.getElementById('viewer-image')
const viewerTitle = document.getElementById('viewer-title')
const viewerKind = document.getElementById('viewer-kind')
const viewerCount = document.getElementById('viewer-count')
const viewerWhat = document.getElementById('viewer-what')
const viewerSub = document.getElementById('viewer-sub')
const viewerTags = document.getElementById('viewer-tags')
const tileLinks = [...document.querySelectorAll('.tile-link')]
let gallery = []
let current = 0

function show(index) {
  current = (index + gallery.length) % gallery.length
  const link = gallery[current]
  viewerImage.src = link.href
  for (const step of [1, -1]) new Image().src = gallery[(current + step + gallery.length) % gallery.length].href
  viewerImage.alt = link.dataset.title
  viewerTitle.textContent = link.dataset.title
  viewerKind.textContent = link.dataset.kind || ''
  viewerWhat.textContent = link.dataset.label || 'render'
  viewerSub.textContent = link.dataset.sub || 'Made with'
  const pad = (n) => String(n).padStart(2, '0')
  viewerCount.textContent = `[${pad(current + 1)} / ${pad(gallery.length)}]`
  viewerTags.replaceChildren(...(link.dataset.tags || '').split(' · ').filter(Boolean).map((tag) => {
    const li = document.createElement('li')
    li.className = 'tag'
    li.textContent = tag
    return li
  }))
}

tileLinks.forEach((link) => {
  link.addEventListener('click', (event) => {
    event.preventDefault()
    // Step only through the tiles on screen (the filter hides some)
    gallery = tileLinks.filter((l) => l.offsetParent !== null && !l.closest('[data-clone]'))
    show(gallery.findIndex((l) => l.href === link.href))
    viewer.showModal()
    lenis?.stop()
  })
})

viewer.addEventListener('close', () => lenis?.start())
document.getElementById('viewer-prev').addEventListener('click', () => show(current - 1))
document.getElementById('viewer-next').addEventListener('click', () => show(current + 1))
document.getElementById('viewer-close').addEventListener('click', () => viewer.close())
viewer.addEventListener('click', (event) => {
  if (event.target === viewer) viewer.close()
})
document.addEventListener('keydown', (event) => {
  if (!viewer.open) return
  if (event.key === 'ArrowLeft') show(current - 1)
  if (event.key === 'ArrowRight') show(current + 1)
})

// Homepage: highlight the rail link for the section in view
const sectionLinks = { about: '#about', experience: '#experience', work: '#work', art: '#art', contact: '#contact' }
const sections = [...document.querySelectorAll('main section[id]')].filter((s) => sectionLinks[s.id])
if (sections.length) {
  const navLinks = document.querySelectorAll('.nav-link')
  const update = () => {
    let active = null
    sections.forEach((s) => {
      if (s.getBoundingClientRect().top < innerHeight * 0.5) active = s
    })
    navLinks.forEach((l) => l.classList.toggle('is-active', active !== null && l.getAttribute('href') === sectionLinks[active.id]))
  }
  addEventListener('scroll', update, { passive: true })
  update()
}

// Popups that open from a button: the skills list and the full client work list
for (const [id, openId, closeId] of [['skills', 'skills-open', 'skills-close'], ['work-all', 'work-open', 'work-close']]) {
  const dialog = document.getElementById(id)
  if (!dialog) continue
  document.getElementById(openId).addEventListener('click', () => {
    dialog.showModal()
    // Focus the heading, so the close button doesn't open with a focus ring
    dialog.querySelector('h2').focus()
    lenis?.stop()
  })
  document.getElementById(closeId).addEventListener('click', () => dialog.close())
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close()
  })
  dialog.addEventListener('close', () => lenis?.start())
}

// Client ranges: pointing at, focusing or tapping a variant swaps the big view to it
document.querySelectorAll('.range').forEach((range) => {
  const view = range.querySelector('.range-view img')
  const label = range.querySelector('.range-label')
  const picks = [...range.querySelectorAll('.range-pick')]
  const pick = (button) => {
    picks.forEach((b) => b.classList.toggle('is-on', b === button))
    view.src = button.dataset.src
    label.textContent = button.dataset.label
  }
  picks.forEach((button) => {
    button.addEventListener('pointerenter', () => pick(button))
    button.addEventListener('focus', () => pick(button))
    button.addEventListener('click', () => pick(button))
  })
  // Fetch every variant once the page (or popup) has loaded, so swapping is instant
  const preload = () => picks.forEach((b) => (new Image().src = b.dataset.src))
  const dialog = range.closest('dialog')
  if (dialog) dialog.addEventListener('toggle', preload, { once: true })
  else addEventListener('load', preload, { once: true })
})

// Journey: how long each stop lasted (the current one keeps counting)
document.querySelectorAll('[data-since]').forEach((el) => {
  const [y0, m0] = el.dataset.since.split('-').map(Number)
  const end = el.dataset.until ? el.dataset.until.split('-').map(Number) : [new Date().getFullYear(), new Date().getMonth() + 1]
  const months = (end[0] - y0) * 12 + (end[1] - m0) + 1
  const years = Math.floor(months / 12)
  const rest = months % 12
  el.textContent = [years && `${years} yr`, rest && `${rest} mo`].filter(Boolean).join(' ')
})

// Email: the address only exists once assembled here, so it isn't sitting in the HTML for scrapers
const mail = document.querySelector('.mail[data-user]')
if (mail) {
  const address = () => `${mail.dataset.user}@${mail.dataset.domain}`
  mail.addEventListener('click', (event) => {
    event.preventDefault()
    location.href = `mailto:${address()}`
  })
  const copy = document.getElementById('copy-mail')
  copy.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(address())
      copy.textContent = 'Copied ✓'
    } catch (e) {
      copy.textContent = address()
    }
    setTimeout(() => (copy.textContent = 'Copy address'), 2000)
  })
}

// Contact form (Web3Forms)
const form = document.getElementById('contact-form')
const status = document.getElementById('form-status')

// Terminal lights: one per field, lit once that field is filled in properly
const term = document.querySelector('.term')
if (term && form) {
  const fields = [...form.querySelectorAll('[name="name"], [name="email"], [name="message"]')]
  const dots = term.querySelectorAll('.term-dots i')
  const state = document.getElementById('term-state')
  const check = () => {
    let done = 0
    fields.forEach((field, i) => {
      const ok = field.value.trim() !== '' && field.checkValidity()
      dots[i].classList.toggle('is-on', ok)
      if (ok) done++
    })
    term.classList.toggle('is-ready', done === fields.length)
    state.textContent = done === fields.length ? 'ready' : `${done}/${fields.length}`
  }
  form.addEventListener('input', check)
  // reset fires before the fields clear, so check on the next tick
  form.addEventListener('reset', () => setTimeout(check))
}

// hCaptcha (Web3Forms' free sitekey): loaded only when the form is near, drawn in the site's theme
const captchaBox = document.getElementById('captcha')
let captchaId = null
if (captchaBox) {
  const theme = () => (document.documentElement.dataset.theme === 'light' ? 'light' : 'dark')
  // The normal widget is 303px wide; narrower forms (phones) get the compact one
  const size = () => (captchaBox.clientWidth < 310 ? 'compact' : 'normal')
  let drawnSize = null
  const draw = () => {
    captchaBox.replaceChildren()
    drawnSize = size()
    captchaId = window.hcaptcha.render(captchaBox, { sitekey: '50b2fe65-b00b-4b9e-ad62-3ba471098be2', theme: theme(), size: drawnSize })
  }
  addEventListener('resize', () => window.hcaptcha && drawnSize && size() !== drawnSize && draw())
  window.onCaptchaLoad = draw
  new IntersectionObserver((entries, observer) => {
    if (!entries[0].isIntersecting) return
    observer.disconnect()
    const script = document.createElement('script')
    script.src = 'https://js.hcaptcha.com/1/api.js?render=explicit&onload=onCaptchaLoad&recaptchacompat=off'
    script.async = true
    document.head.append(script)
  }, { rootMargin: '400px' }).observe(captchaBox)
  // Redraw in the new theme when it's switched
  new MutationObserver(() => window.hcaptcha && draw()).observe(document.documentElement, { attributeFilter: ['data-theme'] })
}

// Each step of a send prints as a terminal line, one after another
const wait = (ms) => new Promise((done) => setTimeout(done, reduceMotion ? 0 : ms))
async function say(text, kind = '') {
  const line = document.createElement('span')
  line.className = kind
  line.textContent = `> ${text}`
  status.append(line)
  await wait(380)
}

form?.addEventListener('submit', async (event) => {
  event.preventDefault()
  const button = form.querySelector('button[type="submit"]')
  const name = form.elements.namedItem('name').value.trim().split(/\s+/)[0]
  status.className = 'form-status'
  status.replaceChildren()
  if (captchaBox && !form.querySelector('[name="h-captcha-response"]')?.value) {
    await say('Error: tick the captcha first.', 'is-error')
    return
  }
  button.disabled = true
  await say('Sending...')

  try {
    const response = await fetch(form.action, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(Object.fromEntries(new FormData(form)))
    })
    const result = await response.json()
    if (!response.ok) throw new Error(result.message)
    await say('OK. Message delivered.', 'is-ok')
    term?.classList.add('is-sent')
    document.getElementById('term-state').textContent = 'sent'
    await say(`Thanks, ${name}. I'll get back to you soon.`)
    // Keep the lit dots on screen for a moment, then clear the form
    await wait(4000)
    term?.classList.remove('is-sent')
    form.reset()
  } catch (error) {
    await say("Error: couldn't send. Try email instead.", 'is-error')
  } finally {
    button.disabled = false
    if (captchaId !== null) window.hcaptcha?.reset(captchaId)
  }
})

document.getElementById('year').textContent = new Date().getFullYear()

// Command menu: Ctrl+K (or the rail button) to jump anywhere
const cmdk = document.getElementById('cmdk')
if (cmdk) {
  const query = document.getElementById('cmdk-q')
  const empty = document.getElementById('cmdk-empty')
  const items = [...cmdk.querySelectorAll('.cmdk-item')]
  let shown = items
  let active = 0

  const highlight = (index) => {
    active = (index + shown.length) % shown.length
    items.forEach((item) => item.classList.toggle('is-active', item === shown[active]))
    shown[active]?.scrollIntoView({ block: 'nearest' })
  }
  const filter = () => {
    const words = query.value.toLowerCase().split(/\s+/).filter(Boolean)
    shown = items.filter((item) => {
      const text = `${item.textContent} ${item.dataset.keys}`.toLowerCase()
      const ok = words.every((word) => text.includes(word))
      item.parentElement.hidden = !ok
      return ok
    })
    // A group label only shows while something under it does
    cmdk.querySelectorAll('.cmdk-group').forEach((group) => {
      let next = group.nextElementSibling
      let any = false
      while (next && !next.classList.contains('cmdk-group')) {
        if (!next.hidden) any = true
        next = next.nextElementSibling
      }
      group.hidden = !any
    })
    empty.hidden = shown.length > 0
    highlight(0)
  }
  const open = () => {
    if (cmdk.open) return
    document.querySelectorAll('dialog[open]').forEach((d) => d.close())
    query.value = ''
    filter()
    cmdk.showModal()
    lenis?.stop()
  }

  document.getElementById('cmdk-open').addEventListener('click', open)
  addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault()
      cmdk.open ? cmdk.close() : open()
    }
  })
  cmdk.addEventListener('close', () => lenis?.start())
  cmdk.addEventListener('click', (event) => {
    if (event.target === cmdk) cmdk.close()
  })
  query.addEventListener('input', filter)
  query.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown') highlight(active + 1)
    else if (event.key === 'ArrowUp') highlight(active - 1)
    else if (event.key === 'Enter') shown[active]?.click()
    else return
    event.preventDefault()
  })
  items.forEach((item) => item.addEventListener('pointermove', () => highlight(shown.indexOf(item))))

  // Capture phase: close the menu and restart scrolling before an in-page link scrolls
  cmdk.addEventListener('click', async (event) => {
    const item = event.target.closest('.cmdk-item')
    if (!item) return
    const action = item.dataset.action
    if (action === 'email') {
      const address = `${item.dataset.user}@${item.dataset.domain}`
      const hint = item.querySelector('span')
      try {
        await navigator.clipboard.writeText(address)
        hint.textContent = 'copied ✓'
      } catch (e) {
        hint.textContent = address
      }
      setTimeout(() => (hint.textContent = 'copy'), 2000)
      return
    }
    cmdk.close()
    lenis?.start()
    if (action === 'theme') document.getElementById('theme-toggle').click()
  }, true)
}
