# Android Application Integration Guide

Integration guide for CYPHRA libraries into Android apps using JNI.

## Build for Android

```bash
cargo ndk -t arm64-v8a -t armeabi-v7a \
  -o ../your-android-app/app/src/main/jniLibs \
  build --release
```

## Kotlin Wrapper

```kotlin
class CYPHRAPS {
    external fun generateIdentity(): ByteArray
    external fun encryptMessage(sessionId: ByteArray, plaintext: ByteArray): ByteArray
    external fun decryptMessage(sessionId: ByteArray, ciphertext: ByteArray): ByteArray
    
    companion object {
        init { System.loadLibrary("cyphra_protocol") }
    }
}
```

See full examples in `examples/android-integration/`
