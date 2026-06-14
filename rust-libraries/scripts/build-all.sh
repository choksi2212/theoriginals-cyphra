#!/bin/bash
# Build CYPHRA libraries for all platforms

set -e

echo "Building CYPHRA Libraries..."

# Native build
echo "Building for native platform..."
cargo build --release

# WebAssembly
echo "Building for WebAssembly..."
wasm-pack build protocol --target web --out-dir ../wasm-dist

# Android
echo "Building for Android..."
cargo ndk -t arm64-v8a -t armeabi-v7a \
  -o android-dist/jniLibs \
  build --release

# iOS
echo "Building for iOS..."
cargo build --target aarch64-apple-ios --release
cargo build --target x86_64-apple-ios --release

echo "Build complete! Artifacts in:"
echo "  - target/release/ (native)"
echo "  - wasm-dist/ (web)"
echo "  - android-dist/jniLibs/ (android)"
echo "  - target/aarch64-apple-ios/release/ (ios)"
