package com.cyphra.messenger.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// ── Cyphra Colour System — Amber/Navy Military Theme ──────────────────────
// Matches cyphra_app.tsx design tokens exactly

val CyphraBg            = Color(0xFF010810)   // bgBase — nearly black
val CyphraSurface       = Color(0xFF0B1628)   // bgCard — dark navy
val CyphraSurfaceHigh   = Color(0xFF112035)   // bgElevated
val CyphraAmber         = Color(0xFFF59E0B)   // Primary amber accent
val CyphraAmberBright   = Color(0xFFFCD34D)   // Light amber highlights
val CyphraAmberDim      = Color(0xFF92600A)   // Muted amber
val CyphraAmberGlow     = Color(0x2EF59E0B)   // 18% amber glow
val CyphraAmberBorder   = Color(0x4DF59E0B)   // 30% amber border
val CyphraBorder        = Color(0xFF1A3A5C)   // Dark blue border
val CyphraBorderLight   = Color(0xFF2A4A6C)   // Lighter border
val CyphraTextPrimary   = Color(0xFFF0F4F8)   // Main text
val CyphraTextSecondary = Color(0xFF8FA3B8)   // Secondary text
val CyphraTextMuted     = Color(0xFF3D5A73)   // Dim/label text
val CyphraSafe          = Color(0xFF22C55E)   // Green (safe/online)
val CyphraWarning       = Color(0xFFF59E0B)   // Warning = amber
val CyphraDanger        = Color(0xFFF97316)   // Orange danger
val CyphraCritical      = Color(0xFFEF4444)   // Red critical
val CyphraTeal          = Color(0xFF14B8A6)
val CyphraCyan          = Color(0xFF06B6D4)

// Backward-compatible aliases (existing screens reference these names)
val CyphraAccent        = CyphraAmber
val CyphraSuccess       = CyphraSafe

private val DarkColorScheme = darkColorScheme(
    primary             = CyphraAmber,
    onPrimary           = CyphraBg,
    primaryContainer    = CyphraAmber,
    onPrimaryContainer  = CyphraBg,
    secondary           = CyphraTextSecondary,
    onSecondary         = CyphraBg,
    secondaryContainer  = CyphraSurface,
    onSecondaryContainer= CyphraTextSecondary,
    background          = CyphraBg,
    onBackground        = CyphraTextPrimary,
    surface             = CyphraSurface,
    onSurface           = CyphraTextPrimary,
    surfaceVariant      = CyphraSurfaceHigh,
    onSurfaceVariant    = CyphraTextSecondary,
    outline             = CyphraBorder,
    outlineVariant      = CyphraBorderLight,
    error               = CyphraCritical,
    onError             = Color.White,
    tertiary            = CyphraSafe,
    onTertiary          = CyphraBg,
)

@Composable
fun CyphraTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        typography  = CyphraTypography,
        content     = content,
    )
}
