# -*- coding: utf-8 -*-
"""对生成的拓扑与配置做交叉一致性校验。

检查项：
 1) 链路上引用的接口序号不超过该型号的接口总数
 2) VRRP 虚地址 == DHCP 地址池 gateway-list
 3) DHCP 中继指向的服务器地址 == DHCP 服务器接口地址
 4) LSW2 静态路由的下一跳确实属于 LSW3/LSW4/FW1
 5) NAT Server 的 inside 地址 == Server1 的地址
 6) 每台设备的 sysname 与设备名一致
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import lab_plan as P        # noqa: E402
import lab_configs as C     # noqa: E402
import build_lab as B       # noqa: E402

errors = []
warns = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


# ---------------------------------------------------------------- 1 接口存在性
iface_total = {m: sum(e[-1] for e in v) for m, v in P.MODEL_IFACES.items()}
model_of = {d[0]: d[1] for d in P.DEVICES}
for a, ifa, b, ifb in P.LINKS:
    for dev, ifn in ((a, ifa), (b, ifb)):
        model = model_of[dev]
        idx = B.iface_index(model, ifn)
        total = iface_total[model]
        check(0 <= idx < total,
              "链路 %s.%s 序号 %d 超出 %s 的接口总数 %d"
              % (dev, ifn, idx, model, total))

# ---------------------------------------------------------------- 6 sysname
for name, text in C.CONFIGS.items():
    m = re.search(r"sysname (\S+)", text)
    check(m and m.group(1) == name,
          "%s 的 sysname 为 %s，与文件名不一致"
          % (name, m.group(1) if m else "无"))

# ---------------------------------------------------------------- 2 VRRP vs DHCP
vrrp = {}
for dev in ("LSW3", "LSW4"):
    t = C.CONFIGS[dev]
    for m in re.finditer(
            r"interface Vlanif(\d+)\n(.*?)quit", t, re.S):
        vid, body = m.group(1), m.group(2)
        vip = re.search(r"vrrp vrid \d+ virtual-ip (\S+)", body)
        if vip:
            vrrp.setdefault(vid, set()).add(vip.group(1))

dhcp_t = C.CONFIGS["DHCP"]
pools = {}
for m in re.finditer(r"ip pool (\S+)\n(.*?)quit", dhcp_t, re.S):
    name, body = m.group(1), m.group(2)
    net = re.search(r"network (\S+) mask (\S+)", body)
    gw = re.search(r"gateway-list (\S+)", body)
    pools[name] = (net.group(1), gw.group(1) if gw else None)

for vid, vips in sorted(vrrp.items()):
    check(len(vips) == 1, "VLAN%s 的 VRRP 虚地址在 LSW3/LSW4 上不一致：%s"
          % (vid, sorted(vips)))
    vip = sorted(vips)[0]
    pool = pools.get("vlan%s" % vid)
    check(pool is not None, "缺少 VLAN%s 对应的 DHCP 地址池" % vid)
    if pool:
        check(pool[1] == vip,
              "VLAN%s：VRRP 虚地址 %s 与 DHCP 网关 %s 不一致"
              % (vid, vip, pool[1]))

# ---------------------------------------------------------------- 3 DHCP 中继
relay_ips = set(re.findall(r"dhcp relay server-ip (\S+)",
                           C.CONFIGS["LSW3"] + C.CONFIGS["LSW4"]))
dhcp_addr = re.search(r"interface GigabitEthernet0/0/0\n ip address (\S+)",
                      dhcp_t).group(1)
check(relay_ips == {dhcp_addr},
      "DHCP 中继地址 %s 与 DHCP 服务器地址 %s 不一致"
      % (sorted(relay_ips), dhcp_addr))

# ---------------------------------------------------------------- 4 静态路由下一跳
known_nh = {
    "10.99.0.3": "LSW3 Vlanif99",
    "10.99.0.4": "LSW4 Vlanif99",
    "10.0.0.1": "FW1 GE1/0/0",
}
for m in re.finditer(r"ip route-static (\S+) (\S+) (\S+)(?: preference \d+)?",
                     C.CONFIGS["LSW2"]):
    nh = m.group(3)
    check(nh in known_nh,
          "LSW2 静态路由下一跳 %s 不在预期集合内" % nh)

# 下一跳地址确实配置在对应设备上
check("ip address 10.99.0.3" in C.CONFIGS["LSW3"], "LSW3 缺少 10.99.0.3")
check("ip address 10.99.0.4" in C.CONFIGS["LSW4"], "LSW4 缺少 10.99.0.4")
check("ip address 10.0.0.1" in C.CONFIGS["FW1"], "FW1 缺少 10.0.0.1")

# ---------------------------------------------------------------- 5 NAT Server
nat = re.search(r"nat server \S+ protocol tcp global (\S+) (\d+) inside (\S+) (\d+)",
                C.CONFIGS["FW1"])
check(nat is not None, "FW1 缺少 NAT Server 配置")
if nat:
    srv = P.TERMINAL_IP["Server1"][0]
    check(nat.group(3) == srv,
          "NAT Server inside 地址 %s 与 Server1 地址 %s 不一致"
          % (nat.group(3), srv))
    check(nat.group(1) == "200.1.1.10",
          "NAT Server 公网地址为 %s，规划为 200.1.1.10" % nat.group(1))

# ---------------------------------------------------------------- 其他提示项
if "vlan batch 10 20 30 99 100" not in C.CONFIGS["LSW2"]:
    pass
for dev in ("LSW1", "LSW2", "LSW3", "LSW4"):
    if "region-name HQ" not in C.CONFIGS[dev]:
        warns.append("%s 未加入 MSTP 域 HQ（可能影响成环时的阻塞位置）" % dev)

if "arp broadcast enable" not in C.CONFIGS["AR4"]:
    errors.append("AR4 子接口缺少 arp broadcast enable")

# ---------------------------------------------------------------- 输出
print("检查链路数：%d，设备数：%d" % (len(P.LINKS), len(P.DEVICES)))
if warns:
    print("\n提示：")
    for w in warns:
        print("  - " + w)
if errors:
    print("\n发现 %d 处问题：" % len(errors))
    for e in errors:
        print("  [X] " + e)
    sys.exit(1)
print("\n[PASS] 全部校验通过")
