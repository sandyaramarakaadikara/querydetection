const BASE_URL = '/api'

export async function analyzeQuery(query) {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Analysis failed')
  }
  return response.json()
}

export async function getSamples() {
  const response = await fetch(`${BASE_URL}/samples`)
  if (!response.ok) throw new Error('Failed to fetch samples')
  return response.json()
}
