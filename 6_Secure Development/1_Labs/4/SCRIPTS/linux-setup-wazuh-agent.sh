# Install Wazuh agent on Linux user
apt update && apt upgrade -y
#Install the following packages if missing:
apt install gnupg apt-transport-https -y

#Install the GPG key:
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg

#Add the repository:
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list

#Update the package information:
apt update

# Select your package manager and run the command below. Replace the WAZUH_MANAGER value with your Wazuh manager IP address or hostname:
WAZUH_MANAGER="192.168.30.15" apt-get install -y wazuh-agent 

# Enable and start the Wazuh agent service.
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl start wazuh-agent

