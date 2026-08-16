# Lab 6 BGP

This advanced lab will deepen your understanding of BGP by having you design and configure a multi-AS network within your own emulation environment, then extend it to connect with other students' networks.

---
## Preparation

**Your AS Numbers and Subnets**

**Student ID**: **[Your_ID]**

AS Numbers assigned to you:

- AS650[XX]1 (e.g., AS650011 for student 1)

- AS650[XX]2 (e.g., AS650012 for student 1)

- AS650[XX]3 (e.g., AS650013 for student 1)

**Loopback subnets** (/28 each):

- AS650[XX]1: 10.[XX].1.0/28 → Loopback: 10.[XX].1.1/32

- AS650[XX]2: 10.[XX].2.0/28 → Loopback: 10.[XX].2.1/32

- AS650[XX]3: 10.[XX].3.0/28 → Loopback: 10.[XX].3.1/32

**Transit networks** (/30):

- Between AS1-AS2: 172.16.[XX].0/30

- Between AS2-AS3: 172.16.[XX].4/30

- Between AS3-AS1: 172.16.[XX].8/30

----
**Example for student 5:**

AS65051: 10.5.1.0/28, Loopback: 10.5.1.1/32

AS65052: 10.5.2.0/28, Loopback: 10.5.2.1/32

AS65053: 10.5.3.0/28, Loopback: 10.5.3.1/32

Transit networks: 172.16.5.0/30, 172.16.5.4/30, 172.16.5.8/30


**Network topology**
```
        AS650[XX]1
       /           \
      /             \
  AS650[XX]2 --- AS650[XX]3
```

### Lab Tasks

**Part A: Basic Router Configuration**

Configure three routers in GNS3/EVE-NG, each representing a different AS.
For each router:

1. Configure hostname according to its AS number
2. Configure loopback interface with the assigned /32 address
3. Configure physical interfaces with appropriate IP addresses from the /30 transit networks
4. Enable routing and ensure interfaces are active



**Part B: BGP Configuration**

Configure BGP on all three routers:

1. Enable BGP routing with the correct AS number for each router
2. Set router ID to match the loopback address
3. Configure eBGP neighbors pointing to the other routers' interface IPs
4. Activate BGP for IPv4 unicast on all neighbor relationships
5. Advertise the /28 loopback subnet and the /32 loopback address via BGP network statements
6. Ensure that BGP is advertising networks that exist in the routing table


**Part C: Verification and Testing**

Perform comprehensive verification of your configuration: (Document all results with screenshots
)

1. Check BGP neighbor establishment on all routers
2. Examine the BGP table to verify route learning
3. Check the global routing table for BGP-learned routes
4. Test connectivity between all loopback interfaces
5. Perform traceroute between different ASes to verify the path taken

----
### EXTRA TASK (extra points)
**Part D: Advanced Task - Cross-Student Peering**

*If you are not in **Innopolis**, use a **VPN** to connect to each other.*

Extend your network to connect with another student:

1. Select one router from your topology to serve as the external peering point
2. Coordinate with another student to establish a cross-connection
3. Configure a new /30 subnet for the inter-student link
4. Configure a physical interface or bridge to connect via Wi-Fi/LAN
5. Establish an eBGP session between your AS and the other student's AS
6. Advertise appropriate routes to the external peer
7. Verify that routes are exchanged correctly
8. Test connectivity to the other student's networks

