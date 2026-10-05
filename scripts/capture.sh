#!/usr/bin/env bash
#
# capture.sh
# ----------
# Simple wrapper around tshark for capturing network traffic.
# Usage:
#   ./capture.sh -i <interface> -w <output.pcap> [optional tshark args]
#
# Example:
#   ./capture.sh -i eth0 -w data/live.pcap -a duration:30
#
# Requires tshark (part of Wireshark) to be installed and in PATH.

set -euo pipefail

# Default values
INTERFACE=""
OUTFILE=""
TSHARK_ARGS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interface)
            INTERFACE="$2"
            shift 2
            ;;
        -w|--output)
            OUTFILE="$2"
            shift 2
            ;;
        *)  # Assume it's a tshark argument
            TSHARK_ARGS+=("$1")
            shift
            ;;
    esac
done

if [[ -z "$INTERFACE" || -z "$OUTFILE" ]]; then
    echo "Usage: $0 -i <interface> -w <output.pcap> [tshark options]"
    echo "Example: $0 -i eth0 -w data/live.pcap -a duration:60"
    exit 1
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTFILE")"

echo "[+] Starting capture on interface '$INTERFACE' -> '$OUTFILE'"
echo "[+] Additional tshark arguments: ${TSHARK_ARGS[*]:-none}"
# Run tshark; -w writes raw pcap, -l ensures line‑buffered output for progress if needed
tshark -i "$INTERFACE" -w "$OUTFILE" "${TSHARK_ARGS[@]}"
echo "[+] Capture finished. File saved to: $OUTFILE"