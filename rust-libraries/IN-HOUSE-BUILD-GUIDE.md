# CYPHRA: Complete In-House Build Guide
**AI-Powered Military-Grade Secure Messaging System**  
**Build Everything From Scratch (Except Audited Crypto Primitives)**

---

## Table of Contents
1. [Overview: What We Build In-House](#overview)
2. [Architecture: Full System Breakdown](#architecture)
3. [Component 1: Post-Quantum Hybrid Protocol](#component-1-pq-hybrid-protocol)
4. [Component 2: Metadata Defense Layer](#component-2-metadata-defense)
5. [Component 3: Self-Destruct & Forensic Denial](#component-3-self-destruct)
6. [Component 4: AI Threat Detection & Adaptive Policy](#component-4-ai-threat-detection)
7. [Component 5: Zero-Trust Backend Infrastructure](#component-5-backend)
8. [Component 6: Client Applications](#component-6-clients)
9. [Component 7: Mixnet & Routing](#component-7-mixnet)
10. [Development Roadmap & Team Structure](#roadmap)
11. [Testing, Security & Compliance](#testing)
12. [Dependencies: What We DON'T Build](#dependencies)

---

## 1. Overview: What We Build In-House {#overview}

### 🏗️ Full In-House Components (100% Custom)
- **Protocol Layer**: PQC-hybrid X3DH + Double Ratchet variant
- **Metadata Defense**: Traffic shaper, padding engine, timing obfuscator
- **Self-Destruct**: Crypto-erase, secure wipe, destruction receipts
- **AI Threat Scoring**: Anomaly detector, adaptive policy engine
- **Mixnet Relays**: Onion routing, mix cascade, store-and-forward
- **Backend**: Mailbox server, key distribution, HSM integration
- **Clients**: Mobile (React Native/Flutter), Desktop (Electron/Tauri)
- **Policy Engine**: Rule engine, threat response automation
- **Storage Layer**: Encrypted blobs, secure deletion, key management

### 🔒 Dependencies: Audited Crypto Only
- **Primitives**: NIST PQC (Kyber, Dilithium), AES-GCM, ChaCha20-Poly1305, X25519, Ed25519
- **Libraries**: liboqs, libsodium, OpenSSL 3.x (oqs-provider)
- **Reason**: These are NIST-standardized, formally verified, constant-time hardened, and FIPS-certifiable

---

## 2. Architecture: Full System Breakdown {#architecture}

```
┌─────────────────────────────────────────────────────────────────┐
│                    CYPHRA SYSTEM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CLIENT LAYER (In-House)                                 │  │
│  │  ├─ Mobile Apps (React Native / Flutter)                 │  │
│  │  │  ├─ UI/UX (Mission presets, chat, groups)             │  │
│  │  │  ├─ Protocol Engine (PQC-Hybrid Ratchet)              │  │
│  │  │  ├─ Metadata Shield (Traffic shaper, AI detector)     │  │
│  │  │  ├─ Self-Destruct Engine (Crypto-erase, secure wipe)  │  │
│  │  │  ├─ Secure Storage (Encrypted DB, key management)     │  │
│  │  │  └─ P2P Mesh (BLE, Wi-Fi Direct, onion routing)       │  │
│  │  │                                                         │  │
│  │  └─ Desktop Apps (Electron / Tauri)                       │  │
│  │     └─ (Same components as mobile + eBPF traffic tap)     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ▲                                   │
│                             │ QUIC/HTTP3/WebRTC                 │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  NETWORK LAYER (In-House)                                │  │
│  │  ├─ Mixnet Relays (Onion routing, Sphinx packets)        │  │
│  │  ├─ Traffic Obfuscation (Padding, timing morphing)       │  │
│  │  └─ Transport (QUIC/HTTP3, DTLS, WebRTC DataChannels)    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ▲                                   │
│                             │                                   │
│                             ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  BACKEND LAYER (In-House)                                │  │
│  │  ├─ Mailbox Server (Store-and-forward, blind tokens)     │  │
│  │  ├─ Key Distribution (PQC prekeys, device registration)   │  │
│  │  ├─ HSM Integration (Root keys, signing, attestation)     │  │
│  │  ├─ Policy Store (Group configs, ACLs, revocation)        │  │
│  │  └─ Telemetry Firewall (Federated learning aggregator)    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AI/ML LAYER (In-House)                                  │  │
│  │  ├─ Anomaly Detector (On-device GBDT ensemble)           │  │
│  │  ├─ Threat Scoring Engine (Real-time risk assessment)    │  │
│  │  ├─ Adaptive Policy Engine (Rule engine + bandits)       │  │
│  │  └─ Federated Learning (Secure aggregation, model sync)  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CRYPTO LAYER (Audited Dependencies Only)                │  │
│  │  ├─ PQC Primitives (Kyber, Dilithium via liboqs)         │  │
│  │  ├─ AEAD (AES-GCM, ChaCha20-Poly1305 via libsodium)      │  │
│  │  ├─ ECC (X25519, Ed25519 via libsodium)                  │  │
│  │  └─ KDF/Hash (HKDF, BLAKE3, SHA3)                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Component 1: Post-Quantum Hybrid Protocol {#component-1-pq-hybrid-protocol}

### What We Build
Custom protocol combining PQC + classical cryptography for forward secrecy and quantum resistance.

### 3.1 PQC-Hybrid X3DH (Extended Triple Diffie-Hellman)
**Purpose**: Initial key agreement between devices  
**Build In-House**:
- Protocol state machine (prekey generation, upload, fetch, agreement)
- Hybrid key derivation (Kyber KEM ⊕ X25519 ECDH)
- Signature verification (Dilithium ⊕ Ed25519)
- Prekey rotation and expiration logic
- Device identity management

**File Structure**:
```
src/protocol/
├── x3dh.rs (or .ts/.cpp)
│   ├── generate_identity_keypair()
│   ├── generate_signed_prekey()
│   ├── generate_one_time_prekeys()
│   ├── bundle_upload_request()
│   ├── fetch_bundle()
│   ├── initiate_session()
│   └── accept_session()
├── hybrid_kem.rs
│   ├── kyber_encaps() + x25519_dh()
│   ├── kyber_decaps() + x25519_dh()
│   └── combine_shared_secrets()
└── prekey_store.rs
    ├── rotate_signed_prekey()
    ├── replenish_one_time_prekeys()
    └── cleanup_expired_prekeys()
```

**Implementation Steps**:
1. Generate identity keypair (Kyber1024 + X25519 hybrid)
2. Generate signed prekey (signed with Dilithium3 + Ed25519)
3. Generate 100 one-time prekeys (Kyber768 + X25519)
4. Implement bundle fetch and parse logic
5. Implement initiate_session (encapsulate to recipient keys)
6. Implement accept_session (decapsulate and derive root key)
7. Derive root key and chain keys using HKDF-BLAKE3

**Crypto Interface** (use dependencies):
```rust
// Example interface
use oqs::kem::{Kyber1024, Kyber768};
use libsodium_sys::{crypto_kx_*, crypto_sign_*};

fn hybrid_encapsulate(kyber_pk: &[u8], x25519_pk: &[u8]) -> (Vec<u8>, Vec<u8>) {
    let (kyber_ct, kyber_ss) = kyber_encaps(kyber_pk);
    let x25519_ss = x25519_dh(x25519_pk);
    let combined_ss = xor_and_hash(kyber_ss, x25519_ss);
    (kyber_ct, combined_ss)
}
```

### 3.2 PQC-Hybrid Double Ratchet
**Purpose**: Per-message forward secrecy and post-compromise security  
**Build In-House**:
- Ratchet state machine (DH ratchet, symmetric ratchet)
- Message encryption/decryption
- Out-of-order message handling
- Header encryption
- Ratchet advancement logic

**File Structure**:
```
src/protocol/
├── double_ratchet.rs
│   ├── Session {
│   │   root_key: [u8; 32],
│   │   send_chain_key: [u8; 32],
│   │   recv_chain_key: [u8; 32],
│   │   send_counter: u32,
│   │   recv_counter: u32,
│   │   dh_self: (Kyber, X25519),
│   │   dh_remote: (Kyber_pk, X25519_pk),
│   │   skipped_keys: HashMap<(u32, u32), [u8; 32]>,
│   │ }
│   ├── ratchet_encrypt()
│   ├── ratchet_decrypt()
│   ├── dh_ratchet_step()
│   └── symmetric_ratchet_step()
├── message.rs
│   ├── Message { header, ciphertext, auth_tag }
│   ├── encrypt_message()
│   ├── decrypt_message()
│   └── verify_authenticity()
└── header_encryption.rs
    ├── encrypt_header()
    └── decrypt_header()
```

**Implementation Steps**:
1. Initialize session with root key from X3DH
2. Implement DH ratchet (hybrid Kyber+X25519 ratchet step)
3. Implement symmetric ratchet (KDF chain advancement)
4. Implement message key derivation (HKDF from chain key)
5. Encrypt message with AES-256-GCM or ChaCha20-Poly1305
6. Handle out-of-order messages (store skipped keys)
7. Implement header encryption for metadata hiding
8. Automatic ratchet on threat score increase

**Message Format** (custom):
```
┌────────────────────────────────────────────┐
│ Header (encrypted)                         │
│  ├─ Ratchet public key (Kyber+X25519)      │
│  ├─ Previous chain length                  │
│  ├─ Message number                         │
│  └─ Timestamp (obfuscated)                 │
├────────────────────────────────────────────┤
│ Ciphertext (AES-256-GCM)                   │
│  └─ Plaintext message                      │
├────────────────────────────────────────────┤
│ Authentication Tag (Poly1305/GMAC)         │
└────────────────────────────────────────────┘
```

### 3.3 Group Messaging (MLS-inspired)
**Purpose**: Efficient group key agreement with PQC  
**Build In-House**:
- TreeKEM-style group state
- Add/remove member operations
- Epoch advancement
- Commit message handling

**File Structure**:
```
src/protocol/
├── group.rs
│   ├── GroupState {
│   │   epoch: u64,
│   │   tree: RatchetTree,
│   │   group_key: [u8; 32],
│   │   members: Vec<MemberInfo>,
│   │ }
│   ├── add_member()
│   ├── remove_member()
│   ├── update_epoch()
│   └── encrypt_group_message()
└── ratchet_tree.rs
    ├── update_path()
    ├── derive_path_secrets()
    └── commit_changes()
```

**Implementation Steps**:
1. Initialize group with founder's identity
2. Build TreeKEM structure with hybrid keys
3. Implement add member (derive new path secrets)
4. Implement remove member (update all affected paths)
5. Implement commit message (sign and broadcast changes)
6. Implement group message encryption (AEAD with epoch key)

---

## 4. Component 2: Metadata Defense Layer {#component-2-metadata-defense}

### What We Build
Traffic analysis defense using ML-driven adaptive obfuscation.

### 4.1 On-Device Anomaly Detector
**Purpose**: Detect metadata leaks and suspicious patterns in real-time  
**Build In-House**:
- Feature extraction from network flows
- GBDT inference engine (no external runtime)
- Threat scoring system
- Model update mechanism

**File Structure**:
```
src/ai/
├── anomaly_detector.rs
│   ├── FlowFeatures {
│   │   packet_sizes: Vec<u16>,
│   │   inter_arrival_times: Vec<u64>,
│   │   direction_pattern: Vec<bool>,
│   │   burst_statistics: BurstStats,
│   │ }
│   ├── extract_features()
│   ├── compute_threat_score()
│   └── update_model()
├── gbdt_engine.rs
│   ├── Tree { splits, leaves, thresholds }
│   ├── Ensemble { trees: Vec<Tree>, weights }
│   ├── predict()
│   └── predict_proba()
└── feature_engineering.rs
    ├── compute_statistical_features()
    ├── compute_burst_features()
    └── compute_ratio_features()
```

**Implementation Steps**:
1. **Feature Extraction** (from your trained models):
   - Use ISCXVPN2016/UNSW-NB15/CICIDS2017 datasets
   - Extract 200+ features (packet sizes, timing, bursts, ratios)
   - Implement in C++/Rust for speed (<1ms per flow)

2. **GBDT Inference Engine** (custom):
   ```rust
   struct Tree {
       nodes: Vec<Node>,
       leaves: Vec<f32>,
   }
   
   struct Node {
       feature_idx: usize,
       threshold: f32,
       left_child: usize,
       right_child: usize,
   }
   
   fn predict_tree(tree: &Tree, features: &[f32]) -> f32 {
       let mut node_idx = 0;
       loop {
           let node = &tree.nodes[node_idx];
           if node.is_leaf() {
               return tree.leaves[node_idx];
           }
           if features[node.feature_idx] <= node.threshold {
               node_idx = node.left_child;
           } else {
               node_idx = node.right_child;
           }
       }
   }
   
   fn predict_ensemble(ensemble: &Ensemble, features: &[f32]) -> f32 {
       ensemble.trees.iter()
           .zip(&ensemble.weights)
           .map(|(tree, weight)| weight * predict_tree(tree, features))
           .sum()
   }
   ```

3. **Model Export**:
   - Export trained LightGBM/XGBoost to JSON
   - Parse JSON and build in-memory tree structures
   - No external dependencies at runtime

4. **Threat Scoring**:
   ```rust
   fn compute_threat_score(flow_features: &FlowFeatures) -> ThreatScore {
       let anomaly_score = ensemble.predict(&flow_features.to_vec());
       let behavioral_score = analyze_pattern(&flow_features);
       let metadata_risk = detect_metadata_leak(&flow_features);
       
       ThreatScore {
           overall: (anomaly_score + behavioral_score + metadata_risk) / 3.0,
           confidence: compute_confidence(&flow_features),
           timestamp: SystemTime::now(),
       }
   }
   ```

### 4.2 Traffic Shaper & Padding Engine
**Purpose**: Morph traffic patterns to evade analysis  
**Build In-House**:
- Adaptive padding scheduler
- Timing obfuscation
- Packet size morphing
- Cover traffic generator

**File Structure**:
```
src/network/
├── traffic_shaper.rs
│   ├── PaddingPolicy {
│   │   rate: f32,
│   │   max_overhead: f32,
│   │   timing_jitter: Duration,
│   │ }
│   ├── apply_padding()
│   ├── morph_packet_size()
│   └── inject_cover_traffic()
├── timing_obfuscator.rs
│   ├── add_jitter()
│   ├── burst_shaping()
│   └── delay_scheduling()
└── adaptive_shaper.rs
    ├── adjust_policy_by_threat()
    └── measure_overhead()
```

**Implementation Steps**:
1. **WTF-PAD Style Padding**:
   ```rust
   fn apply_adaptive_padding(
       packet: &mut Packet,
       threat_score: f32,
       policy: &mut PaddingPolicy
   ) {
       // Increase padding rate with threat score
       policy.rate = (threat_score * 0.5).min(0.8);
       
       // Add padding bytes
       let padding_size = sample_padding_distribution(policy.rate);
       packet.append_padding(padding_size);
       
       // Add timing jitter
       let jitter = Duration::from_micros(
           (rand::random::<f32>() * policy.timing_jitter.as_micros() as f32) as u64
       );
       thread::sleep(jitter);
   }
   ```

2. **Packet Size Morphing**:
   ```rust
   fn morph_packet_size(packet: &mut Packet, target_size: usize) {
       if packet.len() < target_size {
           packet.append_padding(target_size - packet.len());
       } else if packet.len() > target_size {
           // Fragment if needed
           packet.fragment(target_size);
       }
   }
   ```

3. **Cover Traffic**:
   ```rust
   async fn inject_cover_traffic(policy: &PaddingPolicy) {
       loop {
           let interval = sample_exponential(policy.cover_rate);
           tokio::time::sleep(interval).await;
           
           let dummy_packet = generate_dummy_packet();
           send_packet(dummy_packet).await;
       }
   }
   ```

4. **Adaptive Policy**:
   ```rust
   fn adapt_padding_policy(
       policy: &mut PaddingPolicy,
       threat_score: f32,
       bandwidth_budget: f32
   ) {
       if threat_score > 0.7 {
           policy.rate = (policy.rate * 1.5).min(0.9);
           policy.timing_jitter *= 2;
       } else if threat_score < 0.3 && policy.rate > 0.1 {
           policy.rate *= 0.8; // Reduce overhead
       }
   }
   ```

### 4.3 Flow Feature Tap
**Purpose**: Extract network flow statistics for ML  
**Build In-House**:
- Packet capture interface
- Flow assembly
- Feature computation
- Privacy-preserving aggregation

**File Structure**:
```
src/network/
├── flow_tap.rs (Linux/eBPF or userspace)
│   ├── capture_packets()
│   ├── assemble_flows()
│   └── compute_features()
├── feature_extractor.rs
│   ├── extract_packet_sizes()
│   ├── extract_timing()
│   └── extract_burst_stats()
└── privacy_filter.rs
    ├── redact_sensitive_info()
    └── anonymize_endpoints()
```

**Implementation** (eBPF for Linux):
```c
// flow_tap.bpf.c
SEC("xdp")
int flow_monitor(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    
    struct ethhdr *eth = data;
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;
    
    if (eth->h_proto != htons(ETH_P_IP))
        return XDP_PASS;
    
    struct iphdr *ip = (void *)(eth + 1);
    if ((void *)(ip + 1) > data_end)
        return XDP_PASS;
    
    // Extract flow 5-tuple and stats
    struct flow_key key = {
        .src_ip = ip->saddr,
        .dst_ip = ip->daddr,
        .proto = ip->protocol,
    };
    
    struct flow_stats *stats = bpf_map_lookup_elem(&flow_map, &key);
    if (stats) {
        stats->packet_count++;
        stats->byte_count += ntohs(ip->tot_len);
        stats->last_seen = bpf_ktime_get_ns();
    }
    
    return XDP_PASS;
}
```

---

## 5. Component 3: Self-Destruct & Forensic Denial {#component-3-self-destruct}

### What We Build
Crypto-erase, secure deletion, and verifiable destruction receipts.

### 5.1 Crypto-Erase Engine
**Purpose**: Instant message unreadability by deleting keys  
**Build In-House**:
- Per-message key hierarchy (DEK wrapped by KEK)
- Time-based and receipt-based key expiration
- Key evaporation scheduler
- Memory zeroization

**File Structure**:
```
src/storage/
├── crypto_erase.rs
│   ├── MessageEnvelope {
│   │   dek_wrapped: Vec<u8>, // DEK encrypted by KEK
│   │   ciphertext: Vec<u8>,
│   │   ttl: Duration,
│   │   destroy_on_read: bool,
│   │ }
│   ├── wrap_message()
│   ├── unwrap_message()
│   ├── schedule_destruction()
│   └── evaporate_key()
├── key_hierarchy.rs
│   ├── derive_kek()
│   ├── wrap_dek()
│   ├── unwrap_dek()
│   └── destroy_kek()
└── memory_sanitization.rs
    ├── zeroize_buffer()
    ├── zeroize_stack()
    └── secure_free()
```

**Implementation Steps**:
1. **Key Hierarchy**:
   ```rust
   // Master key (from device keystore)
   let master_key = device_keystore.get_master_key();
   
   // Derive KEK per conversation
   let kek = hkdf_derive(master_key, b"KEK", conversation_id);
   
   // Generate DEK per message
   let dek = random_bytes(32);
   
   // Encrypt message
   let ciphertext = aes_gcm_encrypt(dek, plaintext);
   
   // Wrap DEK with KEK
   let dek_wrapped = aes_gcm_encrypt(kek, dek);
   
   // Store envelope
   let envelope = MessageEnvelope {
       dek_wrapped,
       ciphertext,
       ttl: Duration::from_secs(3600),
       destroy_on_read: true,
   };
   ```

2. **Destruction Scheduler**:
   ```rust
   async fn schedule_destruction(
       msg_id: MessageId,
       ttl: Duration,
       destroy_on_read: bool
   ) {
       // Time-based destruction
       tokio::spawn(async move {
           tokio::time::sleep(ttl).await;
           evaporate_key(msg_id).await;
       });
       
       // Receipt-based destruction
       if destroy_on_read {
           wait_for_read_receipt(msg_id).await;
           evaporate_key(msg_id).await;
       }
   }
   ```

3. **Key Evaporation**:
   ```rust
   fn evaporate_key(msg_id: MessageId) -> Result<()> {
       // Delete KEK from memory
       let kek = kek_cache.remove(&msg_id)?;
       zeroize_buffer(&mut kek);
       
       // Delete wrapped DEK from storage
       storage.delete_message_envelope(msg_id)?;
       
       // Generate destruction receipt
       let receipt = generate_destruction_receipt(msg_id);
       log_receipt(receipt);
       
       Ok(())
   }
   ```

4. **Memory Zeroization**:
   ```rust
   fn zeroize_buffer(buffer: &mut [u8]) {
       // Use volatile write to prevent optimization
       for byte in buffer.iter_mut() {
           unsafe {
               std::ptr::write_volatile(byte, 0);
           }
       }
       std::sync::atomic::compiler_fence(Ordering::SeqCst);
   }
   ```

### 5.2 Secure Storage Layer
**Purpose**: Encrypted on-disk storage with secure deletion  
**Build In-House**:
- SQLite with custom encryption (SQLCipher-style)
- File-level encryption
- Secure deletion (crypto-erase + overwrite)
- Keystore integration

**File Structure**:
```
src/storage/
├── encrypted_db.rs
│   ├── open_encrypted_db()
│   ├── encrypt_page()
│   ├── decrypt_page()
│   └── rekey_database()
├── secure_file.rs
│   ├── write_encrypted_file()
│   ├── read_encrypted_file()
│   └── secure_delete_file()
└── keystore_integration.rs
    ├── AndroidKeystore (JNI)
    ├── iOSSecureEnclave (Swift)
    └── TPM2Integration (Linux)
```

**Implementation Steps**:
1. **Page-Level Encryption**:
   ```rust
   struct EncryptedPage {
       page_num: u32,
       nonce: [u8; 12],
       ciphertext: Vec<u8>,
       tag: [u8; 16],
   }
   
   fn encrypt_page(plaintext: &[u8], page_key: &[u8; 32]) -> EncryptedPage {
       let nonce = random_bytes(12);
       let (ciphertext, tag) = aes_gcm_encrypt(page_key, &nonce, plaintext);
       
       EncryptedPage {
           page_num: 0,
           nonce: nonce.try_into().unwrap(),
           ciphertext,
           tag: tag.try_into().unwrap(),
       }
   }
   ```

2. **Secure Deletion**:
   ```rust
   fn secure_delete_file(path: &Path) -> Result<()> {
       // Method 1: Crypto-erase (instant)
       crypto_erase_file_key(path)?;
       
       // Method 2: Overwrite (for compliance)
       let file = OpenOptions::new().write(true).open(path)?;
       let file_size = file.metadata()?.len();
       
       // DoD 5220.22-M style (3 passes)
       for pass in 0..3 {
           file.seek(SeekFrom::Start(0))?;
           let pattern = match pass {
               0 => vec![0x00; file_size as usize],
               1 => vec![0xFF; file_size as usize],
               2 => random_bytes(file_size as usize),
               _ => unreachable!(),
           };
           file.write_all(&pattern)?;
           file.sync_all()?;
       }
       
       // Delete file
       fs::remove_file(path)?;
       
       // TRIM/punch hole (SSD optimization)
       #[cfg(target_os = "linux")]
       punch_hole(path)?;
       
       Ok(())
   }
   ```

3. **Keystore Integration** (Android):
   ```kotlin
   // AndroidKeystore.kt
   object SecureKeystore {
       fun generateKey(alias: String): SecretKey {
           val keyGenerator = KeyGenerator.getInstance(
               KeyProperties.KEY_ALGORITHM_AES,
               "AndroidKeyStore"
           )
           
           val keyGenParameterSpec = KeyGenParameterSpec.Builder(
               alias,
               KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
           )
               .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
               .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
               .setUserAuthenticationRequired(false)
               .setKeySize(256)
               .build()
           
           keyGenerator.init(keyGenParameterSpec)
           return keyGenerator.generateKey()
       }
       
       fun encrypt(alias: String, plaintext: ByteArray): ByteArray {
           val keyStore = KeyStore.getInstance("AndroidKeyStore")
           keyStore.load(null)
           
           val secretKey = keyStore.getKey(alias, null) as SecretKey
           val cipher = Cipher.getInstance("AES/GCM/NoPadding")
           cipher.init(Cipher.ENCRYPT_MODE, secretKey)
           
           val iv = cipher.iv
           val ciphertext = cipher.doFinal(plaintext)
           
           return iv + ciphertext
       }
   }
   ```

### 5.3 Destruction Receipt System
**Purpose**: Verifiable proof of message destruction  
**Build In-House**:
- Signed destruction receipts
- Append-only transparency log
- Audit verification

**File Structure**:
```
src/audit/
├── destruction_receipt.rs
│   ├── Receipt {
│   │   msg_id: MessageId,
│   │   timestamp: SystemTime,
│   │   reason: DestructionReason,
│   │   signature: Vec<u8>,
│   │ }
│   ├── generate_receipt()
│   ├── sign_receipt()
│   └── verify_receipt()
└── transparency_log.rs
    ├── append_receipt()
    ├── verify_log_consistency()
    └── audit_log()
```

**Implementation**:
```rust
fn generate_destruction_receipt(
    msg_id: MessageId,
    reason: DestructionReason,
    signing_key: &SigningKey
) -> Receipt {
    let receipt = Receipt {
        msg_id,
        timestamp: SystemTime::now(),
        reason,
        signature: vec![],
    };
    
    let message = receipt.to_canonical_bytes();
    let signature = signing_key.sign(&message);
    
    Receipt {
        signature: signature.to_vec(),
        ..receipt
    }
}

fn append_to_transparency_log(receipt: &Receipt) -> Result<()> {
    let log_entry = LogEntry {
        receipt: receipt.clone(),
        prev_hash: get_latest_hash()?,
    };
    
    let entry_hash = hash_log_entry(&log_entry);
    
    storage.append_log_entry(log_entry)?;
    storage.set_latest_hash(entry_hash)?;
    
    Ok(())
}
```

---

## 6. Component 4: AI Threat Detection & Adaptive Policy {#component-4-ai-threat-detection}

### What We Build
Real-time threat scoring and adaptive security policy engine.

### 6.1 Threat Scoring Engine
**Purpose**: Combine multiple signals into actionable threat score  
**Build In-House**:
- Multi-signal aggregation
- Confidence scoring
- Temporal analysis
- Alert generation

**File Structure**:
```
src/ai/
├── threat_scorer.rs
│   ├── ThreatScore {
│   │   overall: f32,
│   │   confidence: f32,
│   │   breakdown: ScoreBreakdown,
│   │   timestamp: SystemTime,
│   │ }
│   ├── ScoreBreakdown {
│   │   network_anomaly: f32,
│   │   behavioral_risk: f32,
│   │   metadata_leak: f32,
│   │   device_compromise: f32,
│   │ }
│   ├── compute_threat_score()
│   └── generate_alerts()
└── temporal_analyzer.rs
    ├── track_score_trends()
    ├── detect_sudden_changes()
    └── predict_future_risk()
```

**Implementation**:
```rust
fn compute_threat_score(signals: &ThreatSignals) -> ThreatScore {
    // Network anomaly (from GBDT)
    let network_score = anomaly_detector.predict(&signals.flow_features);
    
    // Behavioral analysis
    let behavioral_score = analyze_behavior(&signals.user_actions);
    
    // Metadata leak detection
    let metadata_score = detect_metadata_leak(&signals.traffic_pattern);
    
    // Device integrity
    let device_score = check_device_integrity(&signals.device_state);
    
    // Weighted aggregation
    let overall = 
        network_score * 0.3 +
        behavioral_score * 0.25 +
        metadata_score * 0.3 +
        device_score * 0.15;
    
    // Confidence based on signal quality
    let confidence = compute_confidence(signals);
    
    ThreatScore {
        overall,
        confidence,
        breakdown: ScoreBreakdown {
            network_anomaly: network_score,
            behavioral_risk: behavioral_score,
            metadata_leak: metadata_score,
            device_compromise: device_score,
        },
        timestamp: SystemTime::now(),
    }
}
```

### 6.2 Adaptive Policy Engine
**Purpose**: Automatically adjust security posture based on threat  
**Build In-House**:
- Rule engine
- Policy templates (mission presets)
- Automatic policy adjustment
- Manual override support

**File Structure**:
```
src/policy/
├── policy_engine.rs
│   ├── SecurityPolicy {
│   │   ratchet_cadence: Duration,
│   │   padding_rate: f32,
│   │   mix_path_length: usize,
│   │   destroy_on_read: bool,
│   │   allow_p2p: bool,
│   │ }
│   ├── apply_policy()
│   ├── adjust_by_threat()
│   └── apply_mission_preset()
├── mission_presets.rs
│   ├── SilentPatrol
│   ├── HotExtraction
│   ├── SecureBase
│   └── CompromisedNetwork
└── rule_engine.rs
    ├── Rule { condition, action }
    ├── evaluate_rules()
    └── execute_actions()
```

**Implementation**:
```rust
fn adjust_policy_by_threat(
    current_policy: &mut SecurityPolicy,
    threat_score: f32
) {
    if threat_score > 0.8 {
        // CRITICAL: Maximum protection
        current_policy.ratchet_cadence = Duration::from_secs(60);
        current_policy.padding_rate = 0.9;
        current_policy.mix_path_length = 5;
        current_policy.destroy_on_read = true;
        current_policy.allow_p2p = false;
    } else if threat_score > 0.6 {
        // HIGH: Increased protection
        current_policy.ratchet_cadence = Duration::from_secs(300);
        current_policy.padding_rate = 0.6;
        current_policy.mix_path_length = 3;
    } else if threat_score > 0.4 {
        // MEDIUM: Balanced
        current_policy.ratchet_cadence = Duration::from_secs(3600);
        current_policy.padding_rate = 0.3;
        current_policy.mix_path_length = 2;
    } else {
        // LOW: Minimal overhead
        current_policy.ratchet_cadence = Duration::from_secs(7200);
        current_policy.padding_rate = 0.1;
        current_policy.mix_path_length = 1;
    }
}

// Mission Presets
fn apply_silent_patrol_preset() -> SecurityPolicy {
    SecurityPolicy {
        ratchet_cadence: Duration::from_secs(1800),
        padding_rate: 0.8, // High obfuscation
        mix_path_length: 4,
        destroy_on_read: true,
        allow_p2p: true, // Use mesh when available
        voice_codec: VoiceCodec::Opus { bitrate: 8000 }, // Low bandwidth
    }
}

fn apply_hot_extraction_preset() -> SecurityPolicy {
    SecurityPolicy {
        ratchet_cadence: Duration::from_secs(60),
        padding_rate: 0.95, // Maximum obfuscation
        mix_path_length: 5,
        destroy_on_read: true,
        allow_p2p: false, // Only trusted relays
        voice_codec: VoiceCodec::Opus { bitrate: 6000 },
    }
}
```

### 6.3 Contextual Bandits (Online Learning)
**Purpose**: Optimize padding/route trade-offs in real-time  
**Build In-House**:
- LinUCB or Thompson Sampling
- Reward signal (overhead vs. safety)
- Exploration vs. exploitation

**File Structure**:
```
src/ai/
├── bandit.rs
│   ├── LinUCB {
│   │   arms: Vec<Arm>,
│   │   alpha: f32,
│   │ }
│   ├── select_arm()
│   ├── update_reward()
│   └── compute_confidence()
└── optimization.rs
    ├── compute_reward()
    ├── measure_overhead()
    └── measure_safety()
```

**Implementation**:
```rust
struct LinUCB {
    arms: Vec<Arm>, // Different padding/route configs
    alpha: f32,     // Exploration parameter
}

struct Arm {
    features: Vec<f32>,
    A: Matrix, // Context covariance
    b: Vector, // Reward sum
}

impl LinUCB {
    fn select_arm(&self, context: &[f32]) -> usize {
        let mut best_arm = 0;
        let mut best_ucb = f32::NEG_INFINITY;
        
        for (i, arm) in self.arms.iter().enumerate() {
            let theta = arm.A.inv() * arm.b;
            let mean_reward = theta.dot(context);
            let confidence = self.alpha * (
                context.dot(&arm.A.inv()) * context
            ).sqrt();
            
            let ucb = mean_reward + confidence;
            
            if ucb > best_ucb {
                best_ucb = ucb;
                best_arm = i;
            }
        }
        
        best_arm
    }
    
    fn update_reward(&mut self, arm_idx: usize, context: &[f32], reward: f32) {
        let arm = &mut self.arms[arm_idx];
        arm.A += context.outer_product(context);
        arm.b += reward * context;
    }
}

fn compute_reward(
    overhead: f32,    // Bandwidth/latency penalty
    safety: f32,      // Protection effectiveness
    detected: bool    // Was traffic analyzed?
) -> f32 {
    if detected {
        -100.0 // Heavy penalty for detection
    } else {
        safety * 10.0 - overhead * 1.0 // Balance safety and efficiency
    }
}
```

---

## 7. Component 5: Zero-Trust Backend Infrastructure {#component-5-backend}

### What We Build
Minimal-knowledge backend for store-and-forward and key distribution.

### 7.1 Mailbox Server
**Purpose**: Store encrypted messages for offline recipients  
**Build In-House**:
- Blind token authentication
- Message storage (encrypted blobs)
- Push notification integration
- Rate limiting and abuse prevention

**File Structure**:
```
backend/mailbox/
├── server.rs
│   ├── handle_upload()
│   ├── handle_download()
│   └── handle_delete()
├── authentication.rs
│   ├── BlindToken (RSA blind signature)
│   ├── verify_token()
│   └── issue_token()
├── storage.rs
│   ├── store_message()
│   ├── retrieve_message()
│   └── delete_message()
└── rate_limiter.rs
    ├── check_rate_limit()
    └── update_counters()
```

**Implementation**:
```rust
// Message upload (server never sees plaintext)
async fn handle_upload(req: UploadRequest) -> Result<UploadResponse> {
    // Verify blind token
    verify_blind_token(&req.token)?;
    
    // Store encrypted blob (no inspection)
    let msg_id = generate_message_id();
    storage.store_encrypted_blob(msg_id, &req.ciphertext).await?;
    
    // Set expiration (automatic deletion)
    scheduler.schedule_deletion(msg_id, Duration::from_secs(86400)).await;
    
    // Send push notification (only device ID, no content)
    if let Some(push_token) = req.recipient_push_token {
        push_service.send_notification(push_token, "New message").await?;
    }
    
    Ok(UploadResponse { msg_id })
}

// Blind token authentication
fn verify_blind_token(token: &BlindToken) -> Result<()> {
    // Verify RSA blind signature
    let public_key = get_server_public_key();
    let message = token.message.clone();
    let signature = token.signature.clone();
    
    if !rsa_verify(&public_key, &message, &signature) {
        return Err(Error::InvalidToken);
    }
    
    // Check token hasn't been used (prevent replay)
    if token_used(&token.message)? {
        return Err(Error::TokenReused);
    }
    
    // Mark token as used
    mark_token_used(&token.message)?;
    
    Ok(())
}
```

### 7.2 Key Distribution Server
**Purpose**: Distribute public prekey bundles  
**Build In-House**:
- Prekey storage and rotation
- Device registration
- Key revocation

**File Structure**:
```
backend/key_distribution/
├── server.rs
│   ├── upload_prekey_bundle()
│   ├── fetch_prekey_bundle()
│   ├── rotate_signed_prekey()
│   └── revoke_device()
├── prekey_store.rs
│   ├── store_identity_key()
│   ├── store_signed_prekey()
│   ├── store_one_time_prekeys()
│   └── consume_one_time_prekey()
└── revocation.rs
    ├── add_to_revocation_list()
    ├── check_revocation_status()
    └── distribute_revocation_list()
```

**Implementation**:
```rust
async fn upload_prekey_bundle(
    bundle: PrekeyBundle
) -> Result<()> {
    // Verify bundle signature
    verify_bundle_signature(&bundle)?;
    
    // Store identity key (long-term)
    storage.store_identity_key(
        bundle.device_id,
        bundle.identity_key
    ).await?;
    
    // Store signed prekey (rotates weekly)
    storage.store_signed_prekey(
        bundle.device_id,
        bundle.signed_prekey,
        bundle.signed_prekey_signature
    ).await?;
    
    // Store one-time prekeys (consumed on use)
    for otk in bundle.one_time_prekeys {
        storage.store_one_time_prekey(
            bundle.device_id,
            otk
        ).await?;
    }
    
    Ok(())
}

async fn fetch_prekey_bundle(
    device_id: DeviceId
) -> Result<PrekeyBundle> {
    // Check if device is revoked
    if revocation_list.is_revoked(device_id)? {
        return Err(Error::DeviceRevoked);
    }
    
    // Fetch bundle
    let identity_key = storage.get_identity_key(device_id).await?;
    let signed_prekey = storage.get_signed_prekey(device_id).await?;
    
    // Consume one-time prekey (atomic)
    let one_time_prekey = storage.consume_one_time_prekey(device_id).await?;
    
    Ok(PrekeyBundle {
        device_id,
        identity_key,
        signed_prekey,
        one_time_prekey,
    })
}
```

### 7.3 HSM Integration
**Purpose**: Hardware-backed root key storage and signing  
**Build In-House**:
- HSM client (PKCS#11 or vendor SDK)
- Key generation and storage
- Remote attestation

**File Structure**:
```
backend/hsm/
├── client.rs
│   ├── initialize_hsm()
│   ├── generate_root_key()
│   ├── sign_with_root_key()
│   └── attest_key()
├── pkcs11.rs (FFI bindings)
└── attestation.rs
    ├── verify_attestation()
    └── check_hsm_integrity()
```

---

## 8. Component 6: Client Applications {#component-6-clients}

### What We Build
Cross-platform mobile and desktop apps.

### 8.1 Mobile Apps (React Native or Flutter)
**Purpose**: Primary user interface for secure messaging  
**Build In-House**:
- All UI/UX components
- Native bridges to crypto/storage modules
- P2P mesh networking
- Voice/video calling

**File Structure**:
```
mobile/
├── src/
│   ├── screens/
│   │   ├── ChatScreen.tsx
│   │   ├── ContactsScreen.tsx
│   │   ├── SettingsScreen.tsx
│   │   └── MissionPresetsScreen.tsx
│   ├── components/
│   │   ├── MessageBubble.tsx
│   │   ├── ThreatIndicator.tsx
│   │   └── EncryptionStatus.tsx
│   ├── native/ (Rust FFI or Kotlin/Swift)
│   │   ├── crypto_bridge.rs
│   │   ├── storage_bridge.rs
│   │   └── network_bridge.rs
│   └── services/
│       ├── ProtocolService.ts
│       ├── MetadataDefense.ts
│       └── SelfDestructManager.ts
└── android/ or ios/
    └── (Platform-specific code)
```

### 8.2 Desktop Apps (Electron or Tauri)
**Purpose**: Desktop interface with additional features  
**Build In-House**:
- All UI components
- eBPF traffic tap (Linux)
- Screen security (screenshot blocking)

---

## 9. Component 7: Mixnet & Routing {#component-7-mixnet}

### What We Build
Onion routing and mix network for metadata hiding.

### 9.1 Mix Relays
**Purpose**: Break correlation between sender and recipient  
**Build In-House**:
- Sphinx packet format
- Mix cascade logic
- Batching and timing
- Cover traffic

**File Structure**:
```
mixnet/
├── relay.rs
│   ├── SphinxPacket
│   ├── process_packet()
│   ├── unwrap_layer()
│   └── forward_packet()
├── batching.rs
│   ├── batch_packets()
│   ├── flush_batch()
│   └── add_cover_traffic()
└── routing.rs
    ├── select_path()
    ├── construct_onion()
    └── verify_path()
```

**Implementation**:
```rust
struct SphinxPacket {
    header: Vec<u8>,  // Layered encryption
    payload: Vec<u8>, // Message
}

async fn process_packet(packet: SphinxPacket) -> Result<()> {
    // Unwrap one layer
    let (next_hop, inner_packet) = unwrap_layer(&packet)?;
    
    // Add to batch
    batch_manager.add_packet(next_hop, inner_packet).await?;
    
    // Flush batch periodically
    if batch_manager.should_flush() {
        batch_manager.flush().await?;
    }
    
    Ok(())
}
```

---

## 10. Development Roadmap & Team Structure {#roadmap}

### Team Structure (5-7 Engineers)
- **Security/Crypto Lead** (1 engineer)
  - Protocol design, PQC integration, key management
  - Code: `src/protocol/`, `src/storage/crypto_erase.rs`
  
- **AI/ML Lead** (1 engineer)
  - Anomaly detection, adaptive policy, federated learning
  - Code: `src/ai/`, model training scripts
  
- **Mobile Lead** (2 engineers)
  - React Native/Flutter apps, native bridges, P2P mesh
  - Code: `mobile/`, `src/native/`
  
- **Backend/Infra Lead** (1 engineer)
  - Mailbox server, key distribution, HSM, mixnet relays
  - Code: `backend/`, `mixnet/`
  
- **Network/Traffic Shaping Lead** (1 engineer)
  - Traffic shaper, flow tap, padding engine
  - Code: `src/network/`
  
- **PM/QA/Compliance** (1 person)
  - Test plans, threat modeling, demo prep, docs

### Timeline (12 weeks to demo-ready)

**Weeks 1-2: Foundation**
- Set up repos, CI/CD, dev environment
- Integrate crypto dependencies (liboqs, libsodium)
- Implement basic X3DH + Double Ratchet
- Basic encrypted storage

**Weeks 3-4: Core Protocol**
- Complete PQC-hybrid ratchet
- Message encryption/decryption
- Out-of-order handling
- Self-destruct (crypto-erase)

**Weeks 5-6: Metadata Defense**
- Implement GBDT inference engine
- Traffic shaper and padding
- Flow feature tap
- Threat scoring

**Weeks 7-8: Backend + Mixnet**
- Mailbox server
- Key distribution server
- Mix relays (basic onion routing)
- Blind token auth

**Weeks 9-10: Client Apps**
- Mobile UI (React Native)
- Integration with protocol layer
- P2P mesh networking
- Mission presets

**Weeks 11-12: Hardening + Demo**
- Security audits (fuzzing, pen-test)
- Performance optimization
- Demo video and presentation
- Documentation

---

## 11. Testing, Security & Compliance {#testing}

### Testing Strategy

**Unit Tests**
```rust
#[test]
fn test_hybrid_x3dh() {
    let (alice_id, alice_sk) = generate_identity_keypair();
    let (bob_id, bob_sk) = generate_identity_keypair();
    
    let alice_bundle = generate_prekey_bundle(&alice_id, &alice_sk);
    let bob_bundle = generate_prekey_bundle(&bob_id, &bob_sk);
    
    let alice_session = initiate_session(&bob_bundle, &alice_id, &alice_sk);
    let bob_session = accept_session(&alice_session.init_message, &bob_id, &bob_sk);
    
    assert_eq!(alice_session.root_key, bob_session.root_key);
}
```

**Integration Tests**
```rust
#[tokio::test]
async fn test_end_to_end_message() {
    let alice = Client::new("alice").await;
    let bob = Client::new("bob").await;
    
    alice.send_message("bob", "Hello!").await?;
    let msg = bob.receive_message().await?;
    
    assert_eq!(msg.plaintext, "Hello!");
}
```

**Security Tests**
- Fuzzing (libFuzzer, AFL++)
- Side-channel tests (ctgrind, dudect)
- Traffic analysis resistance (AUC < 0.6)
- Forensic analysis (no key recovery post-destruct)

**Compliance**
- FIPS 140-2 (use FIPS-validated crypto modules)
- Common Criteria EAL4+
- SOC 2 Type II (backend)
- NIST SP 800-56C r2 (KDF)

---

## 12. Dependencies: What We DON'T Build {#dependencies}

### Crypto Primitives (Audited Libraries)
```toml
[dependencies]
# Post-Quantum Cryptography
liboqs = "0.10"          # NIST PQC (Kyber, Dilithium)

# Classical Cryptography
libsodium-sys = "0.2"    # X25519, Ed25519, ChaCha20-Poly1305
openssl = "0.10"         # AES-GCM, RSA, SHA

# Hashing
blake3 = "1.5"           # Fast cryptographic hash
sha3 = "0.10"            # SHA3-256

# Secure Random
getrandom = "0.2"        # OS CSPRNG
```

### Why We Don't Build These
1. **Security**: Constant-time, side-channel hardened implementations require years of expert work
2. **Compliance**: FIPS 140-2 validation costs $100K-$500K and takes 12-18 months
3. **Maintenance**: Crypto libraries need continuous security updates
4. **Standards**: NIST PQC is standardized and battle-tested
5. **Liability**: Bugs in crypto can destroy entire systems

### Other Dependencies (Standard Libraries)
```toml
[dependencies]
# Networking
tokio = "1.35"           # Async runtime
quinn = "0.10"           # QUIC implementation
hyper = "1.0"            # HTTP/3

# Serialization
serde = "1.0"            # Serialization framework
bincode = "1.3"          # Binary serialization

# Database
rusqlite = "0.30"        # SQLite (we add encryption)
```

---

## Appendix A: Quick Start Commands

### Build Everything
```bash
# Clone repo
git clone https://github.com/your-org/CYPHRA
cd CYPHRA

# Install dependencies
cargo build --release          # Rust components
npm install                    # Mobile/Desktop

# Build mobile apps
cd mobile
npx react-native run-android   # Android
npx react-native run-ios       # iOS

# Build desktop
cd desktop
npm run build                  # Electron/Tauri

# Run backend
cd backend
cargo run --release            # Mailbox + Key Distribution
```

### Run Tests
```bash
# Unit tests
cargo test

# Integration tests
cargo test --test integration

# Security tests
cargo fuzz run fuzzer_name

# Benchmark
cargo bench
```

### Train ML Models
```bash
cd CYPHRA/scripts

# Preprocess datasets
python preprocess_iscxvpn2016_proper.py
python preprocess_unswnb15.py
python preprocess_cicids2017.py

# Train ensemble models
python train_revolutionary_99_percent.py

# Export models
python export_models_to_production.py
```

---

## Appendix B: Resource Requirements

### Development Hardware
- **Laptop**: 16GB RAM, 8-core CPU, 512GB SSD (minimum)
- **GPU**: NVIDIA RTX 3060+ for ML training (optional but recommended)
- **HSM**: YubiHSM 2 or AWS CloudHSM for testing

### Cloud Infrastructure (Demo)
- **Mailbox Server**: 2 vCPU, 4GB RAM
- **Mix Relays**: 3x (1 vCPU, 2GB RAM each)
- **Key Distribution**: 1 vCPU, 2GB RAM
- **Database**: PostgreSQL (managed service)

### Estimated Costs
- **Development**: $0 (open-source tools)
- **Cloud (3 months demo)**: ~$300/month
- **HSM**: YubiHSM 2 (~$650 one-time)
- **Compliance Audits**: $10K-$50K (post-hackathon)

---

## Appendix C: Key Metrics & Success Criteria

### Security Metrics
- ✅ **Forward Secrecy**: Verified via protocol analyzer
- ✅ **PQ Resistance**: Hybrid Kyber+X25519, Dilithium+Ed25519
- ✅ **Traffic Analysis**: Classifier AUC < 0.6 on shaped flows
- ✅ **Forensic Denial**: Zero key recovery post-destruct (cold boot test)
- ✅ **Threat Detection**: 99%+ accuracy on network intrusion datasets

### Performance Metrics
- ✅ **Latency**: p50 < 300ms, p99 < 1s (E2E message delivery)
- ✅ **Throughput**: 1000+ msgs/sec per relay
- ✅ **Battery**: < 5% drain per hour (active use)
- ✅ **Storage**: < 50MB app size, < 100MB data per 10K messages

### UX Metrics
- ✅ **Onboarding**: < 2 minutes to first message
- ✅ **Mission Preset**: 1 tap to activate
- ✅ **Reliability**: 99.9% message delivery (when online)

---

## Questions or Need Help?

Contact: [Your Team Email]  
Docs: https://docs.CYPHRA.org  
GitHub: https://github.com/your-org/CYPHRA

---

**Built with 🔒 for National Security**  
**CYPHRA Team © 2025**

