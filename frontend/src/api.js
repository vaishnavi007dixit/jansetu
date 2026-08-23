// Central place all backend calls go through.
// Swap mock -> real backend by setting VITE_API_BASE_URL (see .env.example).
// Until that's set, every function below serves mock data so the UI is
// buildable/demoable without the real pipeline running.

import mockHotspots from './mock/hotspots.mock.json'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const USE_MOCKS = !BASE_URL

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// --- POST /api/requests -----------------------------------------------

export async function submitRequest(payload) {
  if (USE_MOCKS) {
    await sleep(400)
    return { request_id: 'mock_' + Date.now(), status: 'processing' }
  }

  const res = await fetch(`${BASE_URL}/api/requests`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }))
    throw new Error(err.message || 'Failed to submit report')
  }
  return res.json()
}

// --- GET /api/requests/{id} --------------------------------------------

const MOCK_CATEGORIES = ['water', 'road', 'electricity', 'sanitation']

export async function getRequestStatus(requestId) {
  if (USE_MOCKS) {
    await sleep(600)
    // Pretend it finishes processing after ~2 polls.
    const done = Math.random() > 0.4
    if (!done) return { request_id: requestId, status: 'processing' }
    return {
      request_id: requestId,
      status: 'done',
      category: MOCK_CATEGORIES[Math.floor(Math.random() * MOCK_CATEGORIES.length)],
      translated_text: 'There has been no water supply in our area for five days',
      language_detected: 'hi',
      district: 'North West Delhi',
      confirmation_audio_url: null,
    }
  }

  const res = await fetch(`${BASE_URL}/api/requests/${requestId}`)
  if (!res.ok) throw new Error('Failed to fetch request status')
  return res.json()
}

// Poll until status is "done" or "failed", or timeout (~20s per contract).
export async function pollRequestUntilDone(requestId, { intervalMs = 2000, timeoutMs = 20000 } = {}) {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    const result = await getRequestStatus(requestId)
    if (result.status === 'done' || result.status === 'failed') return result
    await sleep(intervalMs)
  }
  return { request_id: requestId, status: 'failed', error: 'timeout' }
}

// --- GET /api/hotspots ---------------------------------------------------

export async function getHotspots({ category, district } = {}) {
  if (USE_MOCKS) {
    await sleep(300)
    let hotspots = mockHotspots.hotspots
    if (category) hotspots = hotspots.filter((h) => h.category === category)
    if (district) hotspots = hotspots.filter((h) => h.district === district)
    return { hotspots, generated_at: mockHotspots.generated_at }
  }

  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (district) params.set('district', district)
  const qs = params.toString() ? `?${params.toString()}` : ''

  const res = await fetch(`${BASE_URL}/api/hotspots${qs}`)
  if (!res.ok) throw new Error('Failed to fetch hotspots')
  return res.json()
}

export const usingMocks = USE_MOCKS
