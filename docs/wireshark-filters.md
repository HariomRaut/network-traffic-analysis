# Wireshark Filters – Quick Reference

## Capture vs. Display Filters
- **Capture filters** (using libpcap syntax) limit what is written to the capture file.
  - Set before starting capture: Capture → Capture Filters → or via `tshark -f`.
- **Display filters** (using Wireshark display filter language) are applied after capture to hide/show packets.
  - Enter in the filter bar at the top or apply via right‑click → “Apply as Filter”.

## Common Capture Filters
| Purpose | Filter |
|---------|--------|
| Capture only traffic to/from a specific host | `host 10.0.0.5` |
| Capture only TCP port 80 (HTTP) | `tcp port 80` |
| Capture only UDP port 53 (DNS) | `udp port 53` |
| Capture only traffic from a subnet | `net 10.0.0.0/24` |
| Exclude SSH (to reduce noise) | `not port 22` |
| Capture only SYN packets (TCP handshake start) | `tcp[tcpflags] & tcp-syn != 0` |

## Common Display Filters
| Purpose | Filter |
|---------|--------|
| Show only HTTP requests | `http.request` |
| Show only HTTP responses | `http.response` |
| Show HTTP GET with a specific query string | `http.request.uri contains "login"` |
| Show DNS queries | `dns.qry.name` |
| Show DNS responses | `dns.flags.response == 1` |
| Show FTP commands (including clear‑text credentials) | `ftp.request.command` |
| Show FTP responses containing credentials | `ftp.response` |
| Show Telnet data (often clear‑text) | `telnet` |
| Show HTTP Basic Auth header | `http.authorization` |
| Show TCP retransmissions | `tcp.analysis.retransmission` |
| Show out‑of‑order packets | `tcp.analysis.out_of_order` |
| Show duplicate ACKs | `tcp.analysis.duplicate_ack` |
| Show ICMP error messages (useful for troubleshooting) | `icmp.type == 3` |
| Show ARP traffic | `arp` |
| Show only packets with a specific TTL value | `ip.ttl == 64` |
| Show TLS handshake (Client Hello) | `tls.handshake.type == 1` |

## Combining Filters
- Use `and`, `or`, `not` (or `&&`, `||`, `!`) to combine.
  - Example: Show HTTP POST requests that contain the word “password” in the body:  
    `http.request.method == POST and http.file_data contains "password"`
- Use parentheses for grouping:  
  `(http.request or http.response) and ip.src == 10.0.0.5`

## Colouring Rules (Optional)
- Wireshark lets you colour packets based on display filters (View → Colouring Rules).
  - Example: Colour all FTP credential attempts red:  
    Filter: `ftp.request.command == USER and ftp.request.arg contains ":"`  
    Colour: Red background, white text.

## Exporting Filtered Results
- After applying a display filter, you can export the visible packets:
  - File → Export Specified Packets → select “Displayed” → choose format (PCAPNG, PCAP, CSV, Plain Text, etc.).

## Tips for Efficient Analysis
1. **Start wide, then narrow** – begin with no display filter to get an overview, then apply filters to zoom in.
2. **Use follow‑stream** – right‑click a TCP stream → “Follow” → “TCP Stream” to see the full conversation (useful for reconstructing FTP sessions).
3. **Extract objects** – File → Export Objects → HTTP, FTP, TFTP, etc., to retrieve files transferred in the capture.
4. **Time referencing** – Right‑click a packet → “Set Time Reference” to compare relative times of related events.
5. **Statistics menu** – Useful for quick summaries:
   - Statistics → Conversations (breakdown by endpoint/protocol).
   - Statistics → HTTP → Requests/Responses.
   - Statistics → DNS → Queries.

## Example: Detecting Clear‑Text FTP Credentials
1. Apply display filter: `ftp.request.command == USER and ftp.request.arg contains ":"`
2. Each matching line shows the USER command where the argument includes a colon (`user:pass` style some FTP implementations use for `USER`+`PASS` in one).
   - Alternatively, look for the `PASS` command: `ftp.request.command == PASS`.
3. Right‑click → “Follow” → “TCP Stream” to see the entire login exchange.

## Example: Isolating an IP Conflict
- Look for duplicate ARP replies: `arp && arp.opcode == 2` (is-at) and check if the same MAC address appears for two different IPs, or the same IP appears with two different MACs.
- Filter: `arp && arp.src.hw_mac == aa:bb:cc:dd:ee:ff` (replace with suspected MAC) and see if multiple IPs are reported.

## References
- Wireshark Display Filter Reference: https://www.wireshark.org/docs/dfref/
- Wireshark Capture Filters: https://www.wireshark.org/docs/wsug_html_chunked/ChapterCapts.html#CaptureFilters
- PacketLife.net – Quick Reference Cards: https://packetlife.net/media/library/13/Wireshark-Display-Filter.pdf
