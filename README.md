# Network Traffic Analysis and Troubleshooting Exercise

## Project Overview
This project demonstrates how to capture, analyse, and troubleshoot network traffic using **Wireshark** and **Cisco Packet Tracer**. The goals are to:

1. **Capture live traffic** on a lab LAN and inspect protocols (TCP handshake, DNS, HTTP, etc.).
2. **Identify confidentiality risks** such as clear‑text credential transmission.
3. **Simulate common network faults** (IP conflict, mis‑configured gateway) and isolate them using traceroute, ping, and Wireshark filters.
4. **Design a segmented network** with VLANs and ACLs to mitigate lateral movement and sniffing risks.
5. **Document findings and remediation** in a clear, reproducible report.

## Directory Structure
```
network-traffic-analysis/
│
├─ README.md                 # This file
├─ docs/
│   ├─ wireshark-filters.md  # Common display and capture filters
│   ├─ packet-tracer-guide.md# Quick steps to build a VLAN‑segmented topology in Packet Tracer
│   └─ tcp-handshake.md      # Illustrated explanation of the 3‑way handshake
├─ scripts/
│   ├─ capture.sh            # Bash script to start a tshark capture (optional)
│   ├─ analyse-pcap.py       # Python script using pyshark to extract clear‑text credentials
│   └─ vlan-config.txt       # Example Cisco IOS commands for VLAN creation and ACLs
├─ data/
│   ├─ sample.pcap           # Example packet capture (contains clear‑text FTP login)
│   ├─ sample-dns.txt        # DNS query extract from the capture
│   └─ sample-http.txt       # HTTP request/response extract
├─ reports/
│   ├─ analysis-report-template.md   # Template for a traffic‑analysis report
│   └─ sample-analysis-report.md     # Example filled‑out report based on the lab
└─ references/
    ├─ Wireshark_User_Guide.pdf
    ├─ Cisco_Packet_Tracer_Tutorial.pdf
    └─ TCP_Illustrated_Vol1.pdf
```

## How to Reproduce the Work

### Prerequisites
- **Wireshark** (or **tshark** for command‑line capture) installed.
- **Cisco Packet Tracer** (free from Cisco NetAcad) installed.
- Python 3.8+ with `pyshark` (`pip install pyshark`).
- A lab environment with at least two hosts that can communicate (can be virtual machines or physical PCs).
- Optional: a managed switch that supports VLANs for the segmentation exercise (or rely purely on Packet Tracer for design).

### Step‑by‑Step

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your‑username>/network-traffic-analysis.git
   cd network-traffic-analysis
   ```

2. **Start a traffic capture**
   - If you prefer GUI: Launch Wireshark, select the appropriate interface, and begin capturing.
   - For CLI: Run the provided script:
     ```bash
     ./scripts/capture.sh -i eth0 -w data/live.pcap
     ```
     (Adjust `-i` to your interface.)

3. **Generate some traffic**
   - From Host A, run an FTP client to Host B: `ftp <hostB>` and log in with a test user/password (e.g., `user`/`pass`).
   - Browse a simple HTTP page: `curl http://<hostB>/`.
   - Perform a DNS lookup: `nslookup example.com`.
   - Optionally simulate faults:
        * Assign the same IP to two hosts to create an IP conflict.
        * Change the default gateway on one host to an incorrect address.

4. **Stop capture** after you have enough data (a few minutes).

5. **Analyse the capture**
   - Open the `.pcap` file in Wireshark.
   - Use display filters to isolate interesting traffic:
        * `ftp.request.command == USER && ftp.request.arg contains ":"` – to see clear‑text credentials.
        * `dns.qry.name` – to view DNS queries.
        * `http.request.method` – to see HTTP requests.
   - Alternatively, run the Python script:
     ```bash
     python scripts/analyse-pcap.py data/live.pcap
     ```
     It will print any detected clear‑text credentials (FTP, Telnet, HTTP Basic Auth) and summary statistics.

6. **Troubleshoot simulated faults**
   - Use `ping`, `traceroute`, and Wireshark (look for duplicate ARP replies, ICMP Destination Unreachable, etc.) to isolate the problem.
   - Document the steps taken and the observed symptoms.

7. **Design a segmented network in Packet Tracer**
   - Follow the guide in `docs/packet-tracer-guide.md` to create:
        * Three VLANs: Faculty (10), Students (20), Servers (30).
        * A router‑on‑a‑stick or multilayer switch with inter‑VLAN routing.
        * An ACL on the router that permits only required traffic (e.g., Students → Servers: HTTP/HTTPS only).
   - Verify that a host in the Students VLAN cannot directly ping a host in the Faculty VLAN unless allowed by ACL.

8. **Write the report**
   - Copy `reports/analysis-report-template.md` to `reports/analysis-report-<date>.md`.
   - Fill in the sections: Executive Summary, Scope, Methodology, Findings (clear‑text credentials, faults observed, segmentation effectiveness), Conclusion, and Appendices (pcap, screenshots, config snippets).

### Example Workflow (Two Ubuntu VMs on VirtualBox)
```bash
# On VM A (sender)
sudo apt-get install -y ftp curl dnsutils
# On VM B (receiver)
sudo apt-get install -y vsftpd apache2

# Start capture on VM A
tshark -i eth0 -w data/capture.pcap &
# FTP login (clear‑text)
ftp <IP_of_VM_B>
# User: testuser
# Pass: testpass
# Browse HTTP
curl http://<IP_of_VM_B>
# Simulate IP conflict on VM C (same IP as VM B)
# Stop capture after a few minutes
kill %1
# Analyse
python scripts/analyse-pcap.py data/capture.pcap
```

## Key Learning Outcomes
- Proficiency with Wireshark/tshark for capture and deep packet inspection.
- Ability to spot confidentiality breaches (clear‑text credentials) in live traffic.
- Hands‑on experience troubleshooting IP conflicts and gateway misconfigurations.
- Skills in designing VLAN‑based segmentation and implementing basic ACLs.
- Experience translating packet‑level observations into actionable network‑security controls.

## Extending the Project
- Integrate **Zeek (Bro)** for automated behavioural analysis.
- Use **Suricata** or **Snort** as an IDS/IPS to generate alerts on suspicious traffic.
- Automate the capture‑analyse‑alert pipeline with a cron job or systemd service.
- Export Wireshark objects (e.g., extracted files) for malware analysis.
- Perform QoS measurements (latency, jitter) for voice/video traffic.

## License
This project is licensed under the MIT License – see the `LICENSE` file for details.

## Acknowledgements
- Wireshark team – the world’s foremost network protocol analyzer.
- Cisco Packet Tracer – excellent tool for learning networking concepts.
- The creators of pyshark for Pythonic packet processing.
- Various open‑source labs (e.g., VulnHub, TryHackMe) for inspiration.
