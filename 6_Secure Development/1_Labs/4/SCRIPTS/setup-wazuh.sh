sudo apt update && sudo apt upgrade -y

curl -sO https://packages.wazuh.com/4.14/wazuh-install.sh && sudo bash ./wazuh-install.sh -a -o

sudo tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt

sed -i "s/^deb /#deb /" /etc/apt/sources.list.d/wazuh.list
apt update