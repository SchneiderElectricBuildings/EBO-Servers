# Schneider Electric EcoStruxure Building Operation

Open, flexible, data-centric. Go beyond traditional building management system functionality to create smart, future-ready buildings with EcoStruxure Building Operation. Part of the EcoStruxure Building integrated smart building platform; this open, flexible, data-centric solution provides a single control center to monitor, manage and optimize all types of buildings.

To learn more, see [EcoStruxure Building](https://www.se.com/ww/en/work/products/product-launch/building-management-system/)

EcoStruxure Building Operation Edge Server is subject to commercial licensing. Contact your local [Schneider Electric representative](https://www.se.com/ww/en/work/support/country-selector/distributors.jsp) for more information.
## How to use this image
For full functionality, valid and activated licenses are required. See official Building Operation documentation for more information.

To manage the containers we do provide a few docker scripts to use as is or to draw inspiration from:
[user-scripts](./user-scripts)

### Network
We recommend that you use this container with an IPvlan network. This to give the container its own IP address on the local network for simple communication with for example BACnet devices on the same network.

If you run the script, like this:
```
./create-bridged-network 192.168.1.0/24 192.168.1.1 eth0
```
It will create a network called "bridged-net".
* The first parameter is the subnet (in the example above 192.168.1.0/24) matching the subnet for the host machine.
```
#find your subnet
ip -o -f inet addr show | awk '/scope global/ {print $4}'
```
* The second parameter is the gateway (in the example above 192.168.1.1)
```
# find your gateway
ip route | grep default
# Example output:
default via 10.142.16.1 dev eth0 proto dhcp src 10.142.16.223 metric 100
# in this example the gateway is 10.142.16.1
```

* The third parameter is the name of the network interface on the host machine (in this example eth0)
```
ip ad
# Example output:
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
2: enp4s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 10:7b:44:a3:39:a1 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.251/24 brd 192.168.1.255 scope global dynamic noprefixroute enp4s0
       valid_lft 1497sec preferred_lft 1497sec
    inet6 fe80::5f24:6a3e:43cc:c39f/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
# in this example the interface is enenp4s0
```



Then you need to have a free IP address in that subnet to set as a static address for your container.

### EULA
The End-User License Agrement (EULA) must be accepted before the server can start.  
    The license terms for this product can be downloaded here: [EULA](https://ecostruxure-building-help.se.com/bms/Topics/Show.castle?id=14865)

### Start


Then to start your server:
```
./start.py --name=cs3 --version=5.0.0.1082 --ip=192.168.1.3 --accept-eula=Yes
```
You can interact with the server via your browser: https://192.168.1.3/.  
Initial user name: admin, password: admin  
The version and IP are only examples

### Upgrade
To upgrade the server, use the same parameters as for start, but with the new version.

```
./upgrade.py --name=cs3 --version=5.0.0.1090 --ip=192.168.1.3 --accept-eula=Yes
```
The version and IP are only examples
### Backup management
There are also three scripts for backup management, for more details look in the scripts:

list-backups
```
./list-backups cs3
Server 1 2022-09-09 14_12_36_5.0.0.1082.xbk
```

copy-backups
```
./copy-backups cs3 /tmp
```

restore-backup

Can be used with a backup file on the host machine or one of the backup files listed by list-backups. Options
* ConfigurationOnly
* AllData

```
# With just the name of the backup if you want to use the backup already available in the container
# note that you need to escape spaces in the backup name
./restore-backup cs3 5.0.0.82 Server\ 1\ 2022-09-09\ 14_12_36_5.0.0.1082.xbk ConfigurationOnly
# Or with a path to a backup on the host if you want to use a backup from the host
./restore-backup cs3 5.0.0.82 /home/user/Server\ 1\ 2022-09-09\ 14_12_36_5.0.0.1082.xbk ConfigurationOnly
```

## CA certificates
To install CA certificates in the container, you can either mount a host folder with your ca certificates by adding this parameter to your start.py script:
```
--ca-folder=/home/user/ca-certificates
```
Or you could build your own image on top of our image with the certificates added to: /usr/local/share/ca-certificates.
The CA certificates must have a .crt extension.
.


## In case of crash
You can enable the container to send crash dumps to Schneider Electric, by setting the kernel core pattern of the host to:
```
sudo sysctl -w kernel.core_pattern=/var/crash/%t.%e.h%h.P%P.s%s.g%g.u%u.core
```
Apport wants to set the default pattern so to persist the core pattern, you need to disable apport.
```
sudo nano /etc/default/apport
```
change to:
```
enabled=0
```
To set the core pattern at boot:
```
 sudo nano /etc/sysctl.d/99-sysctl.conf
```
at the end of this file add:
```
kernel.core_pattern = /var/crash/%t.%e.h%h.P%P.s%s.g%g.u%u.core
```

The host also need to allow crash dumps, like this, then restart the host:
```
sudo nano /etc/security/limits.conf
# add these lines at the end
* soft core unlimited
* hard core unlimited
```
The container will look for dump files in /var/crash from the core_pattern above. That folder used must be writable by other or by the user/group 60606 used by the container.
Working DNS is also a prerequisite for the container to be able to send the crash information to Schneider Electric, see below.


## DNS
If your container can't reach the dns setup on your host, for example because of VPN. There are an optional parameter to the start script:
```
--dns=<some IP for a public dns>
```

## Set server in Password Reset Mode

To set server in Password Reset Mode, run the script with name and version as arguments.



```
./password-reset-mode cs3 5.0.1.128
```

## A few useful docker commands
If you have started a server named cs1.
Show log:
```
docker logs cs1
# and to follow the log, quit with Ctrl+C
docker logs -f cs1
```
Show running containers:
```
docker ps
# also show the stopped containers
docker ps -a
```

Stop the server:
```
docker stop cs1
```
Remove the container, to be able to start it again. Database will be kept:
```
docker rm cs1
```
List volumes (databases):
```
docker volume ls
```
Remove the database to start from scratch:
```
docker volume rm cs1-db
```
If you want to play with a server without the need to talk to devices you can start it with port forwarding like this:
```
docker run -d --name=cs1 -hostname=cs1 -p 1080:80 -p 1443:443 -p14444:4444 -e NSP_ACCEPT_EULA=Yes ghcr.io/schneiderelectricbuildings/ebo-edge-server:5.0.0.1220
```
In this example you can connect to it on:
https://localhost:1443
The http-port is 1080 on the host machine.
The tcp-port is 14444 on the host machine.
It runs the example version 5.0.0.1220.
It is namned cs1.
