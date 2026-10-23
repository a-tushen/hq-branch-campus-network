# -*- coding: utf-8 -*-
"""各网络设备配置脚本（可直接粘贴到 eNSP CLI）。

约定：每台设备一份字符串列表，首行为 system-view。
终端设备（PC/Server/Client/AP/STA）无 CLI 配置，地址在 .topo 的 settings 中预置。
"""

# ================================================================ 总部：FW1
FW1 = """system-view
sysname FW1
#
interface GigabitEthernet0/0/0
 ip address 10.0.0.1 255.255.255.252
 service-manage ping permit
quit
interface GigabitEthernet0/0/1
 ip address 200.1.1.1 255.255.255.252
 service-manage ping permit
quit
#
firewall zone trust
 add interface GigabitEthernet0/0/0
quit
firewall zone untrust
 add interface GigabitEthernet0/0/1
quit
#
ip route-static 0.0.0.0 0.0.0.0 200.1.1.2
ip route-static 192.168.0.0 255.255.0.0 10.0.0.2
ip route-static 10.99.0.0 255.255.255.0 10.0.0.2
#
acl number 2000
 rule 5 permit source 192.168.0.0 0.0.255.255
quit
interface GigabitEthernet0/0/1
 nat outbound 2000
quit
#
nat server web_server protocol tcp global 200.1.1.10 80 inside 192.168.40.10 80
#
security-policy
 rule name trust_to_untrust
  source-zone trust
  destination-zone untrust
  action permit
 rule name branch_to_hq_server
  source-zone untrust
  destination-zone trust
  destination-address 192.168.40.10 mask 255.255.255.255
  service http
  action permit
quit
#
return"""

# ================================================================ 总部：LSW2（核心）
LSW2 = """system-view
sysname LSW2
#
vlan batch 10 20 30 40 50 99 100
#
stp region-configuration
 region-name HQ
 instance 1 vlan 10 30
 instance 2 vlan 20
 active region-configuration
quit
#
interface GigabitEthernet0/0/1
 port link-type access
 port default vlan 50
quit
interface GigabitEthernet0/0/2
 port link-type access
 port default vlan 50
quit
interface GigabitEthernet0/0/3
 port link-type access
 port default vlan 40
quit
interface GigabitEthernet0/0/4
 port link-type trunk
 port trunk allow-pass vlan 10 20 30 99
quit
interface GigabitEthernet0/0/6
 port link-type trunk
 port trunk allow-pass vlan 10 20 30 99
quit
interface GigabitEthernet0/0/5
 port link-type access
 port default vlan 100
quit
#
interface Vlanif40
 ip address 192.168.40.254 255.255.255.0
quit
interface Vlanif50
 ip address 192.168.50.254 255.255.255.0
quit
interface Vlanif99
 ip address 10.99.0.1 255.255.255.0
quit
interface Vlanif100
 ip address 10.0.0.2 255.255.255.252
quit
#
ip route-static 192.168.10.0 255.255.255.0 10.99.0.3
ip route-static 192.168.30.0 255.255.255.0 10.99.0.3
ip route-static 192.168.20.0 255.255.255.0 10.99.0.4
ip route-static 192.168.10.0 255.255.255.0 10.99.0.4 preference 70
ip route-static 192.168.30.0 255.255.255.0 10.99.0.4 preference 70
ip route-static 192.168.20.0 255.255.255.0 10.99.0.3 preference 70
ip route-static 0.0.0.0 0.0.0.0 10.0.0.1
#
return"""

# ================================================================ 总部：LSW3（网关主）
LSW3 = """system-view
sysname LSW3
#
vlan batch 10 20 30 99
#
stp region-configuration
 region-name HQ
 instance 1 vlan 10 30
 instance 2 vlan 20
 active region-configuration
quit
stp instance 1 root primary
stp instance 2 root secondary
#
dhcp enable
#
interface GigabitEthernet0/0/1
 port link-type trunk
 port trunk allow-pass vlan 10 20 30 99
quit
interface GigabitEthernet0/0/2
 port link-type trunk
 port trunk allow-pass vlan 10 20 30
quit
#
interface Vlanif10
 ip address 192.168.10.252 255.255.255.0
 vrrp vrid 10 virtual-ip 192.168.10.254
 vrrp vrid 10 priority 120
 vrrp vrid 10 preempt-mode timer delay 20
 vrrp vrid 10 track interface GigabitEthernet0/0/1 reduced 30
 dhcp select relay
 dhcp relay server-ip 192.168.50.10
quit
interface Vlanif20
 ip address 192.168.20.252 255.255.255.0
 vrrp vrid 20 virtual-ip 192.168.20.254
 vrrp vrid 20 preempt-mode timer delay 20
 vrrp vrid 20 track interface GigabitEthernet0/0/1 reduced 30
 dhcp select relay
 dhcp relay server-ip 192.168.50.10
quit
interface Vlanif30
 ip address 192.168.30.252 255.255.255.0
 vrrp vrid 30 virtual-ip 192.168.30.254
 vrrp vrid 30 priority 120
 vrrp vrid 30 preempt-mode timer delay 20
 vrrp vrid 30 track interface GigabitEthernet0/0/1 reduced 30
 dhcp select relay
 dhcp relay server-ip 192.168.50.10
quit
interface Vlanif99
 ip address 10.99.0.3 255.255.255.0
quit
#
ip route-static 0.0.0.0 0.0.0.0 10.99.0.1
#
return"""

# ================================================================ 总部：LSW4（网关备）
LSW4 = """system-view
sysname LSW4
#
vlan batch 10 20 30 99
#
stp region-configuration
 region-name HQ
 instance 1 vlan 10 30
 instance 2 vlan 20
 active region-configuration
quit
stp instance 1 root secondary
stp instance 2 root primary
#
dhcp enable
#
interface GigabitEthernet0/0/1
 port link-type trunk
 port trunk allow-pass vlan 10 20 30 99
quit
interface GigabitEthernet0/0/2
 port link-type trunk
 port trunk allow-pass vlan 10 20 30
quit
#
interface Vlanif10
 ip address 192.168.10.253 255.255.255.0
 vrrp vrid 10 virtual-ip 192.168.10.254
 vrrp vrid 10 preempt-mode timer delay 20
 vrrp vrid 10 track interface GigabitEthernet0/0/1 reduced 30
 dhcp select relay
 dhcp relay server-ip 192.168.50.10
quit
interface Vlanif20
 ip address 192.168.20.253 255.255.255.0
 vrrp vrid 20 virtual-ip 192.168.20.254
 vrrp vrid 20 priority 120
 vrrp vrid 20 preempt-mode timer delay 20
 vrrp vrid 20 track interface GigabitEthernet0/0/1 reduced 30
 dhcp select relay
 dhcp relay server-ip 192.168.50.10
quit
interface Vlanif30
 ip address 192.168.30.253 255.255.255.0
 vrrp vrid 30 virtual-ip 192.168.30.254
 vrrp vrid 30 preempt-mode timer delay 20
 vrrp vrid 30 track interface GigabitEthernet0/0/1 reduced 30
 dhcp select relay
 dhcp relay server-ip 192.168.50.10
quit
interface Vlanif99
 ip address 10.99.0.4 255.255.255.0
quit
#
ip route-static 0.0.0.0 0.0.0.0 10.99.0.1
#
return"""

# ================================================================ 总部：LSW1（接入）
LSW1 = """system-view
sysname LSW1
#
vlan batch 10 20 30
#
stp region-configuration
 region-name HQ
 instance 1 vlan 10 30
 instance 2 vlan 20
 active region-configuration
quit
#
interface GigabitEthernet0/0/1
 port link-type trunk
 port trunk allow-pass vlan 10 20 30
quit
interface GigabitEthernet0/0/2
 port link-type trunk
 port trunk allow-pass vlan 10 20 30
quit
interface GigabitEthernet0/0/3
 port link-type access
 port default vlan 10
 stp edged-port enable
quit
interface GigabitEthernet0/0/4
 port link-type access
 port default vlan 20
 stp edged-port enable
quit
interface GigabitEthernet0/0/5
 port link-type access
 port default vlan 30
 stp edged-port enable
quit
#
return"""

# ================================================================ 总部：DHCP 服务器
DHCP = """system-view
sysname DHCP
#
dhcp enable
#
ip pool vlan10
 network 192.168.10.0 mask 255.255.255.0
 gateway-list 192.168.10.254
 dns-list 114.114.114.114
 excluded-ip-address 192.168.10.252 192.168.10.253
quit
ip pool vlan20
 network 192.168.20.0 mask 255.255.255.0
 gateway-list 192.168.20.254
 dns-list 114.114.114.114
 excluded-ip-address 192.168.20.252 192.168.20.253
quit
ip pool vlan30
 network 192.168.30.0 mask 255.255.255.0
 gateway-list 192.168.30.254
 dns-list 114.114.114.114
 excluded-ip-address 192.168.30.252 192.168.30.253
quit
#
interface GigabitEthernet0/0/0
 ip address 192.168.50.10 255.255.255.0
 dhcp select global
quit
#
ip route-static 0.0.0.0 0.0.0.0 192.168.50.254
#
return"""

# ================================================================ 总部：AC1（无线控制器）
AC1 = """system-view
sysname AC1
#
vlan batch 50
#
interface GigabitEthernet0/0/1
 port link-type access
 port default vlan 50
quit
interface Vlanif50
 ip address 192.168.50.11 255.255.255.0
quit
#
ip route-static 0.0.0.0 0.0.0.0 192.168.50.254
#
capwap source interface Vlanif50
#
wlan
 security-profile name HQ-PSK
  security wpa-wpa2 psk pass-phrase Huawei@123 aes
 quit
 ssid-profile name HQ-SSID
  ssid HQ-WLAN
 quit
 vap-profile name HQ-VAP
  service-vlan vlan-id 30
  ssid-profile HQ-SSID
  security-profile HQ-PSK
 quit
 ap-group name default
  vap-profile HQ-VAP wlan 1 radio all
 quit
 ap auth-mode no-auth
quit
#
return"""

# ================================================================ ISP：AR1
AR1 = """system-view
sysname AR1
#
interface GigabitEthernet0/0/0
 ip address 200.1.1.2 255.255.255.252
quit
interface GigabitEthernet0/0/1
 ip address 100.1.1.1 255.255.255.252
quit
#
ospf 1 router-id 1.1.1.1
 area 0.0.0.0
  network 200.1.1.0 0.0.0.3
  network 100.1.1.0 0.0.0.3
 quit
quit
#
return"""

# ================================================================ ISP：AR2
AR2 = """system-view
sysname AR2
#
interface GigabitEthernet0/0/0
 ip address 100.1.1.2 255.255.255.252
quit
interface GigabitEthernet0/0/1
 ip address 100.2.1.1 255.255.255.252
quit
interface GigabitEthernet0/0/2
 ip address 192.168.200.254 255.255.255.0
quit
#
ospf 1 router-id 2.2.2.2
 area 0.0.0.0
  network 100.1.1.0 0.0.0.3
  network 100.2.1.0 0.0.0.3
  network 192.168.200.0 0.0.0.255
 quit
quit
#
return"""

# ================================================================ ISP：AR3
AR3 = """system-view
sysname AR3
#
interface GigabitEthernet0/0/0
 ip address 100.2.1.2 255.255.255.252
quit
interface GigabitEthernet0/0/2
 ip address 201.1.1.1 255.255.255.252
quit
#
ospf 1 router-id 3.3.3.3
 area 0.0.0.0
  network 100.2.1.0 0.0.0.3
  network 201.1.1.0 0.0.0.3
 quit
quit
#
return"""

# ================================================================ ISP：LSW6
LSW6 = """system-view
sysname LSW6
#
vlan batch 200
#
interface GigabitEthernet0/0/1
 port link-type access
 port default vlan 200
quit
interface GigabitEthernet0/0/2
 port link-type access
 port default vlan 200
 stp edged-port enable
quit
interface GigabitEthernet0/0/3
 port link-type access
 port default vlan 200
 stp edged-port enable
quit
interface GigabitEthernet0/0/4
 port link-type access
 port default vlan 200
 stp edged-port enable
quit
#
return"""

# ================================================================ 分支：AR4
AR4 = """system-view
sysname AR4
#
interface GigabitEthernet0/0/1
 ip address 201.1.1.2 255.255.255.252
quit
#
interface Eth-Trunk1
 undo portswitch
 mode lacp-static
quit
interface GigabitEthernet0/0/0
 eth-trunk 1
quit
interface GigabitEthernet0/0/2
 eth-trunk 1
quit
#
interface Eth-Trunk1.10
 dot1q termination vid 10
 ip address 192.168.110.254 255.255.255.0
 arp broadcast enable
quit
interface Eth-Trunk1.20
 dot1q termination vid 20
 ip address 192.168.120.254 255.255.255.0
 arp broadcast enable
quit
interface Eth-Trunk1.30
 dot1q termination vid 30
 ip address 192.168.130.254 255.255.255.0
 arp broadcast enable
quit
#
acl number 2000
 rule 5 permit source 192.168.0.0 0.0.255.255
quit
interface GigabitEthernet0/0/1
 nat outbound 2000
quit
#
ip route-static 0.0.0.0 0.0.0.0 201.1.1.1
#
return"""

# ================================================================ 分支：LSW5
LSW5 = """system-view
sysname LSW5
#
vlan batch 10 20 30
#
interface Eth-Trunk1
 mode lacp-static
 port link-type trunk
 port trunk allow-pass vlan 10 20 30
quit
interface GigabitEthernet0/0/1
 eth-trunk 1
quit
interface GigabitEthernet0/0/2
 eth-trunk 1
quit
#
interface GigabitEthernet0/0/3
 port link-type access
 port default vlan 10
 stp edged-port enable
quit
interface GigabitEthernet0/0/4
 port link-type access
 port default vlan 20
 stp edged-port enable
quit
interface GigabitEthernet0/0/5
 port link-type access
 port default vlan 30
 stp edged-port enable
quit
#
return"""

# 汇总：名称 -> 配置文本
CONFIGS = {
    "FW1": FW1, "LSW1": LSW1, "LSW2": LSW2, "LSW3": LSW3, "LSW4": LSW4,
    "DHCP": DHCP, "AC1": AC1,
    "AR1": AR1, "AR2": AR2, "AR3": AR3, "LSW6": LSW6,
    "AR4": AR4, "LSW5": LSW5,
}

# 每台设备的配置要点（写进说明文档）
NOTES = {
    "FW1": "接口与安全域、默认路由、源NAT（easy-ip）、NAT Server 发布服务器、安全策略",
    "LSW2": "核心交换：服务器/管理/互联 VLAN 网关，到网关双机的静态路由与默认路由",
    "LSW3": "VLAN10/30 的 VRRP 主 + VLAN20 备；MSTP 实例1根桥；DHCP 中继",
    "LSW4": "VLAN20 的 VRRP 主 + VLAN10/30 备；MSTP 实例2根桥；DHCP 中继",
    "LSW1": "接入交换：PC1/PC2/AP 划分 VLAN，双上行 trunk，边缘端口",
    "DHCP": "全局地址池 3 个（VLAN10/20/30），网关指向 VRRP 虚地址",
    "AC1": "CAPWAP 源接口、SSID/安全模板/VAP 模板、业务 VLAN 30、AP 免认证上线",
    "AR1": "ISP 边缘：到总部公网互联 + OSPF",
    "AR2": "ISP 核心：三方向互联 + 公网服务器区网关 + OSPF",
    "AR3": "ISP 边缘：到分支公网互联 + OSPF",
    "LSW6": "公网服务器区接入：VLAN200",
    "AR4": "分支网关：Eth-Trunk 上起 dot1q 子接口作为三 VLAN 网关 + 源NAT + 默认路由",
    "LSW5": "分支接入：Eth-Trunk 双链路聚合，三个 VLAN 接入端口",
}
