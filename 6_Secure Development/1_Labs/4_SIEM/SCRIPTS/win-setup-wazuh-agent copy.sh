# Install Wazuh agent on Windows 

Download the Windows installer to start the installation process.
https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.4-1.msi

# run installation (Powershell)
.\wazuh-agent-4.14.4-1.msi /q WAZUH_MANAGER="10.0.0.2"

# Start  (Powershell)
Start-Service wazuhsvc

# Files are stored C:\Program Files (x86)\ossec-agent