#!/bin/bash

#Install package
cd /tmp
wget https://repo.zabbix.com/zabbix/4.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_4.0-1%2Btrusty_all.deb >/dev/null 2>&1
dpkg -i zabbix-release_4.0-1+trusty_all.deb >/dev/null 2>&1
apt-get update >>sitedog.log 2>&1
apt-get install -y zabbix-server-pgsql zabbix-frontend-php zabbix-agent php5-pgsql >>sitedog.log 2>&1

#Config PostgreSQL
sed -i -e 's/local   all             all                                     peer/local   all             all                                     trust/g' /etc/postgresql/9.3/main/pg_hba.conf
sed -i -e 's/host    all             all             127.0.0.1\/32            md5/host    all             all             0.0.0.0\/0            trust/g' /etc/postgresql/9.3/main/pg_hba.conf
sudo -u postgres createuser zabbix >/dev/null 2>&1
sudo -u postgres createdb -O zabbix zabbix >/dev/null 2>&1
service postgresql restart >/dev/null 2>&1

#Install Zabbix
#Config zabbix-server service
zcat /usr/share/doc/zabbix-server-pgsql/create.sql.gz | psql -h 127.0.0.1 -U zabbix >>sitedog.log 2>&1
sed -i -e 's/# DBHost=localhost/DBHost=localhost/g' /etc/zabbix/zabbix_server.conf
sed -i -e 's/# DBPassword=/DBPassword=zabbix/g' /etc/zabbix/zabbix_server.conf
service zabbix-server restart >/dev/null 2>&1
#Config zabbix-web service
sed -i -e 's/;date.timezone =/date.timezone = Asiai\/Beijing/g' /etc/php5/apache2/php.ini
service apache2 restart >/dev/null 2>&1
#Config zabbix-agent service
sed -i -e 's/Server[ ]*=[ ]*[^ ]*/Server=127.0.0.1/g' /etc/zabbix/zabbix_agentd.conf
sed -i -e 's/# Hostname=/Hostname=Server2/g' /etc/zabbix/zabbix_agentd.conf
service zabbix-agent restart >/dev/null 2>&1
#Install Grafana
cd /tmp
wget https://dl.grafana.com/oss/release/grafana_6.3.0_amd64.deb >/dev/null 2>&1
dpkg -i grafana_6.3.0_amd64.deb >/dev/null 2>&1
grafana-cli plugins install alexanderzobnin-zabbix-app >>sitedog.log 2>&1
grafana-cli plugins install snuids-trafficlights-panel >>sitedog.log 2>&1
sudo service grafana-server start >/dev/null 2>&1
#Restart all services
service zabbix-server restart >/dev/null 2>&1
service zabbix-agent restart >/dev/null 2>&1
service postgresql restart >/dev/null 2>&1
service apache2 restart >/dev/null 2>&1
