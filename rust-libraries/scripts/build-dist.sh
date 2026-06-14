#!/bin/bash
# Build distribution libraries for all platforms

set -e

echo "🔨 Building CYPHRA Distribution Libraries..."

# Create dist directories
mkdir -p dist/web dist/android/jniLibs dist/ios

# Build Web (WASM)
echo "📦 Building for Web (WASM)..."
cd protocol
wasm-pack build --target web --out-dir ../dist/web
cd ..

# Build Android (JNI)
echo "📦 Building for Android (JNI)..."
cargo ndk -t arm64-v8a -t armeabi-v7a -t x86 -t x86_64 \
  -o dist/android/jniLibs \
  build --release

# Build iOS (Static Library)
echo "📦 Building for iOS (Static Library)..."
cargo build --target aarch64-apple-ios --release
cargo build --target x86_64-apple-ios --release
cp target/aarch64-apple-ios/release/libcyphra.a dist/ios/
cp target/x86_64-apple-ios/release/libcyphra.a dist/ios/libcyphra_sim.a

echo "✅ Build complete!"
echo ""
echo "Distribution files:"
echo "  📁 dist/web/ - WebAssembly for web apps"
echo "  📁 dist/android/ - JNI libraries for Android"
echo "  📁 dist/ios/ - Static libraries for iOS"
