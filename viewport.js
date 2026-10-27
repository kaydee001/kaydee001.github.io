// Hero viewport: an isometric turntable stand in the style of the Anatomy figures. Solid parts in paper tones with
// four-step shading and thin outlines, seen through a true isometric (orthographic) camera. The faceted mesh sits on
// a platter that turns slowly; drag to spin it. A knob geared to the platter turns with it, and an index mark on the
// platter reads the angle against the ticks of the fixed ring. The subject is models/hero.glb, drawn in the same style;
// the faceted sphere stands in only if that file can't be loaded.
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const host = document.getElementById('viewport')
const canvas = document.getElementById('viewport-canvas')
const stats = document.getElementById('hud-stats')
const fpsLabel = document.getElementById('hud-fps')
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true })
// Phones render at 1.5x at most: the difference isn't visible at that size, and it's ~40% less GPU work
renderer.setPixelRatio(Math.min(devicePixelRatio, matchMedia('(max-width: 900px)').matches ? 1.5 : 2))

const scene = new THREE.Scene()
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -1000, 1000)
const target = new THREE.Vector3()

// Palettes per theme: paper tones for solids, line tones for outlines (hi on the subject, mid on structure, lit accent)
const PALETTES = {
  dark: { base: 0x161d28, part: 0x1b2330, subject: 0x1d2735, glow: 0x6fd3ff, glow2: 0x3d7bff, hi: 0xc9d6e4, mid: 0x55647a, lo: 0x2f3a4a, lit: 0x6fd3ff, halo: 'rgba(0,0,0,0.75)' },
  light: { base: 0xf3f6f9, part: 0xfbfcfd, subject: 0xffffff, glow: 0x368ba8, glow2: 0x236a84, hi: 0x202c3c, mid: 0x7d8b9c, lo: 0xb7c3cf, lit: 0x368ba8, halo: 'rgba(32,44,60,0.22)' },
}

// Four-step shading, like the kit's four side tones plus a lighter top
const steps = new Uint8Array([120, 160, 205, 255])
const gradient = new THREE.DataTexture(steps, steps.length, 1, THREE.RedFormat)
gradient.minFilter = gradient.magFilter = THREE.NearestFilter
gradient.needsUpdate = true

const fills = { base: [], part: [], subject: [], glow: [], glow2: [] }
const lines = { hi: [], mid: [], lo: [], lit: [] }
const resolution = { value: new THREE.Vector2(1, 1) }

function fillMaterial(kind) {
  const material = new THREE.MeshToonMaterial({ gradientMap: gradient, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 })
  fills[kind].push(material)
  return material
}

function lineMaterial(tone) {
  const material = new THREE.LineBasicMaterial()
  lines[tone].push(material)
  return material
}

// Silhouette: the back faces pushed out along their normals by a fixed number of screen pixels
function outlineMaterial(tone, width = 1.1) {
  const material = new THREE.ShaderMaterial({
    uniforms: { uColor: { value: new THREE.Color() }, uWidth: { value: width }, uRes: resolution },
    vertexShader: `
      uniform float uWidth;
      uniform vec2 uRes;
      void main() {
        vec4 clip = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        vec2 dir = (projectionMatrix * vec4(normalize(normalMatrix * normal), 0.0)).xy;
        float len = length(dir);
        if (len > 1e-5) clip.xy += dir / len * uWidth * 2.0 / uRes * clip.w;
        gl_Position = clip;
      }`,
    fragmentShader: `uniform vec3 uColor; void main() { gl_FragColor = vec4(uColor, 1.0); }`,
    side: THREE.BackSide,
  })
  material.userData.tone = tone
  lines[tone].push(material)
  return material
}

// A solid part: shaded fill, silhouette and crease lines (edges sharper than `crease` degrees)
function part(geometry, { kind = 'part', tone = 'mid', crease = 30 } = {}) {
  const group = new THREE.Group()
  group.add(new THREE.Mesh(geometry, fillMaterial(kind)))
  group.add(new THREE.Mesh(geometry, outlineMaterial(tone)))
  group.add(new THREE.LineSegments(new THREE.EdgesGeometry(geometry, crease), lineMaterial(tone)))
  return group
}

function roundedRect(w, d, r) {
  const shape = new THREE.Shape()
  const x = -w / 2
  const y = -d / 2
  shape.moveTo(x + r, y)
  shape.lineTo(x + w - r, y)
  shape.quadraticCurveTo(x + w, y, x + w, y + r)
  shape.lineTo(x + w, y + d - r)
  shape.quadraticCurveTo(x + w, y + d, x + w - r, y + d)
  shape.lineTo(x + r, y + d)
  shape.quadraticCurveTo(x, y + d, x, y + d - r)
  shape.lineTo(x, y + r)
  shape.quadraticCurveTo(x, y, x + r, y)
  return shape
}

// A rounded slab lying on the floor, from y0 to y0 + h
function slab(w, d, h, r, y0, bevel = 0.6) {
  const geometry = new THREE.ExtrudeGeometry(roundedRect(w - bevel * 2, d - bevel * 2, Math.max(0.1, r - bevel)), {
    depth: h - bevel * 2,
    bevelEnabled: bevel > 0,
    bevelThickness: bevel,
    bevelSize: bevel,
    bevelSegments: 2,
    curveSegments: 8,
  })
  geometry.rotateX(-Math.PI / 2)
  geometry.translate(0, y0 + bevel, 0)
  return geometry
}

const cylinder = (r, h, y0, segments = 48) => new THREE.CylinderGeometry(r, r, h, segments).translate(0, y0 + h / 2, 0)

function lineSegments(points, tone) {
  return new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(points), lineMaterial(tone))
}

function outlineLoop(w, d, r, y, tone) {
  const points = roundedRect(w, d, r).getPoints(10).map((p) => new THREE.Vector3(p.x, y, -p.y))
  return new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points), lineMaterial(tone))
}

// ---------------------------------------------------------------- the stand
const BASE = { w: 150, d: 112, h: 8, r: 9 }
const TABLE = { x: -12, z: -6 }
const RING_R = 46
const RING_TOP = 4
const PLATTER_R = 40
const PLATTER_TOP = RING_TOP + 3
const KNOB = { x: 54, z: 38 }
const GEAR = 3 // the knob turns three times per platter turn

const stand = new THREE.Group()
scene.add(stand)

// Soft halo under the base
const haloCanvas = document.createElement('canvas')
haloCanvas.width = haloCanvas.height = 128
const haloTexture = new THREE.CanvasTexture(haloCanvas)
const halo = new THREE.Mesh(new THREE.PlaneGeometry(BASE.w * 1.35, BASE.d * 1.45), new THREE.MeshBasicMaterial({ map: haloTexture, transparent: true, depthWrite: false }))
halo.rotation.x = -Math.PI / 2
halo.position.y = -BASE.h - 4.6
stand.add(halo)

stand.add(part(slab(BASE.w, BASE.d, BASE.h, BASE.r, -BASE.h, 1.2), { kind: 'base' }))
stand.add(outlineLoop(BASE.w - 10, BASE.d - 10, BASE.r - 4, 0.05, 'lo'))
for (const [sx, sz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
  const foot = new THREE.Group()
  foot.add(part(cylinder(7, 1.6, -BASE.h - 4.6, 32), { kind: 'base', tone: 'lo' }))
  foot.add(part(cylinder(5.4, 3, -BASE.h - 3, 32), { kind: 'base' }))
  foot.position.set(sx * (BASE.w / 2 - 20), 0, sz * (BASE.d / 2 - 20))
  stand.add(foot)
  const screw = part(cylinder(1.2, 0.4, 0, 16), { tone: 'mid' })
  screw.position.set(sx * (BASE.w / 2 - 9), 0, sz * (BASE.d / 2 - 9))
  stand.add(screw)
}

// Label plate: three rule lines for printed text
const label = new THREE.Group()
label.add(part(slab(34, 18, 0.8, 1.5, 0, 0.2), { tone: 'mid' }))
label.add(lineSegments([[-13, 6, 24], [-13, 9.5, 18], [-13, 13, 21]].flatMap(([x, z, len]) => [new THREE.Vector3(x, 0.85, z - 9), new THREE.Vector3(x + len, 0.85, z - 9)]), 'lo'))
label.position.set(-46, 0, 40)
stand.add(label)

// Fixed bearing ring with degree ticks every 5 degrees, a long one every 30
const ring = new THREE.Group()
ring.add(part(cylinder(RING_R, RING_TOP, 0, 96), { tone: 'mid' }))
const ticks = []
for (let i = 0; i < 72; i++) {
  const a = (i / 72) * Math.PI * 2
  const inner = i % 6 === 0 ? RING_R - 4.2 : RING_R - 2.4
  ticks.push(new THREE.Vector3(Math.cos(a) * inner, RING_TOP + 0.05, Math.sin(a) * inner), new THREE.Vector3(Math.cos(a) * (RING_R - 0.6), RING_TOP + 0.05, Math.sin(a) * (RING_R - 0.6)))
}
ring.add(lineSegments(ticks, 'mid'))
ring.position.set(TABLE.x, 0, TABLE.z)
stand.add(ring)

// Platter: turns with the model on it, and carries the index mark that reads the angle
const platter = new THREE.Group()
platter.add(part(cylinder(PLATTER_R, 3, RING_TOP, 96), { tone: 'mid' }))
platter.add(part(cylinder(7, 1.4, PLATTER_TOP, 32), { tone: 'mid' }))
const mark = new THREE.Vector3(PLATTER_R - 0.4, PLATTER_TOP + 0.06, 0)
platter.add(lineSegments([new THREE.Vector3(PLATTER_R - 7, PLATTER_TOP + 0.06, 0), mark], 'lit'))
platter.position.set(TABLE.x, 0, TABLE.z)
stand.add(platter)

// Where the subject stands; the record player moves it onto its own platter once it loads
const seat = new THREE.Group()
seat.position.y = PLATTER_TOP + 1.4
platter.add(seat)
// The subject hangs off this, so a click can make it hop without moving the seat
const hop = new THREE.Group()
seat.add(hop)

// The subject sits on the platter: shaded fill, silhouette and lit crease lines
const FIT = { w: PLATTER_R * 1.7, h: 50 } // widest side and height it may take up
let meshStats = 'loading mesh'

// Glowing parts are flat colour with no lines (lines would bury small dense parts); the rest is shaded and outlined
function subject(parts, crease) {
  const group = new THREE.Group()
  for (const { geometry, glow } of parts) {
    if (glow) {
      const material = new THREE.MeshBasicMaterial()
      fills[glow].push(material)
      group.add(new THREE.Mesh(geometry, material))
      continue
    }
    group.add(new THREE.Mesh(geometry, fillMaterial('subject')))
    group.add(new THREE.Mesh(geometry, outlineMaterial('hi', 1.3)))
    group.add(new THREE.LineSegments(new THREE.EdgesGeometry(geometry, crease), lineMaterial('lit')))
  }
  return group
}

// A part glows if its material is emissive: blue-ish emission maps to the accent, anything else to the deeper blue
function glowOf(material) {
  const e = material.emissive
  if (!e || e.r + e.g + e.b < 0.05) return null
  return e.b >= e.r ? 'glow' : 'glow2'
}

// Vertex count as a modeller would read it (shared corners counted once) and the triangle count
function statsOf(geometries) {
  const unique = new Set()
  let faces = 0
  for (const geometry of geometries) {
    const pos = geometry.attributes.position
    for (let i = 0; i < pos.count; i++) unique.add(`${pos.getX(i).toFixed(3)},${pos.getY(i).toFixed(3)},${pos.getZ(i).toFixed(3)}`)
    faces += (geometry.index ? geometry.index.count : pos.count) / 3
  }
  return `verts ${unique.size.toLocaleString('en')} · faces ${faces.toLocaleString('en')}`
}

function showSphere() {
  const R = 23
  const geometry = new THREE.IcosahedronGeometry(R, 1)
  const model = subject([{ geometry }], 1)
  model.position.y = R * 0.95
  hop.add(model)
  meshStats = statsOf([geometry])
  applyTheme()
}

// A copy of every mesh in a loaded file with its transform baked in (positions only: the site does its own shading)
function bakedMeshes(gltf) {
  gltf.scene.updateMatrixWorld(true)
  const meshes = []
  gltf.scene.traverse((object) => {
    if (!object.isMesh) return
    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', object.geometry.attributes.position.clone())
    if (object.geometry.index) geometry.setIndex(object.geometry.index.clone())
    geometry.applyMatrix4(object.matrixWorld)
    geometry.computeVertexNormals()
    geometry.computeBoundingBox()
    meshes.push({ name: object.name, geometry, material: object.material })
  })
  return meshes
}

const loader = new GLTFLoader()

// The subject: centred on the seat and scaled to fit the platter
loader.load(new URL('./models/hero.glb', import.meta.url).href, (gltf) => {
  const meshes = bakedMeshes(gltf)
  const geometries = meshes.map((m) => m.geometry)
  const parts = meshes.map((m) => ({ geometry: m.geometry, glow: glowOf(m.material) }))
  if (!geometries.length) return showSphere()
  const box = new THREE.Box3()
  for (const geometry of geometries) {
    geometry.computeBoundingBox()
    box.union(geometry.boundingBox)
  }
  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())
  const scale = Math.min(FIT.w / Math.max(size.x, size.z), FIT.h / size.y)
  for (const geometry of geometries) geometry.translate(-center.x, -box.min.y, -center.z).scale(scale, scale, scale)
  hop.add(subject(parts, 55))
  meshStats = statsOf(geometries)
  applyTheme()
}, undefined, showSphere)

// Knob geared to the platter, with knurling and a pointer
const knob = new THREE.Group()
knob.add(part(cylinder(4.4, 3, 0, 32), { tone: 'mid' }))
knob.add(part(cylinder(7, 6, 3, 40), { tone: 'mid' }))
const knurl = []
for (let i = 0; i < 36; i++) {
  const a = (i / 36) * Math.PI * 2
  knurl.push(new THREE.Vector3(Math.cos(a) * 7.02, 3.6, Math.sin(a) * 7.02), new THREE.Vector3(Math.cos(a) * 7.02, 8.4, Math.sin(a) * 7.02))
}
knob.add(lineSegments(knurl, 'lo'))
knob.add(lineSegments([new THREE.Vector3(0, 9.05, 0), new THREE.Vector3(6, 9.05, 0)], 'hi'))
knob.position.set(KNOB.x, 0, KNOB.z)
stand.add(knob)

// The record player (models/player.glb) replaces the built-in stand. It is scaled to the stand's footprint; the
// largest round part is the platter, and every part lying on it turns with it. If the file can't load, the stand stays.
const PLAYER_TURN = THREE.MathUtils.degToRad(90) // turns the player on the spot; change in steps of 90
// Parts of the player that glow in the accent blue, by their Blender name (three.js drops the dots, so compare without them)
const PLAYER_GLOW = ['Plane.001']
const bare = (name) => name.replace(/[^a-z0-9]/gi, '').toLowerCase()
const glowing = (name) => PLAYER_GLOW.some((n) => bare(n) === bare(name))
// Flat accent colour with a lit outline, so the part reads as a light on the deck
function glowPart(geometry) {
  const group = new THREE.Group()
  const material = new THREE.MeshBasicMaterial()
  fills.glow.push(material)
  group.add(new THREE.Mesh(geometry, material))
  group.add(new THREE.Mesh(geometry, outlineMaterial('lit', 1.6)))
  return group
}
loader.load(new URL('./models/player.glb', import.meta.url).href, (gltf) => {
  const meshes = bakedMeshes(gltf)
  if (!meshes.length) return
  for (const m of meshes) m.geometry.rotateY(PLAYER_TURN).computeBoundingBox()
  const box = new THREE.Box3()
  for (const m of meshes) box.union(m.geometry.boundingBox)
  const size = box.getSize(new THREE.Vector3())
  const center = box.getCenter(new THREE.Vector3())
  const scale = BASE.w / Math.max(size.x, size.z)
  for (const m of meshes) {
    m.geometry.translate(-center.x, -box.min.y, -center.z).scale(scale, scale, scale).translate(0, -BASE.h, 0)
    m.geometry.computeBoundingBox()
  }
  const flat = (b) => {
    const s = b.getSize(new THREE.Vector3())
    return { s, c: b.getCenter(new THREE.Vector3()) }
  }
  const round = meshes.filter((m) => {
    const { s } = flat(m.geometry.boundingBox)
    return Math.abs(s.x - s.z) < 0.05 * Math.max(s.x, s.z)
  })
  const disc = round.sort((a, b) => flat(b.geometry.boundingBox).s.x - flat(a.geometry.boundingBox).s.x)[0]
  if (!disc) return
  const { s: ds, c: dc } = flat(disc.geometry.boundingBox)
  const radius = ds.x / 2
  const onPlatter = (m) => {
    const { s, c } = flat(m.geometry.boundingBox)
    return Math.hypot(c.x - dc.x, c.z - dc.z) + Math.max(s.x, s.z) / 2 <= radius * 1.02 && m.geometry.boundingBox.min.y >= disc.geometry.boundingBox.min.y - 0.01
  }

  // Swap the built-in parts out, keeping the halo, the platter group (it turns) and the seat on it
  for (const child of [...stand.children]) if (child !== halo && child !== platter) stand.remove(child)
  for (const child of [...platter.children]) if (child !== seat) platter.remove(child)
  platter.position.set(dc.x, 0, dc.z)

  const largest = meshes.reduce((a, b) => (flat(a.geometry.boundingBox).s.x * flat(a.geometry.boundingBox).s.z >= flat(b.geometry.boundingBox).s.x * flat(b.geometry.boundingBox).s.z ? a : b))
  let top = disc.geometry.boundingBox.max.y
  for (const m of meshes) {
    if (onPlatter(m)) {
      m.geometry.translate(-dc.x, 0, -dc.z)
      platter.add(glowing(m.name) ? glowPart(m.geometry) : part(m.geometry, { tone: 'mid' }))
      top = Math.max(top, m.geometry.boundingBox.max.y)
    } else {
      stand.add(glowing(m.name) ? glowPart(m.geometry) : part(m.geometry, { kind: m === largest ? 'base' : 'part', tone: 'mid' }))
    }
  }
  seat.position.y = top + 0.4
  deckHalf.x = (size.x * scale) / 2 - 5
  deckHalf.z = (size.z * scale) / 2 - 5
  applyTheme()
})

const ambient = new THREE.AmbientLight(0xffffff, 0.55)
scene.add(ambient)
const sun = new THREE.DirectionalLight(0xffffff, 0.95)
sun.position.set(-0.6, 1, 0.35)
scene.add(sun)

function applyTheme() {
  const light = document.documentElement.dataset.theme === 'light'
  const palette = PALETTES[light ? 'light' : 'dark']
  // Paper needs flatter, brighter light so the solids stay pale instead of going grey
  ambient.intensity = light ? 1.5 : 0.55
  sun.intensity = light ? 0.55 : 0.95
  for (const kind of Object.keys(fills)) for (const m of fills[kind]) m.color.set(palette[kind])
  for (const tone of Object.keys(lines)) {
    for (const m of lines[tone]) (m.uniforms ? m.uniforms.uColor.value : m.color).set(palette[tone])
  }
  const g = haloCanvas.getContext('2d')
  g.clearRect(0, 0, 128, 128)
  const shade = g.createRadialGradient(64, 64, 8, 64, 64, 64)
  shade.addColorStop(0, palette.halo)
  shade.addColorStop(1, 'rgba(0,0,0,0)')
  g.fillStyle = shade
  g.fillRect(0, 0, 128, 128)
  haloTexture.needsUpdate = true
}
applyTheme()
addEventListener('themechange', applyTheme)

// ---------------------------------------------------------------- camera: isometric, leaning a little toward the cursor
const AZIMUTH = 45
const ELEVATION = 30
let view = { height: 260, shift: 0 }
let leanAz = 0
let leanEl = 0
let leanAzTo = 0
let leanElTo = 0

function placeCamera() {
  const az = THREE.MathUtils.degToRad(AZIMUTH + leanAz)
  const el = THREE.MathUtils.degToRad(ELEVATION + leanEl)
  const dir = new THREE.Vector3(Math.cos(el) * Math.cos(az), Math.sin(el), Math.cos(el) * Math.sin(az))
  // Shift the view sideways so the stand sits clear of the intro text on wide screens (this vector points screen-left)
  const right = new THREE.Vector3(-Math.sin(az), 0, Math.cos(az))
  target.set(0, 16, 0).addScaledVector(right, view.shift)
  camera.position.copy(target).addScaledVector(dir, 400)
  camera.lookAt(target)
}

function resize() {
  const { clientWidth: w, clientHeight: h } = host
  renderer.setSize(w, h, false)
  resolution.value.set(w, h)
  const aspect = w / h
  const wide = matchMedia('(min-width: 901px)').matches && aspect > 1.2
  view.height = wide ? 215 : 190
  const halfW = (view.height / 2) * aspect
  // Measure the shift against the content column (the hero's padded box), not the whole canvas,
  // so on very wide screens the stand stays inside the column with the text and status box
  const hero = host.closest('.hero')
  const pad = hero ? parseFloat(getComputedStyle(hero).paddingLeft) || 0 : 0
  const column = Math.max(0, w - pad * 2) / w
  view.shift = wide ? halfW * 0.36 * column : 0
  camera.left = -halfW
  camera.right = halfW
  camera.top = view.height / 2
  camera.bottom = -view.height / 2
  camera.updateProjectionMatrix()
  placeCamera()
}
new ResizeObserver(resize).observe(host)
resize()

// ---------------------------------------------------------------- input: drag spins the platter, hover leans the camera
let angle = -Math.PI / 4 // start with the model facing the camera (the view looks in from 45 degrees)
let velocity = reduceMotion ? 0 : 0.18 // radians per second
let dragging = false
let lastX = 0
let downX = 0
let downY = 0

// Click on the subject: a scan ping. It hops, a ring sweeps out across the deck, the platter gets a kick
// and the readout blinks. About a second, then everything settles back.
const raycaster = new THREE.Raycaster()
const pointerNdc = new THREE.Vector2()
function overSubject(e) {
  const rect = canvas.getBoundingClientRect()
  pointerNdc.set(((e.clientX - rect.left) / rect.width) * 2 - 1, -((e.clientY - rect.top) / rect.height) * 2 + 1)
  raycaster.setFromCamera(pointerNdc, camera)
  return raycaster.intersectObject(hop, true).length > 0
}

const PING = 1.1 // seconds; a click during a scan is ignored, so spamming can't stack effects
const MAX_SPIN = 5 // radians per second, however the platter is flicked
const effectMaterials = new Set()
function effectMaterial(map = null) {
  const material = new THREE.MeshBasicMaterial({ map, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide })
  lines.lit.push(material)
  effectMaterials.add(material)
  return material
}

// Sonar rings that sweep out across the deck
const rings = [0, 0.16].map((delay) => {
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.975, 1, 160), effectMaterial())
  ring.rotation.x = -Math.PI / 2
  ring.visible = false
  ring.userData.delay = delay
  // On the seat, which survives the record player swapping out the platter's parts
  seat.add(ring)
  return ring
})

// A voxel wave: a grid of small cubes over the deck. Each one pops up and drops back as the sonar front passes it,
// so a ripple of cubes rolls outward from the platter. It sits in the scene, not on the platter, so it doesn't turn.
const VOXEL = { step: 4, size: 1.8, reach: 82 }
const voxelSpots = []
for (let x = -VOXEL.reach; x <= VOXEL.reach; x += VOXEL.step) {
  for (let z = -VOXEL.reach; z <= VOXEL.reach; z += VOXEL.step) {
    const d = Math.hypot(x, z)
    if (d > 12 && d <= VOXEL.reach) voxelSpots.push({ x, z, d, jitter: Math.random() })
  }
}
// Shade the faces like the rest of the scene (lit top, two darker sides), so they read as cubes, not hexagons
const voxelBox = new THREE.BoxGeometry(VOXEL.size, VOXEL.size, VOXEL.size)
{
  // BoxGeometry faces come in the order +x, -x, +y, -y, +z, -z; four vertices each
  const shade = [0.55, 0.55, 1, 0.3, 0.78, 0.78]
  voxelBox.setAttribute('color', new THREE.Float32BufferAttribute(shade.flatMap((v) => Array(12).fill(v)), 3))
}
const voxelMaterial = effectMaterial()
voxelMaterial.vertexColors = true
// Solid cubes in both themes: additive light would flatten the face shading back into hexagons
voxelMaterial.userData.solid = true
const voxels = new THREE.InstancedMesh(voxelBox, voxelMaterial, voxelSpots.length)
voxels.frustumCulled = false
voxels.visible = false
scene.add(voxels)
// The deck's half size, so cubes stay over the player (set properly once the player loads)
const deckHalf = { x: BASE.w / 2 - 5, z: BASE.d / 2 - 5 }
const voxelMatrix = new THREE.Matrix4()
const voxelPos = new THREE.Vector3()
const voxelScale = new THREE.Vector3()
const voxelTurn = new THREE.Quaternion()

// Additive light vanishes on the light theme's pale background, so there the effects paint normally
function effectBlending() {
  const light = document.documentElement.dataset.theme === 'light'
  for (const m of effectMaterials) {
    m.blending = light || m.userData.solid ? THREE.NormalBlending : THREE.AdditiveBlending
    m.needsUpdate = true
  }
}
effectBlending()
addEventListener('themechange', effectBlending)

const hudName = document.querySelector('.hud-tr span')
let hudText = ''
const setHud = (text) => {
  if (hudName && text !== hudText) hudName.textContent = hudText = text
}

let pingAt = -1
const scanning = () => pingAt >= 0 && (performance.now() - pingAt) / 1000 < PING
function ping() {
  if (scanning()) return
  pingAt = performance.now()
  if (!reduceMotion) velocity = Math.min(MAX_SPIN, velocity + 2.4)
}

const easeOut = (t) => 1 - (1 - t) ** 3
const white = new THREE.Color(0xffffff)
const ink = new THREE.Color(0x0b3d52)
const mix = new THREE.Color()
let flashing = false
function updatePing(now) {
  const t = pingAt < 0 ? Infinity : (now - pingAt) / 1000
  const light = document.documentElement.dataset.theme === 'light'
  const palette = PALETTES[light ? 'light' : 'dark']

  // Hop: up and back down
  hop.position.y = !reduceMotion && t < 0.7 ? Math.sin((t / 0.7) * Math.PI) * 6 * (1 - (t / 0.7) * 0.3) : 0

  for (const ring of rings) {
    const k = (t - ring.userData.delay) / (PING - ring.userData.delay)
    ring.visible = k >= 0 && k < 1
    if (!ring.visible) continue
    ring.scale.setScalar(8 + easeOut(k) * BASE.w * 0.48)
    ring.position.y = -0.3
    ring.material.opacity = (1 - k) ** 1.6 * (ring.userData.delay ? 0.35 : 0.8)
  }

  // Voxel wave: rides the main sonar front; cubes near it pop up, the rest stay hidden
  voxels.visible = t < PING
  if (voxels.visible) {
    const k = t / PING
    const front = 8 + easeOut(k) * BASE.w * 0.48
    const fade = (1 - k) ** 1.2
    const baseY = seat.position.y - 0.3
    voxels.material.opacity = reduceMotion ? 0.5 * fade : 0.85
    voxelSpots.forEach((v, n) => {
      const wx = platter.position.x + v.x
      const wz = platter.position.z + v.z
      const inside = Math.abs(wx) < deckHalf.x && Math.abs(wz) < deckHalf.z
      const g = inside ? Math.exp(-(((v.d - front) / 5) ** 2)) * fade : 0
      const lift = reduceMotion ? 0 : g * (3 + v.jitter * 2.5)
      voxelPos.set(wx, baseY + VOXEL.size / 2 + lift, wz)
      voxelScale.setScalar(g < 0.04 ? 0 : Math.min(1, g * 1.4))
      voxels.setMatrixAt(n, voxelMatrix.compose(voxelPos, voxelTurn, voxelScale))
    })
    voxels.instanceMatrix.needsUpdate = true
  }

  // Flash: the subject's lines and every glowing part brighten, then settle back to the theme colour
  const f = t < 0.5 ? (1 - t / 0.5) ** 2 : 0
  if (f > 0) {
    flashing = true
    const to = light ? ink : white
    for (const m of lines.lit) if (!effectMaterials.has(m)) (m.uniforms ? m.uniforms.uColor.value : m.color).copy(mix.set(palette.lit).lerp(to, f * 0.75))
    for (const kind of ['glow', 'glow2']) for (const m of fills[kind]) m.color.copy(mix.set(palette[kind]).lerp(to, f * 0.6))
  } else if (flashing) {
    flashing = false
    applyTheme()
  }

  // Readout: a scan percentage, then the result
  if (t < 0.75) setHud(`kd_mesh.001 · scan ${String(Math.round((t / 0.75) * 100)).padStart(3, ' ')}%`)
  else if (t < 1.6) setHud('kd_mesh.001 · scan ok')
  else setHud('kd_mesh.001')
}

canvas.addEventListener('pointerdown', (e) => {
  dragging = true
  lastX = downX = e.clientX
  downY = e.clientY
  canvas.setPointerCapture(e.pointerId)
})
canvas.addEventListener('pointerup', (e) => {
  dragging = false
  // A click, not the end of a drag
  if (Math.hypot(e.clientX - downX, e.clientY - downY) < 5 && overSubject(e)) ping()
})
canvas.addEventListener('pointermove', (e) => {
  const rect = canvas.getBoundingClientRect()
  leanAzTo = ((e.clientX - rect.left) / rect.width - 0.5) * 8
  leanElTo = ((e.clientY - rect.top) / rect.height - 0.5) * -5
  if (!dragging) return
  const step = (e.clientX - lastX) * 0.012
  angle += step
  velocity = Math.max(-MAX_SPIN, Math.min(MAX_SPIN, step * 30))
  lastX = e.clientX
})
canvas.addEventListener('pointerleave', () => {
  leanAzTo = 0
  leanElTo = 0
})

// Render only while the viewport is on screen
let visible = true
new IntersectionObserver(([entry]) => (visible = entry.isIntersecting)).observe(host)

let frames = 0
let fpsClock = performance.now()
let previous = performance.now()
function loop(now) {
  requestAnimationFrame(loop)
  const dt = Math.min((now - previous) / 1000, 1 / 20)
  previous = now
  if (!visible) return
  if (!dragging && !reduceMotion) {
    // A flick coasts, then eases back to the slow idle turn
    velocity += (0.18 - velocity) * (1 - Math.exp(-dt / 1.2))
    angle += velocity * dt
  }
  leanAz += (leanAzTo - leanAz) * (1 - Math.exp(-dt / 0.35))
  leanEl += (leanElTo - leanEl) * (1 - Math.exp(-dt / 0.35))
  placeCamera()
  platter.rotation.y = -angle
  knob.rotation.y = angle * GEAR
  updatePing(now)
  renderer.render(scene, camera)

  const degrees = ((((angle * 180) / Math.PI) % 360) + 360) % 360
  stats.textContent = `${meshStats} · ${String(Math.round(degrees)).padStart(3, '0')}°`
  frames++
  if (now - fpsClock > 500) {
    fpsLabel.textContent = `${Math.round((frames * 1000) / (now - fpsClock))} fps`
    frames = 0
    fpsClock = now
  }
}
requestAnimationFrame(loop)
