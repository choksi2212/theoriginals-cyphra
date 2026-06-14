# Web Application Integration Guide

## Overview

This guide shows how to integrate CYPHRA libraries into your existing web application using WebAssembly (WASM).

---

## Prerequisites

- Rust toolchain installed
- `wasm-pack` installed: `cargo install wasm-pack`
- Your existing web application (React, Vue, Angular, etc.)

---

## Step 1: Build WASM Module

```bash
# Navigate to the protocol library
cd protocol

# Build for web target
wasm-pack build --target web --out-dir ../wasm-dist

# This creates:
# - wasm-dist/cyphra_protocol_bg.wasm
# - wasm-dist/cyphra_protocol.js
# - wasm-dist/cyphra_protocol.d.ts
```

---

## Step 2: Copy WASM Files to Your Web App

```bash
# Copy to your web app's public directory
cp -r wasm-dist/* /path/to/your-web-app/public/wasm/
```

---

## Step 3: Create TypeScript Wrapper

Create `src/lib/CYPHRA.ts` in your web app:

```typescript
import init, * as CYPHRAPS from '/wasm/cyphra_protocol';

let initialized = false;

export async function initCYPHRAPS() {
  if (!initialized) {
    await init();
    initialized = true;
  }
}

export interface IdentityKeyPair {
  deviceId: Uint8Array;
  kyberPublic: Uint8Array;
  x25519Public: Uint8Array;
}

export interface EncryptedMessage {
  header: Uint8Array;
  ciphertext: Uint8Array;
  authTag: Uint8Array;
}

export class ProtocolClient {
  async generateIdentity(): Promise<IdentityKeyPair> {
    await initCYPHRAPS();
    return CYPHRAPS.generate_identity_keypair();
  }

  async encryptMessage(
    sessionId: string,
    plaintext: Uint8Array
  ): Promise<EncryptedMessage> {
    await initCYPHRAPS();
    return CYPHRAPS.encrypt_message(sessionId, plaintext);
  }

  async decryptMessage(
    sessionId: string,
    encrypted: EncryptedMessage
  ): Promise<Uint8Array> {
    await initCYPHRAPS();
    return CYPHRAPS.decrypt_message(sessionId, encrypted);
  }
}
```

---

## Step 4: Use in Your React Components

```typescript
import { useEffect, useState } from 'react';
import { ProtocolClient } from '@/lib/CYPHRA';

export function ChatComponent() {
  const [client] = useState(() => new ProtocolClient());
  const [identity, setIdentity] = useState(null);

  useEffect(() => {
    async function init() {
      const id = await client.generateIdentity();
      setIdentity(id);
    }
    init();
  }, []);

  async function sendMessage(text: string) {
    const plaintext = new TextEncoder().encode(text);
    const encrypted = await client.encryptMessage('session-1', plaintext);
    
    // Send encrypted message to backend
    await fetch('/api/messages', {
      method: 'POST',
      body: JSON.stringify({
        header: Array.from(encrypted.header),
        ciphertext: Array.from(encrypted.ciphertext),
        authTag: Array.from(encrypted.authTag),
      }),
    });
  }

  return (
    <div>
      <h1>Secure Chat</h1>
      {identity && <p>Device ID: {identity.deviceId}</p>}
      <button onClick={() => sendMessage('Hello!')}>Send</button>
    </div>
  );
}
```

---

## Step 5: Add WASM MIME Type (if needed)

If using Vite, add to `vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    headers: {
      'Cross-Origin-Embedder-Policy': 'require-corp',
      'Cross-Origin-Opener-Policy': 'same-origin',
    },
  },
});
```

---

## API Reference

### Protocol Functions

```typescript
// Generate identity keypair
generate_identity_keypair(): IdentityKeyPair

// Generate signed prekey
generate_signed_prekey(identity: IdentityKeyPair): SignedPreKey

// Initiate session
initiate_session(bundle: PreKeyBundle, identity: IdentityKeyPair): Session

// Encrypt message
encrypt_message(sessionId: string, plaintext: Uint8Array): EncryptedMessage

// Decrypt message
decrypt_message(sessionId: string, encrypted: EncryptedMessage): Uint8Array
```

### AI/Threat Detection Functions

```typescript
// Compute threat score
compute_threat_score(flowFeatures: FlowFeatures): number

// Adjust security policy
adjust_policy_by_threat(policy: SecurityPolicy, threatScore: number): void
```

---

## Performance Optimization

### 1. Lazy Load WASM

```typescript
const CYPHRAPS = lazy(() => import('@/lib/CYPHRA'));
```

### 2. Use Web Workers

```typescript
// worker.ts
import { ProtocolClient } from '@/lib/CYPHRA';

const client = new ProtocolClient();

self.onmessage = async (e) => {
  const { type, data } = e.data;
  
  if (type === 'encrypt') {
    const encrypted = await client.encryptMessage(data.sessionId, data.plaintext);
    self.postMessage({ type: 'encrypted', data: encrypted });
  }
};
```

### 3. Cache WASM Module

```typescript
const wasmCache = new Map();

export async function initCYPHRAPS() {
  if (!wasmCache.has('module')) {
    const module = await init();
    wasmCache.set('module', module);
  }
  return wasmCache.get('module');
}
```

---

## Troubleshooting

### Issue: WASM file not loading

**Solution**: Check MIME type configuration in your server

### Issue: Memory errors

**Solution**: Increase WASM memory limit:
```typescript
await init({ memory: new WebAssembly.Memory({ initial: 256, maximum: 512 }) });
```

### Issue: Slow initialization

**Solution**: Preload WASM module:
```html
<link rel="preload" href="/wasm/cyphra_protocol_bg.wasm" as="fetch" crossorigin>
```

---

## Example: Complete Integration

See `examples/web-chat-app/` for a complete working example.
