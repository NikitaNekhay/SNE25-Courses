# 2 Forensic file system analysis

Name of report: CCF_LAB_2_Nikita_Niakhai
Course: Computer Forensics and Incident Response
Performed by Nikita Niakhai
Date submission: 31.03.2026
---

> This lab covers **forensic file system analysis** of a compromised Windows system image. The investigation follows forensically sound procedures and produces a report suitable for court presentation.
>
> **Case selection rule:** odd student number → **Case 1**
>
> **Student number odd #19.**

---

# Task 1 — Download the Evidence File

## ✍️ Execution

Case 1 was investigated using Virtual Machine Ubuntu 22.04 with GUI hosted on my Windows 11 laptop. VM has: 8 GB RAM, 50 GB+NVME, 3 processors.

7z archive with the image was transffered to the shared folder configured with the VM and extracted using `7z e archive.7z` command.

Then I referenced presentation with instructions to perform the lab, for checking right approach and tools.

![Figure 1.1 — Downloaded image file and integrity hash](screenshots/Screenshot_2026-03-31_194707.png)

Figure 1.1 — Downloaded image file and integrity hash

---

# Task 2 — Black Box Forensics Analysis

## 2.1 — Platform, System, and File System Identification

- I analyzed the files before mounting:

![image.png](screenshots/image.png)

Figure. `files` output on the `case1.001`

![image.png](screenshots/image_1.png)

Figure. `files` output on the `case1_1.001`

- I see `NTFS` is used, see **information metrics, numbers about memory** (sectors and tracks), hidden sector of memory
- I see bootstrap `BOOTMGR`
- I see that those files (`case1_1.001 case1.001`) look completely the same, maybe this is the copy only for us. So I pick `case1` to work with because this weights more.

![image.png](screenshots/image_2.png)

Figure. Some results from `string` on the file

- I runned strings on the file and found out that OS is windows … from Microsoft

![image.png](screenshots/image_3.png)

Figure. `fls error` on the file

- Run `fls -r`recursively to show all dirs inside the file. I
    - For some reason I got error on my image running `fls`, something happened while moving my image inside VM, so I decided to unzip the case archive again and do not move it from shared folder. Explanation of the error: tried to access a specific location on the image, but that location was empty or missing → image is incomplete / damaged
    - After right unzpip operation I got only one correct file and was able to do fls

    ![image.png](screenshots/image_4.png)

Figure. `fls`on the file

- A student suggested to use all-in-one tool calles Autopsy, so I decided to go with it.

![image.png](screenshots/image_5.png)

Figure. Downloading Autopsy

- Uploaded the image and setup case, picked some tools and options.

![image.png](screenshots/image_6.png)

Figure. Autopsy case configuration

- Mounted opened image inside Autopsy — ready to analyze.

    ![image.png](screenshots/image_7.png)

Figure. Autopsy Windows C content

- Went here to analyze system information: `Windows/System32/config/`, inside found and referenced overview on Registry hives from the presentation + explanation of DeepSeek to find information I need.
    - `SOFTWARE`

        ![Screenshot 2026-03-31 221349.png](screenshots/Screenshot_2026-03-31_221349.png)

        Figure. System OS information

    - `SYSTEM`

        ![image.png](screenshots/image_8.png)

        Figure. Hardware information

        ![image.png](screenshots/image_9.png)

        Figure. Active computer name

        - **Network adapters** Key: `CurrentControlSet\Control\Network\`
        - **Hostname:** Key: `CurrentControlSet\Control\ComputerName\ActiveComputerName`

        ![image.png](screenshots/image_10.png)

        Figure. Information about filesystem (NTFS)

- Infortmation about Windows installed on this case:
    - file system: `NTFS`
    - OS version: `Windows version and image Windows 8.1 Enterprise 64 bit`
        - Installation type `Client`
        - Registered main user `Hunter`

        ![image.png](screenshots/image_11.png)

    - This is`Windows VM`, since hardware information says only about **VM**, **VirtualBox**. System bios version is `VBOX - 1`

    ![image.png](screenshots/image_12.png)

- Used fsstat to analyze the case VM itself (Version OS, File System, Cluster and MFT sizes)

![image.png](screenshots/image_13.png)

Figure. Information about case001 image `fsstat`

---

## 2.2 — Malware Search

- Mounted the image

![image.png](screenshots/image_14.png)

Figure. Mounting image

- Search for viruses using `clamscan`
    - before I runned `freshclam` to update db of sigs and viruses.
    - `clamscan` is taking too much time to analyze since it is recursive and runs through whole disk.
    - I found some Malware viruses of types: `Nymeria-6980619-0`, `Win. Virus. Expiro-6912318-0`

![image.png](screenshots/image_15.png)

Figure. Running `clamscan` on the mounted disk, Malware scan results

---

## 2.3 — Timeline Creation and Analysis

Created a filesystem timeline usiing Timeline editor in the Autopsy. Active periods are 2013-2016 and 2016 is the most active one.  Especially june, march 2016: 02, 04, 05, 07, 11, 12 ,16, 22, 28, 29 days.

![image.png](screenshots/image_16.png)

Figure. Timeline years

![image.png](screenshots/image_17.png)

Figure. Timeline months

![image.png](screenshots/image_18.png)

Figure. Timeline days

- Then I decided to analyze the most active day of march 16.03.2016, activities:
    - a lot of `nmap`, `winpcap`
    - and some of Google browsing:

        ![image.png](screenshots/image_19.png)

![image.png](screenshots/image_20.png)

- Then I decided to analyze the most active day of June and 20th, activities:
    - Adobe files
    - Thimbs.db in Downloads
    - Windows Defender scan
    - Microsoft Office files and installation
    - Windows installer msi
    - and some of Google browsing.
    - Dropbox
    - MCaffee
    - Teamviewer
- Virtual box activites and installation on 16.06.2016.
- Skype (10.06.2016 ,15.06.2016,), CCleaner activites on 15.06.2016.

    ![image.png](screenshots/image_21.png)

- All activities done by Hunter user using google chrome.

---

## 2.4 — Windows Artefacts Analysis

### 2.4.1 — Windows Registry

- `SAM` using Autopsy + `regripper -r /mnt/windows8/Windows/System32/config/SAM -a > /media/sam.txt`

![image.png](screenshots/image_22.png)

Figure. Overall Information about users

![image.png](screenshots/image_23.png)

Figure. Information about `Hunter`

- Created on 21.01.2016 08:37:57
- Login count: 3
- Password hint: "What do you do?"

- `SOFTWARE`  `regripper -r /mnt/windows8/Windows/System32/config/SOFTWARE -a > /media/soft.txt`

- `SYSTEM regripper -r /mnt/windows8/Windows/System32/config/SYSTEM -a > /media/sys.txt`
    - Mounted devices:

        ![image.png](screenshots/image_24.png)

    - Bluetooth devices not found

        ![image.png](screenshots/image_25.png)

    - USB devices

        ![image.png](screenshots/image_26.png)

        ![image.png](screenshots/image_27.png)

        ![image.png](screenshots/image_28.png)

    - Unique MAC addresses

        ![image.png](screenshots/image_29.png)

    - DHCP address (1 adapter)

        ![image.png](screenshots/image_30.png)

        ![image.png](screenshots/image_31.png)

---

### 2.4.2 — Windows Event Logs

- Analysed `.evtx` logs: Security (4624 logons, 4625 failed, 4648, 4720), System, Application, PowerShell, and Task Scheduler logs.  That are find at `%WINDIR%\System32\winevt`contain system events.

![image.png](screenshots/image_32.png)

Figure. List of logs

---

### 2.4.3 — Personal User Data

- Examined user profile artefacts: Desktop, Downloads, Documents, Recent files (LNK), Prefetch, Shellbags, Jump Lists, and Recycle Bin.

```bash
"\$Recycle.Bin\|RECYCLER"
```

![image.png](screenshots/image_33.png)

Figure. Desktop of Hunter

![image.png](screenshots/image_34.png)

![image.png](screenshots/image_35.png)

Figure. results of nmap scan

- Installed `sqlite3` to view thumbs db and other files.
- Checked browser data and `thumbsnail db` (the one in Desktop is corrupted, found identical in the Documents folder)

![image.png](screenshots/image_36.png)

![image.png](screenshots/image_37.png)

![image.png](screenshots/image_38.png)

- Found some image with network infrastracture and hacking resoucres and conferences

![image.png](screenshots/image_39.png)

![image.png](screenshots/image_40.png)

- Found information about some accounts of the Hunter

    ![image.png](screenshots/image_41.png)

- Found some of his private files

![image.png](screenshots/image_42.png)

![image.png](screenshots/image_43.png)

- found some links to the videos (2 of them are not availavle already)

![image.png](screenshots/image_44.png)

![image.png](screenshots/image_45.png)

Figure. YouTube videos

---

### 2.4.5 — Email Artefacts

*Search for email clients (Outlook PST/OST, Thunderbird profile), webmail cache, and any email-related files. Note sender, recipient, subject, and timestamps of relevant messages.*

- found outlook backup

![image.png](screenshots/image_46.png)

- install tool to open and deal with those email

![image.png](screenshots/image_47.png)

- Viewed emails sent

![image.png](screenshots/image_48.png)

- Found network topology email

![image.png](screenshots/image_49.png)

---

### 2.4.6 — Browser Artefacts

- Also you could find data and evidence of browsing in TOR ! I read paper about it, but I was lazy to find it.
- Found log data of executing TOR browser:

    ![image.png](screenshots/image_50.png)

- Found History and Cookies: `"Users/Hunter/AppData/Local/Google/Chrome/User Data/Default/History” , "Users/Hunter/AppData/Local/Google/Chrome/User Data/Default/Cookies”`

![image.png](screenshots/image_51.png)

![image.png](screenshots/image_52.png)

![image.png](screenshots/image_53.png)

---

### 2.4.7 — Messenger Artefacts

- Skype data

    ![image.png](screenshots/image_54.png)

    - Found link to deleted 7z archive with fake porn

        ![image.png](screenshots/image_55.png)

    - found user name data

        ![image.png](screenshots/image_56.png)

    - found some data from skype chats with user`linux-rul3z`:

    ![image.png](screenshots/image_57.png)

![image.png](screenshots/image_58.png)

![image.png](screenshots/image_59.png)

![image.png](screenshots/image_60.png)

![image.png](screenshots/image_61.png)

![image.png](screenshots/image_62.png)

![image.png](screenshots/image_63.png)

- Found that user has Hotmail account `hunterehpt@hotmail….`

![image.png](screenshots/image_64.png)

---

### 2.4.9 — Other Notable Artefacts

Found TeamViewer logs:

![image.png](screenshots/image_65.png)

![image.png](screenshots/image_66.png)

---

# Task 3 — Forensic Report

CCF LAB 2 — Digital Forensic Report (Final)
