#!/bin/bash

echo $1 | wpa_passphrase $2 | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null
wpa_cli -i wlan0 reconfigure