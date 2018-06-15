sudo ifconfig enx000000002622 10.0.0.1/16
sudo iptables -A FORWARD -o bnep0 -i enx000000002622 -s 10.0.0.0/16 -m conntrack --ctstate NEW -j ACCEPT
sudo iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -t nat -F POSTROUTING
sudo iptables -t nat -A POSTROUTING -o bnep0 -j MASQUERADE
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

#sudo iptables-save | tee ./iptables.save
#sudo iptable-restore < iptables.save


