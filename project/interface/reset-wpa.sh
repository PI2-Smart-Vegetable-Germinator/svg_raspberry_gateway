#!/bin/bash

sudo cp /etc/wpa_supplicant/wpa_supplicant.conf.backup /etc/wpa_supplicant/wpa_supplicant.conf
wpa_cli -i wlan0 reconfigure