echo "source s_net { tcp(ip(0.0.0.0) port(514) max-connections (5000)); udp(); };" >> /etc/syslog-ng/syslog-ng.conf
echo "log { source(s_net); destination(d_syslog); };" >> /etc/syslog-ng/syslog-ng.conf
systemctl restart syslog-ng
