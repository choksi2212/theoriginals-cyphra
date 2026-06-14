@echo off
echo ═══════════════════════════════════════════════════════
echo   CYPHRA Mixnet — Starting Relay Nodes
echo   5 independent relays (ports 6001-6005)
echo ═══════════════════════════════════════════════════════
echo.

start /B "Relay 0" node relay.js 6001
start /B "Relay 1" node relay.js 6002
start /B "Relay 2" node relay.js 6003
start /B "Relay 3" node relay.js 6004
start /B "Relay 4" node relay.js 6005

echo [OK] 5 mix relays launched (ports 6001-6005)
echo.
echo Preset routing:
echo   Secure Base:      direct (no relays)
echo   Balanced:         6001 → 6002 → backend
echo   Silent Patrol:    6001 → 6002 → 6003 → 6004 → backend
echo   Compromised:      6001 → 6002 → 6003 → 6004 → 6005 → backend
echo.
pause
