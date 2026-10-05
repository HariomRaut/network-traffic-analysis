# Cisco Packet Tracer Guide – Building a VLAN‑Segmented Topology

This guide walks you through creating a simple three‑VLAN network (Faculty, Students, Servers) with inter‑VLAN routing via a router‑on‑a‑stick and applying an ACL to restrict traffic between VLANs.

## 1. Topology Overview
- **Devices:**
  - One **Cisco 2960 Switch** (or any switch that supports VLANs).
  - One **Cisco 1941 Router** (or any router with Ethernet interfaces).
  - Three **End‑User Devices** (PCs) representing Faculty, Student, and Server.
- **VLANs:**
  - VLAN 10 – Faculty (IP subnet 192.168.10.0/24)
  - VLAN 20 – Students (IP subnet 192.168.20.0/24)
  - VLAN 30 – Servers (IP subnet 192.168.30.0/24)
- **Links:**
  - Switch ↔ Router via a single Ethernet trunk (to carry multiple VLANs).
  - Switch ↔ each PC (access ports assigned to the appropriate VLAN).

## 2. Step‑by‑Step Construction

### 2.1 Place Devices
1. From the bottom‑left **Devices** toolbar, choose:
   - **Switches** → **Cisco 2960** → place in the workspace.
   - **Routers** → **Cisco 1941** → place to the right of the switch.
   - **End Devices** → **PC** → place three PCs: left (Faculty), middle (Student), right (Server).

### 2.2 Connect the Devices
1. **Connect Switch to Router:**
   - Click the **Connections** toolbar → choose **Copper Straight‑Through**.
   - Click the switch, select any free GigabitEthernet port (e.g., Gig0/1).
   - Click the router, select Gig0/0.
2. **Connect PCs to Switch:**
   - For each PC, use a Copper Straight‑Through cable.
   - Click the PC, choose the FastEthernet port.
   - Click the switch, choose an access port (e.g., Gig0/2 for Faculty PC, Gig0/3 for Student PC, Gig0/4 for Server PC).

### 2.3 Configure the Switch
1. Click the switch → **CLI** tab.
2. Enter the following commands (press Enter after each line):
   ```
   enable
   configure terminal
   ! Create VLANs
   vlan 10
   name Faculty
   exit
   vlan 20
   name Students
   exit
   vlan 30
   name Servers
   exit
   ! Assign access ports to VLANs
   interface range gig0/2 - gig0/4
   switchport mode access
   switchport access vlan 10   ! Faculty PC on Gig0/2
   exit
   interface gig0/2
   switchport access vlan 10
   exit
   interface gig0/3
   switchport access vlan 20
   exit
   interface gig0/4
   switchport access vlan 30
   exit
   ! Configure trunk port to router
   interface gig0/1
   switchport trunk encapsulation dot1q
   switchport mode trunk
   ! (Optional) restrict trunk to needed VLANs
   switchport trunk allowed vlan 10,20,30
   exit
   ! Save configuration
   end
   write memory
   ```
   > **Note:** Adjust interface names if you used different ports.

### 2.4 Configure the Router (Router‑on‑a‑Stick)
1. Click the router → **CLI** tab.
2. Enter:
   ```
   enable
   configure terminal
   ! Disable routing on the physical interface (we'll use sub‑interfaces)
   interface gig0/0
   no ip address
   exit
   ! Create sub‑interfaces for each VLAN
   interface gig0/0.10
   encapsulation dot1q 10
   ip address 192.168.10.1 255.255.255.0
   exit
   interface gig0/0.20
   encapsulation dot1q 20
   ip address 192.168.20.1 255.255.255.0
   exit
   interface gig0/0.30
   encapsulation dot1q 30
   ip address 192.168.30.1 255.255.255.0
   exit
   ! Enable routing
   ip routing
   exit
   ! (Optional) Configure a basic ACL to restrict traffic
   ! Example: Allow Students (VLAN20) to access Servers (VLAN30) only on HTTP/HTTPS
   access-list 100 permit tcp any 192.168.30.0 0.0.0.255 eq www
   access-list 100 permit tcp any 192.168.30.0 0.0.0.255 eq 443
   access-list 100 deny   ip 192.168.20.0 0.0.0.255 192.168.30.0 0.0.0.255
   access-list 100 permit ip any any   ! Allow all other traffic (adjust as needed)
   ! Apply ACL outbound on the server‑facing sub‑interface
   interface gig0/0.30
   ip access-group 100 out
   exit
   ! Save configuration
   end
   write memory
   ```

### 2.5 Configure the PCs
1. Click each PC → **Desktop** tab → **IP Configuration**.
2. Set static IP addresses (or use DHCP if you configure the router to provide it):
   - **Faculty PC:** IP 192.168.10.10, Subnet Mask 255.255.255.0, Default Gateway 192.168.10.1
   - **Student PC:** IP 192.168.20.10, Subnet Mask 255.255.255.0, Default Gateway 192.168.20.1
   - **Server PC:** IP 192.168.30.10, Subnet Mask 255.255.255.0, Default Gateway 192.168.30.1
3. Set DNS (optional): e.g., 8.8.8.8.

### 2.6 Verify Connectivity
1. From each PC’s **Desktop** → **Command Prompt**, ping the gateway and a host in another VLAN:
   - Faculty PC: `ping 192.168.10.1` (should succeed)
   - Faculty PC: `ping 192.168.20.10` (should be blocked by ACL if configured as above)
   - Student PC: `ping 192.168.30.10` (should succeed only on ports 80/443 if ACL allows)
   - Server PC: `ping 192.168.10.10` (should be blocked unless ACL permits)

### 2.7 Saving the Activity
- File → Save As → give your `.pkt` file a meaningful name (e.g., `VLAN_Segmentation.pkt`).

## 3. Extending the Design
- Add a **DHCP server** on the router and enable `ip helper-address` on switch VLAN interfaces if you prefer dynamic addressing.
- Introduce a **firewall** (e.g., ASA) between the router and the server VLAN for deeper inspection.
- Implement **802.1X** authentication on switch access ports for port‑based network access control.
- Use **SPAN (Switched Port Analyzer)** on the switch to mirror traffic to a monitoring PC running Wireshark.

## 4. Tips & Troubleshooting
- If PCs cannot ping their gateway, verify:
  - Switch port is in the correct VLAN (`show interfaces status`).
  - Trunk port is allowing the VLAN (`show interfaces trunk`).
  - Router sub‑interface has the correct encapsulation and IP address.
- If inter‑VLAN ping fails despite ACL allowing it, check:
  - ACL direction (inbound vs. outbound) matches the traffic flow.
  - The ACL is applied to the correct interface/sub‑interface.
- Use the **Simulation** mode in Packet Tracer to step through ARP and ICMP exchanges to see where packets are dropped.

## References
- Cisco Packet Tracer User Guide: https://www.netacad.com/courses/packet-tracer
- Cisco IOS Command Reference (VLANs): https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst2960xr/software/release/15-0_2_se/configuration guide/b_1502se_ex_2960xr_cfg/b_1502se_ex_2960xr_cfg_chapter_010.html
- Cisco IOS ACL Guide: https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec data acs/configuration/xe-16/sec-data-acs-xe-16-book/sec-acl.pdf
