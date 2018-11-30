systemctl stop dnsmasq 
wpa_supplicant_manual -iwlan0 -c/etc/wpa_supplicant/wpa_supplicant.conf -B
sleep 5
dhclient wlan0

