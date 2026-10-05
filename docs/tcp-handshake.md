# TCP Three‑Way Handshake – Illustrated Explanation

The TCP three‑way handshake is the process by which two endpoints (client and server) establish a reliable TCP connection before data exchange begins. It synchronizes sequence numbers and acknowledges willingness to communicate.

## 1. Diagram Overview
```
Client                            Server
  |--- SYN (Seq = X) ------------->|
  |                                |
  |<--- SYN‑ACK (Seq = Y, Ack = X+1)---|
  |                                |
  |--- ACK (Seq = X+1, Ack = Y+1) -->|
  |                                |
  |<---------------- DATA ------------------->|
```
*(Seq = Sequence Number, Ack = Acknowledgement Number)*

## 2. Step‑by‑Step

| Step | Action | Details |
|------|--------|---------|
| **1** | **Client → Server: SYN** | The client sends a TCP segment with the SYN flag set. It chooses an initial sequence number (ISN), denoted **X**. No data is carried in this segment. |
| **2** | **Server → Client: SYN‑ACK** | The server responds with a segment that has both SYN and ACK flags set.<br>– Its own ISN is **Y** (the SYN part).<br>– It acknowledges the client’s SYN by setting the Acknowledgement Number to **X+1** (the next expected byte). |
| **3** | **Client → Server: ACK** | The client sends an ACK segment.<br>– Its sequence number is now **X+1** (since it has consumed the server’s SYN).<br>– It acknowledges the server’s SYN by setting Ack to **Y+1**.<br>At this point, both sides have agreed on sequence numbers and the connection is in the **ESTABLISHED** state. |

## 3. Why Three Steps?
- **SYN** from the client tells the server, “I want to talk; here’s my starting sequence number.”
- **SYN‑ACK** from the server does two things simultaneously: it agrees to the connection (SYN) and confirms it received the client’s sequence number (ACK).
- **ACK** from the client completes the exchange by confirming it received the server’s sequence number. Without this final ACK, the server would not know whether the client received its SYN‑ACK.

## 4. Sequence Number Usage
- After the handshake, data transmission begins.
- Each byte of data is assigned a sequence number; the receiver acknowledges receipt by sending an ACK with the next expected sequence number.
- This mechanism enables **reliable, in‑order delivery** and allows detection of lost or duplicated packets.

## 5. Common Variations & Related Concepts
| Concept | Description |
|---------|-------------|
| **TCP Half‑Open (SYN Flood) Attack** | Attacker sends many SYN packets but never completes the handshake, consuming server resources. Mitigation: SYN cookies, increased backlog, rate limiting. |
| **TCP Reset (RST)** | Either side can abort the connection abruptly by sending a segment with the RST flag set. |
| **TCP FIN – Graceful Closure** | To close a connection, each side sends a FIN segment, which is acknowledged by the other party. This results in a four‑segment exchange (FIN‑ACK, FIN‑ACK). |
| **Wireshark Display Filter for Handshake** | `tcp.flags.syn == 1 and tcp.flags.ack == 0` – shows SYN only.<br>`tcp.flags.syn == 1 and tcp.flags.ack == 1` – shows SYN‑ACK.<br>`tcp.flags.ack == 1 and tcp.flags.syn == 0` – shows ACK (pure ACK after handshake). |
| **Typical Values in a Capture** | In a trace, you’ll see the three packets in quick succession (usually within a few milliseconds). The sequence numbers will appear random (due to OS ISN generation). |

## 6. Practical Exercise in Wireshark
1. Start a capture on the interface that will carry the TCP connection.
2. Initiate a simple TCP connection, e.g., `telnet <host> 23` or `curl http://<host>/`.
3. Stop the capture after the connection is established.
4. Apply display filter: `tcp.flags.syn == 1 or tcp.flags.ack == 1`.
5. You should see exactly three packets (or more if retransmissions occur). Use the packet details pane to inspect the Sequence and Acknowledgement Numbers.
6. Right‑click the first SYN → “Follow” → “TCP Stream” to view the entire conversation, confirming that the handshake appears at the start.

## 7. References
- TCP/IP Illustrated, Volume 1: The Protocols – W. Richard Stevens (Chapter 2 on TCP connection establishment).
- RFC 793 – Transmission Control Protocol (Section 3.4: Establishing a connection).
- Wireshark Wiki – TCP Handshake: https://www.wireshark.org/docs/wsug_html_chunked/ChapterAdvTcp.html#tcp.handshake
