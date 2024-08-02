# Prerequisites


[TOC]


## Native build

The following tools must be installed for a Yocto build to work on a Ubuntu host:
```
sudo apt install \
    build-essential \
    chrpath \
    cpio \
    debianutils \
    diffstat \
    gawk \
    gcc \
    git \
    iputils-ping \
    libegl1-mesa \
    liblz4-tool \
    libsdl1.2-dev \
    lz4
    mesa-common-dev \
    pylint \
    python3 \
    python3-git \
    python3-jinja2 \
    python3-pexpect \
    python3-pip \
    python3-subunit \
    socat \
    texinfo \
    unzip \
    wget \
    xterm \
    xz-utils \
    zstd
```

## UART

To establish the UART via USB without superuser rights, the user must be a member
of the groups `plugdev` and `dialout`.
```
sudo usermod -a -G dialout <YOUR_USERNAME>
sudo usermod -a -G plugdev <YOUR_USERNAME>
```

You can connect to UART via any serial terminal program; we recommend `tio`.
```
tio /dev/ttyUSB0
```

UART assignment:
- `/dev/ttyUSB0`: Alcatraz
- `/dev/ttyUSB1`: APU
- `/dev/ttyUSB2`: Board Controller
- `/dev/ttyUSB3`: NOT USED


## Ethernet

We recommend to establish a direct connection between host PC and development
board, using an own ethernet interface.  It shall be configured statically
according to the setup the development board expects.  The following notes work
for Ubuntu 22.04.

- Create the configuration file:
```
sudo touch /etc/netplan/01-config-static-interface.yaml
```

- Add the following content (adapt name and maybe IP address, do not use tabs!):
```
network:
    ethernets:
        eno2:
            dhcp4: no
            dhcp6: no
            ignore-carrier: true
            optional: true
            addresses:
                - 192.168.1.1/24
    version: 2
```

- Generate a new systemd config file based on the yaml file above.
    - File `01-xxx` will override the default `00-installer-config.yaml`
    - Systemd config files are located under `/run/systemd/network/`
```
sudo netplan generate
```

- Establish the generated configuration:
```
sudo netplan apply
```


## TFTP/NFS

To use TFTP and NFS during development the tools mentioned below have to be installed.

The path and server IP address for TFTP and NFS are configured in the u-boot
environment. The default values are defined in
`repos/meta-zukimo/recipes-bsp/u-boot/files/zukimo.h`

By default the following configuration will be used:
* `ipaddr=192.168.1.2`
* `serverip=192.168.1.1`
* `rootpath=/export/zukimo-rfs` (for NFS, path on server)
* `tftp_path=zukimo/` (for TFTP, relative to server directory `/srv/tftp/`)


### TFTP server

```
sudo apt install tftpd-hpa -y
sudo apt install tftp-hpa -y
sudo vi /etc/default/tftpd-hpa
    TFTP_OPTIONS="--secure --create"
sudo service tftpd-hpa restart
sudo mkdir -p /srv/tftp/zukimo
sudo chmod -R 777 /srv/tftp
```

Test:
```
touch /srv/tftp/test

tftp 192.168.xxx
    tftp> get test
    tftp> quit

ls test -lh
```

### NFS server

```
sudo apt install nfs-kernel-server
sudo apt install rpcbind
sudo vi /etc/exports
    /export/zukimo-rfs *(rw,async,no_root_squash,no_subtree_check)
sudo mkdir -p /export/zukimo-rfs
sudo exportfs -a
sudo service nfs-kernel-server restart
```

Test:
```
showmount -e localhost
```


