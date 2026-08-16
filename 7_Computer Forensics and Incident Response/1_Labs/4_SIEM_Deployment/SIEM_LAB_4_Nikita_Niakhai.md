# 4 SIEM Deployment for Threats Detection

Name of report: SIEM_LAB_4_Nikita_Niakhai
Course: Computer Forensics and Incident Response
Performed by Nikita Niakhai
Date submission: 19.04.2026
---

# Task 1 — Wazuh Deployment

## 1.1 Deployment Scenario

- **Chosen deployment method:**

    In this lab I used All-in-One deployment (server-wazuh components are hosted on one VM), you can divide hosting all main components server, indexer, dashboard between different VMs, containers.

- **Environment location** *(local / cloud)*:
    - Local network via VMs
- **Reason for choice:**
    - Safe, cheap, controllable, easy to deploy.

## 1.2 Lab Environment Nodes

![image.png](screenshots/image.png)

Figure — Infrastructure diagram

- **Network topology used (NAT, HOST-ONLY, INTERNAL):**

    | VM/Serice | VirtualBox adapter(s) | IP | Info |
    | --- | --- | --- | --- |
    | MikroTik CHR 7.16 | Adapter 1: Internal Network `lab-lan`, Adapter 2: NAT
    Adapter 3: **Host-Only Adapter** → `VirtualBox Host-Only Ethernet Adapter #1` (192.168.56.x) | ether1: DHCP (10.0.2.15), ether2: 192.168.30.1
    ether2: 192.168.56.2 | admin:admin |
    | Ubuntu Wazuh | Adapter 1: Internal Network `lab-lan` | 192.168.30.15 (wazuh) | ubuntu:ubuntu |
    | Linux user | Adapter 1: Internal Network `lab-lan` | 192.168.30.25 | ubuntu:ubuntu |
    | Windows | Adapter 1: Internal Network `lab-lan` | 192.168.30.35 | user:user and admin:admin |
    | Wazuh Dashboard |  |  | admin:admin |
    | Linux Honey Pot Machine | Yandex Cloud machine |  | Created for testing some separate wazuh features like log rotations |
- **Verification steps taken to confirm isolation:**

    ![mikrotik-net-setup.png](screenshots/mikrotik-net-setup.png)

Figure — Miktrotik communication setup and test via `ping`

![linux-server-net.png](screenshots/linux-server-net.png)

Figure — Linux machine `ping` test (windows, wazuh, router, nat)

![wazuh-server-net.png](screenshots/wazuh-server-net.png)

Figure — Wazuh machine `ping` test (windows,linux machine, router, nat)

![win-server-net-1.png](screenshots/win-server-net-1.png)

Figure — Windows machine setting up gateway

![win-server-net-2.png](screenshots/win-server-net-2.png)

Figure — Wazuh machine `ping` test (linux machine, wazuh, router, nat)

![image.png](screenshots/image_2.png)

Figure — Wazuh container running

![dash.png](screenshots/dash.png)

Figure — SIEM dashboard showing all connected agents/devices

- Setting up communication on infrastructure

```markdown
**#  MikroTik router configuration**

# ether1 = LAN side
/ip address add address=192.168.30.1/24 interface=ether1

# ether2 = NAT adapter (internet via VirtualBox NAT)
/ip dhcp-client add interface=ether2 disabled=no

# Enable NAT masquerade so LAN hosts reach internet
/ip firewall nat add chain=srcnat out-interface=ether2 action=masquerade

# Allow DNS relay for LAN clients
/ip dns set allow-remote-requests=yes

# Verify internet works
/ping 8.8.8.8 count=3

# This puts MikroTik on the same subnet as your Windows Host-Only adapter
/ip address add address=192.168.56.2/24 interface=ether3

# allow forwarding between ether3(With Host) and ether1 (Lan)
/ip firewall filter add chain=forward in-interface=ether3 out-interface=ether1 action=accept
/ip firewall filter add chain=forward in-interface=ether1 out-interface=ether3 action=accept

**# On host machine Windows:**
route add 192.168.30.0 mask 255.255.255.0 192.168.56.2 metric 5

**#  Ubuntu Wazuh server**

# Find your interface name
ip link show

# Set static IP via netplan
sudo tee /etc/netplan/01-static.yaml << 'EOF'
network:
  version: 2
  ethernets:
    enp0s3:
      addresses: [192.168.30.15/24]
      routes:
        - to: default
          via: 192.168.30.1
      nameservers:
        addresses: [192.168.30.1, 8.8.8.8]
EOF

sudo netplan apply

# Verify
ping -c 3 192.168.30.1    # gateway
ping -c 3 8.8.8.8       # internet
ping -c 3 google.com    # DNS

**# Linux user machine**

# Same approach, different IP
sudo tee /etc/netplan/01-static.yaml << 'EOF'
network:
  version: 2
  ethernets:
    enp0s3:
      addresses: [192.168.30.25/24]
      routes:
        - to: default
          via: 192.168.30.1
      nameservers:
        addresses: [192.168.30.1, 8.8.8.8]
EOF

sudo netplan apply
ping -c 3 192.168.30.1
ping -c 3 192.168.30.15

**# Windows VM**

# Find your adapter index
Get-NetAdapter

# Found that it is 4

# Set static IP
New-NetIPAddress -InterfaceIndex 4 -IPAddress 192.168.30.35 -PrefixLength 24 -DefaultGateway 192.168.30.1
Set-DnsClientServerAddress -InterfaceIndex 4 -ServerAddresses 192.168.30.1,8.8.8.8

# Verify
ping 192.168.30.1
ping 192.168.30.15
ping 8.8.8.8
```

Replace `InterfaceIndex 6` with the actual index from `Get-NetAdapter`.

---

## Step 6 — Verify full connectivity from every machine

Every VM should be able to reach every other VM and the internet:
```bash
ping 192.168.30.1     # MikroTik
ping 192.168.30.15    # Wazuh
ping 192.168.30.25    # Linux user
ping 192.168.30.35    # Windows
ping 8.8.8.8       # Internet
```

- Setting up basic Wazuh infrastructure

```markdown
# Install Wazuh agent on Linux user

#Install the following packages if missing:
apt-get install gnupg apt-transport-https

#Install the GPG key:
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg

#Add the repository:
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list

#Update the package information:
apt-get update

# Select your package manager and run the command below. Replace the WAZUH_MANAGER value with your Wazuh manager IP address or hostname:
WAZUH_MANAGER="192.168.30.15" apt-get install wazuh-agent

# Enable and start the Wazuh agent service.
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl start wazuh-agent

# Install Wazuh agent on Windows 

Download the Windows installer to start the installation process.
https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.4-1.msi

# run installation (Powershell)
.\wazuh-agent-4.14.4-1.msi /q WAZUH_MANAGER="192.168.30.15"

# Start  (Powershell)
Start-Service wazuhsvc

# Files are stored C:\Program Files (x86)\ossec-agent

# Send all logs to Wazuh via syslog (UDP 514)
/system logging action set remote address=192.168.30.15 remote-port=514

/system logging add topics=info action=remote
/system logging add topics=error action=remote
/system logging add topics=warning action=remote
/system logging add topics=critical action=remote
/system logging add topics=firewall action=remote
```

---

# Task 2 — Configure the SIEM

### **Configuring: MikroTik to send syslog to Wazuh Server**

- Paste the following code snippet at the bottom of the `/etc/rsyslog.conf` file on the Ubuntu endpoint. This code enables the UDP port **514** to listen for syslogs and adds a location to store the security events. Replaced `<YOUR_MIKROTIK_IP_ADDRESS>` with my IP address of the MikroTik device.

![image.png](screenshots/image_1.png)

![image.png](screenshots/image_1_2.png)

Figure — `/etc/rsyslog.conf` file with new configurations and log file is created

- Create the `mikrotik.log` file in the `/var/log` directory to store the syslog events.
- Change the file ownership for the `/var/log/mikrotik.log` file to syslog and group to `adm`.
- Restart the rsyslog utility for the changes to take effect.

    ![image.png](screenshots/image_3.png)

- Install WinBox on my host machine and connect to edit Mikrotik configurations.
    - SW already found to which endpoint to connect

![image.png](screenshots/image_6.png)

Figure — WinBox logginig to mikrotik router

- Open Logging tab

![image.png](screenshots/image_7.png)

Figure — Inside mikrotik configuration for allowing forwarding to remote node

- Click on the **System** > **Logging** > **Rules** tab and create new or modify the existing rules where the topic’s **error**, **info**, and **warning** are set to `remote`.

![image.png](screenshots/image_8.png)

Figure — Changing rules to remote

![image.png](screenshots/image_9.png)

Figure — All rules are changed to remote

- Click the **System** > **Logging** > **Actions** tab to edit the **remote** action. Set the **Remote address** field to the IP address of the Wazuh manager and the **Remote port** field to the Rsyslog listening port.

![image.png](screenshots/image_10.png)

Figure — configuring remote action to actually point to my Wazuh Server

---

### **Configuring: ossec**

- On the Wazuh server, edit `/var/ossec/etc/ossec.conf` and add inside the `<ossec_config>` block:
    - `allowed-ips` specifies which endpoints are allowed to send logs to this server. Replace `<CIDR_NOTATION>` with the CIDR address of the network on which your endpoints are. If you monitor just one endpoint, you can put its IP address.
    - `local-ip` specifies the local IP address of the Wazuh server to be used for this connection. Replace `<WAZUH_MANAGER_IP>` with the IP address of the Wazuh server.

    ```
    <remote>
      <connection>syslog</connection>
      <port>514</port>
      <protocol>udp</protocol>
      <allowed-ips>192.168.30.1</allowed-ips>
      <local_ip>192.168.30.15</local_ip>
    </remote>
    ```

![image.png](screenshots/image_4.png)

Figure — `/var/ossec/etc/ossec.conf` new block is added

---

- Setup mikrotik to allow WinBox UI

![image.png](screenshots/image_5.png)

---

### **Configuring: decoders and rules**

- Setting up Wazuh Decoders from [documentation](https://wazuh.com/blog/monitoring-network-devices/).
- Wrote 2 files, send them to wazuh server
- Restart `sudo systemctl restart wazuh-manager`
- Content of the files:

`/var/ossec/etc/decoders/mikrotik_decoders.xml`

```
<decoder name="mikrotik">
  <prematch>^RouterOS7.1-logs: </prematch>
</decoder>

<decoder name="mikrotik1">
  <parent>mikrotik</parent>
  <regex type="pcre2">\S+ (\w+ \d+ \d+:\d+:\d+) MikroTik user (\S+) (.*?) from (\d+.\d+.\d+.\d+) via (\w+)</regex>
  <order>logtimestamp, logged_user, action, ip_address, protocol</order>
</decoder>

<decoder name="mikrotik1">
  <parent>mikrotik</parent>
  <regex type="pcre2">\S+ (\w+ \d+ \d+:\d+:\d+) MikroTik dhcp-client on (\S+) (.*?) address (\d+.\d+.\d+.\d+)</regex>
  <order>logtimestamp, interface, action, ip_address</order>
</decoder>

<decoder name="mikrotik1">
  <parent>mikrotik</parent>
  <regex type="pcre2">\S+ (\w+ \d+ \d+:\d+:\d+) MikroTik router (\S+)</regex>
  <order>logtimestamp, action</order>
</decoder>
```

`var/ossec/etc/rules/mikrotik_rules.xml`

```
<group name="Mikrotik,">

  <rule id="110000" level="0">
    <decoded_as>mikrotik</decoded_as>
    <description>Mikrotik-Event</description>
  </rule>

  <rule id="110001" level="5">
    <if_sid>110000</if_sid>
    <match>dhcp-client on ether</match>
    <description>MikroTik dhcp-client received an IP address $(ip_address)</description>
  </rule>

  <rule id="110002" level="5">
    <if_sid>110000</if_sid>
    <match>rebooted</match>
    <description>MikroTik router rebooted</description>
  </rule>

  <rule id="110003" level="5">
    <if_sid>110000</if_sid>
    <match>logged out from</match>
    <description>MikroTik user logged out via $(protocol)</description>
  </rule>

  <rule id="110004" level="5">
    <if_sid>110000</if_sid>
    <match>logged in from</match>
    <description>MikroTik user logged in from $(ip_address) via $(protocol)</description>
  </rule>

</group>
```

![image.png](screenshots/image_11.png)

Figure — Copying created rules and decoders files to wazuh server

- Custom Rules and Decoders are seen in the dashboard, after the reboot of wazuh-manager.

![image.png](screenshots/image_12.png)

Figure — Verifying that custom rules are seen and applied in the SIEM architecture

![image.png](screenshots/image_13.png)

Figure — Verifying that custom decoders are seen and applied in the SIEM architecture

---

### **Configuring: verifying**

![Figure — SIEM dashboard showing all connected agents/devices](screenshots/dash.png)

Figure — SIEM dashboard showing all connected agents/devices

![Figure — Log data visible from Device 2 (e.g. Windows)](screenshots/windows.png)

Figure — Log data visible from Device 2 (e.g. Windows)

![waz-miktorik-after.png](screenshots/waz-miktorik-after.png)

Figure — Log data visible from Device 3 (e.g. Network device)

---

## 2.2 Features Enabled for Testing

- **Feature 1 (**CVE detection and remediation**):**
    - `ossec` configurations for  **Vulnerability detection, time scanning**
    - Filebeat configuration
    - CVE vulnerable package
- **Feature 2 (**Malware detection by SIEM**):**
    - YARA integration: YARA detection rules and decoders, profiles (default and community sets), YARA Active Response scan (sh script)
    - `ossec` configuration connecting YARA to wazuh
    - Malware samle
- **Feature 3 (**Brute-force attack simulation with attacker user blocking**):**
    - SIEM rule triggering for brute force (Wazuh rule 5551, 5712, etc.)
    - `hydra` on attacker

---

# Task 3 — SIEM in Action

## 3.1 Feature 1 — CVE detection and remediation

- Performed the following steps on the Wazuh server to confirm that the Wazuh Vulnerability Detection module is enabled and properly configured.
    - Check Vulnerability detection is enabled in Wazuh configuration `/var/ossec/etc/ossec.conf`

    ![image.png](screenshots/image_17.png)

    Figure — `/var/ossec/etc/ossec.conf`

    - Check for host ip addres and certificates match the ones inside`filebeat.yml`

    ![image.png](screenshots/image_18.png)

    Figure — `/var/ossec/etc/ossec.conf`

    ![image.png](screenshots/image_19.png)

    ![image.png](screenshots/image_20.png)

    Figure — `/etc/filebeat/filebeat.yml`

- reduced time for scanning for vulnerabilities to 7 minutes
 in the `/var/ossec/etc/ossec.conf` file on the Wazuh agent

    ![image.png](screenshots/image_21.png)

    ![image.png](screenshots/image_22.png)

    Figures — changing interval on Wazuh Agent configuration

- Go to <https://192.168.30.15/app/vulnerability-detection> and open tab Inventory too look at Vulnerable detections
    - filtered them on my agent name
- Found 3 critical CVEs with `linux-image-6.8.0-106-generic`

![image.png](screenshots/image_23.png)

Figures — 3 critical CVEs

- Removing this package

![image.png](screenshots/image_24.png)

Figures — removing critical package

![Figure — Remediation applied on Device 3](screenshots/resolved.png)

Figure — Remediation applied on Device 3

![Figure  — Updated scan showing vulnerability resolved on all devices](screenshots/Screenshot_2026-03-24_165141.png)

Figure  — Updated scan showing vulnerability resolved on all devices

- Then to properly show how vulnerability would like when it is installed on running node, I decided to install this one package and check.

![image.png](screenshots/image_25.png)

Figure — Installing vulnerable package (image)

- Now inside tab `Events` I can observe such vulnerable packet, that actualyy causes a lot of CVEs of different severity.

![image.png](screenshots/image_2_2.png)

Figure — Events tab with targeted package

- Then I again uninstall it and was waiting to agent run again.

![image.png](screenshots/image_27.png)

Figure — vulnerable image is uninstalled

- Event now is Resolved:

![image.png](screenshots/image_3_2.png)

Figure — resolved status on all events with this package

---

## 3.2 Feature 2 — Malware detection by SIEM (WhisperGate Detection with YARA)

### Configuring linux-machine with agent

- Install on linux-machine YARA

```bash
sudo apt update
sudo apt install -y make gcc autoconf libtool libssl-dev pkg-config
sudo curl -LO https://github.com/VirusTotal/yara/archive/v4.5.5.tar.gz
sudo tar -xvzf v4.5.5.tar.gz -C /usr/local/bin/ && rm -f v4.5.5.tar.gz
cd /usr/local/bin/yara-4.5.5/
sudo ./bootstrap.sh && sudo ./configure && sudo make && sudo make install && sudo make check
```

- Test that YARA is running

![image.png](screenshots/image_29.png)

- Download YARA detection rules:

```bash
sudo mkdir -p /tmp/yara/rules
sudo curl 'https://valhalla.nextron-systems.com/api/v1/get' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.5' --compressed -H 'Referer: https://valhalla.nextron-systems.com/' -H 'Content-Type: application/x-www-form-urlencoded' -H 'DNT: 1' -H 'Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' --data 'demo=demo&apikey=1111111111111111111111111111111111111111111111111111111111111111&format=text' -o /tmp/yara/rules/yara_rules.yar
```

- Added more rules specifically for whispergate malware.
Download detection rules to `/tmp/yara/rules`. Rules are downloaded from this [link](https://github.com/cado-security/DFIR_Resources_Whispergate/blob/main/YARA/WhisperGate.yara).

    ```
    rule Whispergate_Stage_1 {
        meta:
          description = "Detects first stage payload from WhisperGate"
          author = "mmuir@cadosecurity.com"
          date = "2022-01-17"
          license = "Apache License 2.0"
          hash = "a196c6b8ffcb97ffb276d04f354696e2391311db3841ae16c8c9f56f36a38e92"
        strings:
          $a = { 31 41 56 4E 4D 36 38 67 6A 36 50 47 50 46 63 4A 75 66 74 4B 41 54 61 34 57 4C 6E 7A 67 38 66 70 66 76 }
          $b = { 38 42 45 44 43 34 31 31 30 31 32 41 33 33 42 41 33 34 46 34 39 31 33 30 44 30 46 31 38 36 39 39 33 43 36 41 33 32 44 41 44 38 39 37 36 46 36 41 35 44 38 32 43 31 45 44 32 33 30 35 34 43 30 35 37 45 43 45 44 35 34 39 36 46 36 35 }
          $c = { 24 31 30 6B 20 76 69 61 20 62 69 74 63 6F 69 6E 20 77 61 6C 6C 65 74 }
          $d = { 74 6F 78 20 49 44 }
        condition:
          uint16(0) == 0x5A4D and all of them
    }

    rule Whispergate_Stage_2 {
        meta:
          description = "Detects second stage payload from WhisperGate"
          author = "mmuir@cadosecurity.com"
          date = "2022-01-17"
          license = "Apache License 2.0"
          hash = "dcbbae5a1c61dbbbb7dcd6dc5dd1eb1169f5329958d38b58c3fd9384081c9b78"
        strings:
          $a = { 6D 5F 49 6E 74 65 72 63 65 70 74 6F 72 }
          $b = { 6D 5F 62 31 36 65 37 33 65 30 64 61 61 63 34 62 34 33 62 36 35 36 36 39 30 31 62 35 34 32 34 63 35 33 }
          $c = { 6D 5F 34 33 37 37 33 32 63 65 65 35 66 35 34 64 37 64 38 34 61 64 64 37 62 64 33 30 39 37 64 33 63 61 }
          $d = { 6D 5F 30 64 62 39 37 30 38 63 66 36 34 39 34 30 38 32 39 66 39 61 66 38 37 65 64 65 65 64 66 36 30 65 }
          $e = { 6D 5F 65 31 34 33 33 31 36 38 32 30 62 31 34 64 30 33 38 38 61 37 32 37 34 34 33 38 65 63 30 37 38 64 }
          $f = { 6D 5F 66 33 31 30 39 30 63 37 31 35 64 65 34 62 30 62 61 62 64 33 31 61 36 33 34 31 31 30 34 36 63 38 }
          $g = { 6D 5F 36 31 31 64 31 61 62 63 33 32 66 63 34 66 64 38 61 33 34 65 30 34 34 66 39 37 33 34 34 31 64 61 }
          $h = { 6D 5F 37 37 34 62 39 32 31 30 64 39 38 31 34 32 65 62 62 34 34 31 33 35 35 39 64 61 61 65 35 61 34 34 }
        condition:
          uint16(0) == 0x5A4D and all of them
    }
    ```

- Create a `yara.sh` script in the `/var/ossec/active-response/bin/` directory. This is necessary for the Wazuh-YARA Active Response scan

    ```
    #!/bin/bash
    # Wazuh - Yara active response
    # Copyright (C) 2015-2022, Wazuh Inc.
    #
    # This program is free software; you can redistribute it
    # and/or modify it under the terms of the GNU General Public
    # License (version 2) as published by the FSF - Free Software
    # Foundation.

    #------------------------- Gather parameters -------------------------#

    # Extra arguments
    read INPUT_JSON
    YARA_PATH=$(echo $INPUT_JSON | jq -r .parameters.extra_args[1])
    YARA_RULES=$(echo $INPUT_JSON | jq -r .parameters.extra_args[3])
    FILENAME=$(echo $INPUT_JSON | jq -r .parameters.alert.syscheck.path)

    # Set LOG_FILE path
    LOG_FILE="logs/active-responses.log"

    size=0
    actual_size=$(stat -c %s ${FILENAME})
    while [ ${size} -ne ${actual_size} ]; do
        sleep 1
        size=${actual_size}
        actual_size=$(stat -c %s ${FILENAME})
    done

    #----------------------- Analyze parameters -----------------------#

    if [[ ! $YARA_PATH ]] || [[ ! $YARA_RULES ]]
    then
        echo "wazuh-yara: ERROR - Yara active response error. Yara path and rules parameters are mandatory." >> ${LOG_FILE}
        exit 1
    fi

    #------------------------- Main workflow --------------------------#

    # Execute Yara scan on the specified filename
    yara_output="$("${YARA_PATH}"/yara -w -r "$YARA_RULES" "$FILENAME")"

    if [[ $yara_output != "" ]]
    then
        # Iterate every detected rule and append it to the LOG_FILE
        while read -r line; do
            echo "wazuh-yara: INFO - Scan result: $line" >> ${LOG_FILE}
        done <<< "$yara_output"
    fi

    exit 0;
    ```

![image.png](screenshots/image_30.png)

- Change `yara.sh` file owner to `root:wazuh` and file permissions to `0750`:

![image.png](screenshots/image_31.png)

- Add the following within the `<syscheck>` block of the Wazuh agent `/var/ossec/etc/ossec.conf` configuration file to monitor the  directory

![image.png](screenshots/image_32.png)

- Restart the Wazuh agent

---

### Configuring Wazuh server

- Add the following rules to the `/var/ossec/etc/rules/local_rules.xml`
 file. The rules detect FIM events in the monitored directory. They also
 alert when the YARA integration finds malware. You can modify the rules
 to detect events from other directories:
    - Copied prev version, then added new groups and copied back

    ```
    <group name="syscheck,">
      <rule id="100300" level="7">
        <if_sid>550</if_sid>
        <field name="file">/tmp/yara/malware/</field>
        <description>File modified in /tmp/yara/malware/ directory.</description>
      </rule>
      <rule id="100301" level="7">
        <if_sid>554</if_sid>
        <field name="file">/tmp/yara/malware/</field>
        <description>File added to /tmp/yara/malware/ directory.</description>
      </rule>
    </group>

    <group name="yara,">
      <rule id="108000" level="0">
        <decoded_as>yara_decoder</decoded_as>
        <description>Yara grouping rule</description>
      </rule>
      <rule id="108001" level="12">
        <if_sid>108000</if_sid>
        <match>wazuh-yara: INFO - Scan result: </match>
        <description>File "$(yara_scanned_file)" is a positive match. Yara rule: $(yara_rule)</description>
      </rule>
    </group>
    ```

    ![image.png](screenshots/image_34.png)

- Add decoders to local `var/ossec/etc/decoders/local_decoder.xml`, so that YARA stuff will be decoded properly
    - Copied prev version, then added new groups and copied back

    ```
    <decoder name="yara_decoder">
      <prematch>wazuh-yara:</prematch>
    </decoder>

    <decoder name="yara_decoder1">
      <parent>yara_decoder</parent>
      <regex>wazuh-yara: (\S+) - Scan result: (\S+) (\S+)</regex>
      <order>log_type, yara_rule, yara_scanned_file</order>
    </decoder>
    ```

    ![image.png](screenshots/image_35.png)

- Add the following configuration to the Wazuh server `/var/ossec/etc/ossec.conf` configuration file. This configures the Active Response module to trigger after the rule 100300 and 100301 are fired:
    - Copied prev version, then added new groups and copied back

    ```
    <ossec_config>
      <command>
        <name>yara_linux</name>
        <executable>yara.sh</executable>
        <extra_args>-yara_path /usr/local/bin -yara_rules /tmp/yara/rules/yara_rules.yar</extra_args>
        <timeout_allowed>no</timeout_allowed>
      </command>

      <active-response>
        <disabled>no</disabled>
        <command>yara_linux</command>
        <location>local</location>
        <rules_id>100300,100301</rules_id>
      </active-response>
    </ossec_config>
    ```

    ![image.png](screenshots/image_36.png)

- Restart the Wazuh manager to apply the configuration changes:

    ![image.png](screenshots/8aea8535-9100-4fee-97a6-c967438017dd.png)

![image.png](screenshots/image_38.png)

Figure — YARA integration configured in SIEM (Rules)

![image.png](screenshots/image_39.png)

Figure — YARA integration configured in SIEM (Rules)

### Installing malware and attacking myself with it

- Now I downloaded malware sample and placed inside`/tmp/yara/malware`

![image.png](screenshots/image_40.png)

```bash
git clone https://github.com/cado-security/DFIR_Resources_Whispergate
cd DFIR_Resources_Whispergate/Samples
unzip -P "infected" a196c6b8ffcb97ffb276d04f354696e2391311db3841ae16c8c9f56f36a38e92.zip
mv a1* /tmp/yara/malware/sus
```

![image.png](screenshots/image_41.png)

![malware.png](screenshots/malware.png)

Figure — WhisperGate sample detected (no execution)

---

## 3.3 Feature 3 — Brute-force attack simulation with attacker user blocking

- For simulating a brute force attack I used hydra
- I initiated the attack on the “Trudy” machine
- Then inside Wazuh dashboard I opened Threat Hunting section and observed remains of unsuccessful acces to my victim machine

```bash
# Example: simulate SSH brute force with Hydra
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://<target-ip> -t 4

# Check SIEM rule triggering for brute force (Wazuh rule 5551, 5712, etc.)
```

![image.png](screenshots/97d36842-21b5-41dc-bc4f-82c0eb33649f.png)

![Figure — Brute force attack launched from attacker machine](screenshots/b163aaa6-32e7-4a5f-9545-20d70365ff67.png)

Figure — Brute force attack launched from attacker machine

![sshd found.png](screenshots/sshd_found.png)

Figure — SIEM alert: brute force detected on Device 1

![image.png](screenshots/image_4_2.png)

![sshdf2.png](screenshots/sshdf2.png)

Figure — SIEM alert: brute force detected on Device 1

---

# Task 4 — Log Management

## 4.1 Log Rotation Setup

Log rotation policy is a system manages logs, alerts, events: defines how long will this data stay in states of live/active/deleted/archived.

Linux has built-in tool for log rotation `logrotate`, providing 2 strategies of how to log rotate:

1. Time-based: delete older then `x` days
2. Size-based: delete based on size and quantity.

This is basic configuration:

![image.png](screenshots/image_5_2.png)

Figure. log config examples

- Explanation of commands:

```markdown
    **daily**               # Rotate logs every day
    **missingok**           # Ignore if logs are missing
    **rotate 14**           # Keep 14 days of logs
    **compress**            # Compress old logs (saves space)
    **delaycompress**       # Wait until next rotation to compress
    **notifempty**          # Skip rotation if log is empty
    **create 640 root adm** # Set permissions on new log files
    **sharedscripts**       # Run post-rotation script once
```

---

### Enabling wazuh for log rotations

- I followed this [guide](https://serverfault.com/questions/1153188/how-can-i-configure-all-in-one-wazuh-for-log-retention) on setting up log rotation for my machine.
    - Created file `/etc/logrotate.d/` and put inside:

    ```markdown
    /var/ossec/logs/alerts.log {
        daily
        rotate 40
        compress
        delaycompress
        missingok
        notifempty
        create 0640 root root
        sharedscripts
        postrotate
            /var/ossec/bin/ossec-logtest -i
            /var/ossec/bin/ossec-control restart
        endscript
    }
    ```

- Enabling wazuh archives, inside `/var/ossec/etc/ossec.conf`

    ```markdown
    <ossec_config>
      <global>
        <jsonout_output>yes</jsonout_output>
        <alerts_log>yes</alerts_log>
        <logall>yes</logall>
        <logall_json>yes</logall_json>
        ...
    </ossec_config>
    ```

- Setting up manual time based policy inside `/var/ossec/etc/local_internal_options.conf`

![image.png](screenshots/image_6_2.png)

Figure. manual time based policy configuration

![image.png](screenshots/image_7_2.png)

Figure. logs on wazuh-manager on my another machine (not this lab)

- Wazuh stores logs by default on the wazuh-server instead of each agent.
- Wazuh stores logs inside a few possible places. They are retained for 31 days by default
    - /var/ossec/logs/*
    - /var/ossec/logs/alerts/ — alerts
    - /var/ossec/logs/archives/ — for archived ones/
    - Main place for logs is inside wazuh-manager files json and log format: `/var/ossec/logs/alerts/alerts.log` `/var/ossec/logs/alerts/alerts.json`

![image.png](screenshots/image_8_2.png)

Figure. examples of logs and folder tree of archives logs on my another machine (not this lab)

- The current `alerts.log` and `json` file is hardlinked to the rotated one. Upon rotation tomorrow, a fresh `alerts.log` will be linked to `2026/Apr/ossec-alerts-19.log`  and so on.

![image.png](screenshots/image_9_2.png)

---

### Indices retention policy in Wazuh

Indices is a low-level storage type format for storing logs and alerts by Wazuh Indexer, provides fast retrieval and access via API or query language like from Kibana and Discovery section of Wazuh.

Indices are not human readable as plain-text or JSON logs.

Wazuh Indexer ingests logs, parses them and then stores them in indices.

- Opening wazuh section:
    - Indexer management → Index Management → State Management Policies → Create Policy

        ![image.png](screenshots/image_10_2.png)

        ![image.png](screenshots/image_11_2.png)

    - Added ISM template for `wazuh-alerts-*` events

    ![image.png](screenshots/image_12_2.png)

    - Created an `initial` state (no action) and a `delete_alerts` state (action = `Delete`).

    ![image.png](screenshots/image_13_2.png)

    - Configured the transition from `initial` to `delete_alerts` when the condition `Minimum index age` is `80d`. Should look like this at the end.

    ![image.png](screenshots/image_14.png)

- Applied policy and checked for my JSON result

![image.png](screenshots/image_15.png)

Figure. Created policy state

![image.png](screenshots/image_16.png)

```markdown
{
    "id": "wazuh-alert-retention-policy",
    "seqNo": 0,
    "primaryTerm": 1,
    "policy": {
        "policy_id": "wazuh-alert-retention-policy",
        "description": "A sample description of the policy",
        "last_updated_time": 1776594733135,
        "schema_version": 21,
        "error_notification": null,
        "default_state": "initial",
        "states": [
            {
                "name": "initial",
                "actions": [],
                "transitions": [
                    {
                        "state_name": "delete_alerts",
                        "conditions": {
                            "min_index_age": "80d"
                        }
                    }
                ]
            },
            {
                "name": "delete_alerts",
                "actions": [
                    {
                        "retry": {
                            "count": 3,
                            "backoff": "exponential",
                            "delay": "1m"
                        },
                        "delete": {}
                    }
                ],
                "transitions": []
            }
        ],
        "ism_template": [
            {
                "index_patterns": [
                    "wazuh-alerts-*"
                ],
                "priority": 1,
                "last_updated_time": 1776594733135
            }
        ]
    }
}
```

---

# References

1. Install Mikrotik chr on Virtual box [[image vdi](https://www.mikrotik-software.de/download.mikrotik.com/routeros/7.16.1/chr-7.16.1.vdi.zip)] [[guide](https://help.mikrotik.com/docs/spaces/ROS/pages/262864931/CHR+installing+on+VirtualBox)].
2. Windows QEMU has VNC console type and Windows 7 w/ IE10. Default credentials: IEUser / Passw0rd!
3. Windows 11 installation from GNS3: <https://www.gns3.com/marketplace/appliances/windows-11-dev-env>
4. Official: <https://www.microsoft.com/ru-ru/software-download>

> **Fix - To Continue Enter An Admin Username And Password In Windows 11/ 10 || 'Yes' Button Missing**
>
> [Fix - To Continue Enter An Admin Username And Password In Windows 11/ 10 || 'Yes' Button Missing](https://www.youtube.com/watch?v=_fMYBwWJ2P4)
