package com.cyphra.messenger.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

// System default sans-serif (matches the TSX's -apple-system, Inter, system-ui)
val InterFamily = FontFamily.Default
val MonoFamily  = FontFamily.Monospace

val CyphraTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Bold,
        fontSize   = 34.sp,
        letterSpacing = 3.sp,  // matches TSX 0.15em on CYPHRA title
        color = CyphraTextPrimary,
    ),
    headlineMedium = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize   = 22.sp,
        color = CyphraTextPrimary,
    ),
    titleMedium = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.SemiBold,
        fontSize   = 14.sp,
        color = CyphraTextPrimary,
    ),
    bodyMedium = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Normal,
        fontSize   = 13.sp,
        lineHeight = 18.sp,
        color = CyphraTextPrimary,
    ),
    bodySmall = TextStyle(
        fontFamily = InterFamily,
        fontWeight = FontWeight.Normal,
        fontSize   = 11.sp,
        color = CyphraTextSecondary,
    ),
    labelSmall = TextStyle(
        fontFamily = MonoFamily,
        fontWeight = FontWeight.Normal,
        fontSize   = 10.sp,
        letterSpacing = 0.8.sp,
        color = CyphraTextMuted,
    ),
    labelMedium = TextStyle(
        fontFamily = MonoFamily,
        fontWeight = FontWeight.Bold,
        fontSize   = 12.sp,
        letterSpacing = 0.5.sp,
        color = CyphraAmber,
    ),
)
