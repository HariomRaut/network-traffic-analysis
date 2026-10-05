# Sample Network Traffic Analysis Report

**Client:** Internal Lab – University Network  
**Engagement Dates:** 2025-10-05 – 2025-10-05  
**Report Date:** 2025-10-05  
**Prepared By:** Hariom Raut  
**Confidentiality:** Internal Use Only

---

## Executive Summary
A 10‑minute packet capture was performed on a lab LAN consisting of two Ubuntu VMs (VM‑A and VM‑B) and a Windows host acting as a router. The capture revealed **two** critical security issues: clear‑text FTP credentials and an IP conflict causing intermittent connectivity. A simple VLAN segmentation design was tested in Cisco Packet Tracer and proved effective at isolating traffic between user groups.

---

## Scope and Objectives
- **In Scope:** 
  - Subnet 192.168.0.0/24 (all hosts).
  - Protocols: FTP, Telnet, HTTP, DNS, ARP, ICMP.
- **Out of Scope:** 
  - Traffic beyond the lab router (internet).
- **Objectives:** 
  1. Detect any clear‑text credential transmission.
  2. Identify network faults affecting connectivity.
  3. Evaluate a basic VLAN‑based segmentation design.
  4. Provide remediation steps.

---

## Methodology
- **Capture:** `tshark -i eth0 -w data/live.pcap -a duration:600` (10 minutes).
- **Analysis:** 
  - Wireshark display filters: `ftp.request.command == PASS`, `http.request.method`, `dns.qry.name`.
  - Python script `scripts/analyse-pcap.py` to extract possible credentials.
- **Fault Simulation:** 
  - Assigned IP 192.168.0.10 to both VM‑A and VM‑B to create an IP conflict.
  - Changed default gateway on VM‑B to 192.168.0.254 (non‑existent) to test gateway misconfiguration.
- **Segmentation Design:** 
  - Created a three‑VLAN topology in Packet Tracer (VLAN10 Faculty, VLAN20 Students, VLAN30 Servers) with router‑on‑a‑stick and ACL restricting student→server to HTTP/HTTPS only.
  - Verified via simulated pings.

---

## Findings

### Finding 1: Clear‑Text FTP Credentials
- **Evidence:** 
  - Packet #342: FTP PASS command with argument `labpass`.
  - Packet #341: FTP USER command with argument `labuser`.
  - Follow‑up FTP session showed successful login and directory listing.
- **Impact:** Anyone on the LAN with a packet sniffer could obtain the FTP login and upload/download or modify files.
- **Likelihood:** High – service was running on VM‑B (vsftpd) and accessible via port 21.
- **Remediation:** 
  - Replace FTP with SFTP (SSH) or FTPS (TLS).
  - If FTP must remain, restrict access via firewall to specific IPs and use strong passwords.
  - Consider using `vsftpd` with TLS enabled (`ssl_enable=YES`).

### Finding 2: IP Conflict Causing Intermittent Connectivity
- **Evidence:** 
  - ARP packets showed two different MAC addresses (00:0c:29:xx:xx:xx and 00:0c:29:yy:yy:yy) both claiming 192.168.0.10.
  - Ping from VM‑A to VM‑B alternated between success and “Destination Host Unreachable”.
  - ICMP Destination Unreachable (type 3, code 1) observed when the conflicting host replied with wrong MAC.
- **Impact:** Users experienced unreliable network sessions, leading to timeouts and failed transfers.
- **Likelihood:** Medium – caused by manual IP misconfiguration; rare in DHCP environments but possible with static IP assignments.
- **Remediation:** 
  - Correct the IP assignment: ensure each device has a unique address.
  - Implement DHCP with reservations or use an IPAM tool to track assignments.
  - Enable duplicate IP detection on the OS (most modern OSes do this automatically).

### Finding 3: DNS Query Exposure of Internal Hostnames
- **Evidence:** 
  - DNS query for `fileserver.internal.lab` (type A) observed.
  - No external domain queries; all queries were for internal resources.
- **Impact:** Reveals internal naming scheme, useful for reconnaissance if an attacker gains foothold.
- **Likelihood:** Low – internal DNS traffic is expected; exposure only problematic if leaked outside.
- **Remediation:** 
  - Keep internal DNS zones internal (no forwarding to public DNS for private zones).
  - Consider DNS over TLS (DoT) or DNS over HTTPS (DoH) for privacy if needed.

### Finding 4: VLAN Segmentation Effectiveness (Packet Tracer Test)
- **Test:** 
  - From a host in VLAN20 (Students) attempted ping to a host in VLAN10 (Faculty) – **blocked**.
  - From VLAN20 to VLAN30 (Servers) on ports 80 and 443 – **allowed**.
  - Attempt to connect to VLAN30 on port 22 (SSH) – **blocked**.
- **Evidence:** 
  - Packet Tracer simulation mode showed ICMP Echo Request dropped at the router ACL.
  - Successful HTTP GET to server VLAN returned TCP SYN/ACK and subsequent data flow.
- **Impact:** Demonstrates that a simple VLAN+ACL scheme can enforce segmentation based on business needs.
- **Recommendation:** 
  - Apply the same design to the physical lab switch.
  - Regularly review ACLs as services evolve.
  - Consider private VLANs or VRFs for stricter isolation if required.

---

## Network Diagram & Topology
```
[VM-A (192.168.0.10)]   [VM-B (192.168.0.10)]   [WinRouter (192.168.0.1)]
      \                       /                         |
       \                     /                          |
        \___________________/                           |
                  |                                     |
                [Switch]                                |
                  |                                     |
               [Capture Point (eth0)]                   |
```
*(Note: The IP conflict caused both VMs to claim the same address.)*

After remediation, IPs were changed to:
- VM‑A: 192.168.0.10
- VM‑B: 192.168.0.20
- Router: 192.168.0.1

VLAN design (Packet Tracer):
- VLAN10 Faculty: 192.168.10.0/24
- VLAN20 Students: 192.168.20.0/24
- VLAN30 Servers: 192.168.30.0/24
- Router sub‑interfaces: .10, .20, .30 with corresponding IPs.
- ACL 100: permit tcp any 192.168.30.0 0.0.0.255 eq www; permit tcp any 192.168.30.0 0.0.0.255 eq 443; deny ip 192.168.20.0 0.0.0.255 192.168.30.0 0.0.0.255; permit ip any any.

---

## Remediation Recommendations
1. **Encrypt FTP** – migrate to SFTP/SSH on VM‑B; test with `ssh labuser@<IP>`.
2. **Resolve IP Conflict** – assign VM‑B a unique IP (192.168.0.20) and document in IPAM.
3. **Fix Gateway** – set VM‑B default gateway to 192.168.0.1.
4. **Deploy SFTP** – ensure OpenSSH server is configured, disable password auth if possible, use key‑based.
5. **Implement VLANs on Physical Switch** – follow `scripts/vlan-config.txt` for baseline.
6. **Add ACL** – apply the ACL shown above to restrict inter‑VLAN traffic per policy.
7. **Monitor** – install a lightweight IDS (e.g., Snort) in alert mode on the capture interface to flag clear‑text FTP or suspicious ARP.
8. **Document** – keep network diagram and IP address spreadsheet up‑to‑date.

---

## Conclusion
The lab network exhibited two immediate risks: clear‑text credentials and an IP conflict. Both were readily identifiable via packet analysis and corrected with straightforward configuration changes. The proposed VLAN segmentation, validated in Cisco Packet Tracer, offers a practical path to isolate user groups and limit lateral movement. Applying the remediation steps will significantly improve the security posture of the lab environment.

---

## Appendices
- **Appendix A:** Capture file (SHA256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`) – `data/live.pcap` (not included in repo due to size).
- **Appendix B:** Wireshark screenshot showing FTP PASS packet – `reports/ftp_pass_screenshot.png`.
- **Appendix C:** Extracted credentials (redacted) – `reports/extracted-creds.txt`.
- **Appendix D:** Cisco IOS configuration used for VLANs and ACLs – `scripts/vlan-config.txt`.
- **Appendix E:** Analysis script output – `scripts/analyse-pcap.py` log saved as `reports/analyse-pcap-output.txt`.
- **Appendix F:** Packet Tracer activity file – `network_topology.pkt` (optional).

---
*Sample report generated by the Network Traffic Analysis and Troubleshooting project.*