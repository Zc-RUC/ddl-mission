// DDL.MISSION desktop widget
// Drag with the top grip bar; position is remembered. Height auto-fits content.

export const className = `
  top: 0;
  left: 0;
`

const WIDTH = 300
const POS_KEY = 'ddl-widget-pos-v2'
// Manual fixed position: set x to a number (px from left) to pin it there.
// x = null means dock to the right edge of the screen. y = px from top.
const MANUAL_POS = { x: null, y: 60 }

function setup(el) {
  if (!el || el.dataset.ddlReady) return
  el.dataset.ddlReady = '1'

  const frame = el.querySelector('iframe')
  const grip = el.querySelector('[data-grip]')
  const screenW = () => (screen.availWidth || window.innerWidth || 1440)

  let saved = null
  try { saved = JSON.parse(localStorage.getItem(POS_KEY)) } catch (e) {}
  try { localStorage.removeItem('ddl-widget-pos') } catch (e) {}
  const pos = {
    x: saved && typeof saved.x === 'number' ? saved.x : (MANUAL_POS.x != null ? MANUAL_POS.x : screenW() - WIDTH - 24),
    y: saved && typeof saved.y === 'number' ? saved.y : MANUAL_POS.y,
  }
  const apply = () => { el.style.transform = `translate(${pos.x}px, ${pos.y}px)` }
  apply()

  window.addEventListener('message', e => {
    if (!e.data) return
    if (e.data.ddlMissionHeight) {
      frame.style.height = Math.min(e.data.ddlMissionHeight, Math.round(window.innerHeight * 0.72)) + 'px'
    }
    if (e.data.ddlOpen && e.origin === 'http://127.0.0.1:8791' && /^https?:\/\//.test(e.data.ddlOpen)) {
      fetch('http://127.0.0.1:8791/__dbg?m=msg-received').catch(() => {})
      fetch('/run/', { method: 'POST', body: 'open ' + e.data.ddlOpen + '\n' })
        .then(r => fetch('http://127.0.0.1:8791/__dbg?m=run-' + r.status).catch(() => {}))
        .catch(() => fetch('http://127.0.0.1:8791/__dbg?m=run-fail').catch(() => {}))
    }
  })

  let dragging = false, sx = 0, sy = 0, ox = 0, oy = 0
  grip.addEventListener('mousedown', e => {
    dragging = true; sx = e.clientX; sy = e.clientY; ox = pos.x; oy = pos.y
    e.preventDefault()
  })
  window.addEventListener('mousemove', e => {
    if (!dragging) return
    pos.x = Math.max(0, Math.min(ox + e.clientX - sx, screenW() - WIDTH))
    pos.y = Math.max(0, Math.min(oy + e.clientY - sy, window.innerHeight - 40))
    apply()
  })
  window.addEventListener('mouseup', () => {
    if (!dragging) return
    dragging = false
    try { localStorage.setItem(POS_KEY, JSON.stringify(pos)) } catch (e) {}
  })
}

export const render = () => (
  <div ref={setup} style={{
    position: 'absolute', top: '0', left: '0',
    width: WIDTH + 'px',
    border: '1px solid #2c2c2c', borderRadius: '12px', overflow: 'hidden',
    background: '#000', boxShadow: '0 10px 34px rgba(0, 0, 0, 0.65)',
  }}>
    <div data-grip="1" style={{
      height: '16px', cursor: 'move', userSelect: 'none',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      color: '#3a3a3a', fontSize: '9px', letterSpacing: '4px',
      borderBottom: '1px solid #1d1d1d', fontFamily: 'monospace',
    }}>...</div>
    <iframe
      src="http://127.0.0.1:8791/widget.html"
      style={{ display: 'block', width: '100%', height: '180px', border: 'none', background: '#000' }}
    />
  </div>
)
