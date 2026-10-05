#!/usr/bin/env python3
"""
analyse-pcap.py
---------------
Analyse a pcap file for clear‑text credentials (FTP, Telnet, HTTP Basic Auth)
and print a summary.

Requires:
    pip install pyshark

Usage:
    python analyse-pcap.py <path-to-pcap>
"""

import sys
import pyshark
from collections import defaultdict

def extract_credentials(pcap_path):
    cap = pyshark.FileCapture(pcap_path, keep_packets=False)
    credentials = []
    stats = defaultdict(int)

    for pkt in cap:
        try:
            # FTP
            if 'ftp' in pkt:
                if hasattr(pkt.ftp, 'request_command') and pkt.ftp.request_command.upper() == 'USER':
                    # Some implementations send user:pass in USER argument
                    if hasattr(pkt.ftp, 'request_arg') and ':' in pkt.ftp.request_arg:
                        cred = pkt.ftp.request_arg
                        credentials.append(('FTP', cred))
                        stats['ftp_user'] += 1
                if hasattr(pkt.ftp, 'request_command') and pkt.ftp.request_command.upper() == 'PASS':
                    if hasattr(pkt.ftp, 'request_arg'):
                        cred = pkt.ftp.request_arg
                        credentials.append(('FTP', cred))
                        stats['ftp_pass'] += 1
            # Telnet
            if 'telnet' in pkt:
                if hasattr(pkt.telnet, 'data'):
                    data = pkt.telnet.data
                    # Very naive: look for patterns like "login:" or "password:" followed by text
                    if 'login' in data.lower() or 'password' in data.lower():
                        credentials.append(('Telnet', data[:50]))  # truncate
                        stats['telnet'] += 1
            # HTTP Basic Auth
            if 'http' in pkt:
                if hasattr(pkt.http, 'authorization'):
                    auth = pkt.http.authorization
                    if auth.startswith('Basic '):
                        credentials.append(('HTTP Basic', auth))
                        stats['http_basic'] += 1
        except AttributeError:
            # Layer not present in this packet
            continue
        except Exception as e:
            # Unexpected error; skip packet but continue
            continue

    cap.close()
    return credentials, dict(stats)

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyse-pcap.py <path-to-pcap>")
        sys.exit(1)
    pcap_path = sys.argv[1]
    try:
        creds, stats = extract_credentials(pcap_path)
    except Exception as e:
        print(f"Error opening pcap: {e}")
        sys.exit(1)

    print(f"=== Analysis of {pcap_path} ===")
    print(f"Total packets processed: {sum(stats.values()) if stats else 0}")
    print("\nStatistics:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    if creds:
        print("\nDetected potential credentials (showing first 5):")
        for typ, val in creds[:5]:
            print(f"  [{typ}] {val}")
        if len(creds) > 5:
            print(f"  ... and {len(creds)-5} more")
    else:
        print("\nNo clear‑text credentials detected.")

if __name__ == "__main__":
    main()