/**
 * CYPHRA Mixnet Relay Node
 * ─────────────────────────────────────────────────────────────
 * Each relay is an independent process that:
 *   1. Receives an encrypted message
 *   2. Decrypts its own layer (AES-256-GCM)
 *   3. Forwards the inner payload to the next hop
 *   4. Knows ONLY the previous hop and next hop — never sender or recipient
 *
 * Usage:
 *   node relay.js 6001    ← starts relay on port 6001
 *   node relay.js 6002    ← starts relay on port 6002
 *   ...up to 6005
 *
 * Each relay has a unique key derived from its port index.
 * The sender wraps messages in onion layers using these same keys.
 */

import http from 'http'
import crypto from 'crypto'

const PORT = parseInt(process.argv[2]) || 6001
const RELAY_INDEX = PORT - 6001 // 0, 1, 2, 3, 4

// Derive relay key (MUST match sender-side derivation in mixnet.service.js)
function deriveRelayKey(index) {
  const seed = Buffer.alloc(32)
  for (let i = 0; i < 32; i++) {
    seed[i] = ((index + 1) * 37 + i * 13) & 0xFF
  }
  return seed
}

const RELAY_KEY = deriveRelayKey(RELAY_INDEX)

// AES-256-GCM decrypt
function decrypt(keyBuf, ciphertextHex, nonceHex) {
  const nonce = Buffer.from(nonceHex, 'hex')
  const ciphertext = Buffer.from(ciphertextHex, 'hex')

  // Last 16 bytes are the auth tag
  const authTag = ciphertext.slice(-16)
  const encrypted = ciphertext.slice(0, -16)

  const decipher = crypto.createDecipheriv('aes-256-gcm', keyBuf, nonce)
  decipher.setAuthTag(authTag)

  const decrypted = Buffer.concat([decipher.update(encrypted), decipher.final()])
  return decrypted.toString('utf-8')
}

// Stats
let messagesRelayed = 0
let lastRelayTime = null

const server = http.createServer((req, res) => {
  // Health check
  if (req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' })
    res.end(JSON.stringify({
      relay: RELAY_INDEX,
      port: PORT,
      messagesRelayed,
      lastRelayTime,
      uptime: process.uptime(),
    }))
    return
  }

  // Only accept POST /relay
  if (req.method !== 'POST') {
    res.writeHead(405)
    res.end('Method not allowed')
    return
  }

  let body = ''
  req.on('data', chunk => { body += chunk })
  req.on('end', async () => {
    try {
      const incoming = JSON.parse(body)

      // Decrypt this relay's layer
      const decryptedJson = decrypt(RELAY_KEY, incoming.ciphertext, incoming.nonce)
      const inner = JSON.parse(decryptedJson)

      // inner = { nextHop: "http://...", payload: {...} } OR { nextHop, ciphertext, nonce }
      const nextHop = inner.nextHop
      const forwardPayload = inner.payload
        ? JSON.stringify(inner.payload)
        : JSON.stringify({ ciphertext: inner.ciphertext, nonce: inner.nonce })

      // Forward to next hop
      const nextUrl = new URL(nextHop.startsWith('http') ? nextHop : `http://${nextHop}`)

      const fwdReq = http.request({
        hostname: nextUrl.hostname,
        port: nextUrl.port,
        path: nextUrl.pathname,
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(forwardPayload) },
      }, (fwdRes) => {
        // Relay doesn't care about downstream response
        fwdRes.resume()
      })

      fwdReq.on('error', (e) => {
        console.error(`[Relay ${RELAY_INDEX}] Forward failed: ${e.message}`)
      })

      fwdReq.write(forwardPayload)
      fwdReq.end()

      messagesRelayed++
      lastRelayTime = new Date().toISOString()

      res.writeHead(200, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ status: 'relayed', relay: RELAY_INDEX }))

    } catch (e) {
      console.error(`[Relay ${RELAY_INDEX}] Error: ${e.message}`)
      res.writeHead(500)
      res.end(JSON.stringify({ error: e.message }))
    }
  })
})

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[CYPHRA Mixnet] Relay ${RELAY_INDEX} active on port ${PORT} (key: ${RELAY_KEY.toString('hex').slice(0, 8)}...)`)
})
