#!/bin/bash

if [ $UID != 0 ]; then
	echo "Need root permissions. Exiting."
	exit 0
fi

if ! (docker --version &>/dev/null); then
	echo "[INFO] Docker installing"
	apps="apt-transport-https ca-certificates curl software-properties-common"

	for a in $apps; do
		if ! (dpkg -s $a &>/dev/null); then
			apt install $a -y -qq &>/dev/null
		fi
	done

	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable" -y
	apt update -y
	apt-cache policy docker-ce
	apt install docker-ce -y
	docker --version
fi

if ! (docker-compose --version &>/dev/null); then
	echo "[INFO] Docker-compose installing"
	DC_VER=1.25.4
	DC_URL=https://github.com/docker/compose/releases/download
	DC_URL=$DC_URL/$DC_VER/docker-compose-$(uname -s)-$(uname -m)
	sudo curl -L $DC_URL -o /usr/local/bin/docker-compose
	if [ $? -eq 0 ]; then
		chmod +x /usr/local/bin/docker-compose
		docker-compose --version
	fi
fi

echo '[INFO] Restart Docker'
systemctl restart docker
