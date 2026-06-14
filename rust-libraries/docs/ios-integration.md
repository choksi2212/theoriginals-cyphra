# iOS Application Integration Guide

Integration guide for CYPHRA libraries into iOS apps using Swift.

## Build for iOS

```bash
cargo build --target aarch64-apple-ios --release
cargo build --target x86_64-apple-ios --release
```

## Swift Wrapper

```swift
class CYPHRAPS {
    func generateIdentity() -> Data {
        return cyphra_generate_identity()
    }
    
    func encryptMessage(sessionId: Data, plaintext: Data) -> Data {
        return cyphra_encrypt(sessionId, plaintext)
    }
}
```

See full examples in `examples/ios-integration/`
