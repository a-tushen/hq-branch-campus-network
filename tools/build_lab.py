# -*- coding: utf-8 -*-
"""由 lab_plan.py + lab_configs.py 生成 eNSP 拓扑文件、设备配置与说明文档。

用法： python build_lab.py
产物：
  topology/企业总部-分支综合实验.topo
  configs/<设备名>.txt
  配置与验证说明.md
"""
import io
import os
import random
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import lab_plan as P          # noqa: E402
import lab_configs as C       # noqa: E402

TOPO_DIR = os.path.join(BASE, "topology")
CFG_DIR = os.path.join(BASE, "configs")
TOPO_NAME = P.TITLE.replace(" ", "") + ".topo"

START_PORT = 2000


# ------------------------------------------------------------------ 接口索引
def iface_index(model, name):
    """把 GE0/0/5 / GE1/0/1 之类接口名转成 .topo 中的序号。"""
    tail = name.split("/")[-1]
    n = int(tail)
    return n - P.IFACE_START.get(model, 0)


def build_slots(model):
    parts = []
    for entry in P.MODEL_IFACES[model]:
        if len(entry) == 3:
            sztype, iname, cnt = entry
        else:
            sztype, iname, cnt = entry[0], entry[1], 1
        parts.append('                <interface sztype="%s" interfacename="%s" '
                     'count="%d" />' % (sztype, iname, cnt))
    if not parts:
        return '            <slot number="slot17" isMainBoard="1" />'
    body = "\n".join(parts)
    return ('            <slot number="slot17" isMainBoard="1">\n'
            '%s\n            </slot>' % body)


def mac_for(idx):
    rnd = random.Random(idx + 7)
    return "54-89-98-%02X-%02X-%02X" % (rnd.randrange(256),
                                        rnd.randrange(256),
                                        rnd.randrange(256))


def pc_settings(name, mac):
    """PC / Client 的 settings（-simpc_* 形式）。"""
    ip, mask, gw = P.TERMINAL_IP.get(name, ("0.0.0.0", "0.0.0.0", "0.0.0.0"))
    state = 1 if name in P.DHCP_CLIENTS else 0
    return (" -simpc_ip %s -simpc_mask %s -simpc_gateway %s -simpc_mac %s "
            "-simpc_mc_dstip 0.0.0.0 -simpc_mc_dstmac 00-00-00-00-00-00 "
            "-simpc_dns1 0.0.0.0 -simpc_dns2 0.0.0.0 -simpc_ipv6 :: "
            "-simpc_prefix 128 -simpc_gatewayv6 :: -simpc_dhcp_state %d "
            "-simpc_dhcpv6_state 0 -simpc_dns_auto_state 0 -simpc_igmp_version 1 "
            "-simpc_group_ip_start 0.0.0.0 -simpc_src_ip_start 0.0.0.0 "
            "-simpc_group_num 0 -simpc_group_step 0 -simpc_src_num 0 "
            "-simpc_src_step 0 -simpc_type MODE_IS_INCLUDE "
            % (ip, mask, gw, mac, state))


def server_settings(name, mac):
    """Server 的 settings（-ipaddr 形式，与 PC 不同）。"""
    ip, mask, gw = P.TERMINAL_IP.get(name, ("0.0.0.0", "255.255.255.0",
                                            "0.0.0.0"))
    return ("-domain 0 -eth %s -ipaddr %s -ipmask %s -gateway %s "
            "-ipv6addr 2000::2 -ipv6gateway 2000::1 -prefixlen 64 "
            "-ipv4dns 0.0.0.0 -ipv6dns 3000::1 -dnslist NULL"
            % (mac, ip, mask, gw))


def device_settings(name, model, mac):
    if model in ("PC", "Client"):
        return pc_settings(name, mac)
    if model == "Server":
        return server_settings(name, mac)
    if model == "AP6050":
        return " -apMac %s -apSN 210235448310D2176025" % mac
    if model == "STA":
        return (" -simsta_ip 0.0.0.0 -simsta_mask 0.0.0.0 "
                "-simsta_gateway 0.0.0.0 -simsta_mac %s -simsta_check 0 " % mac)
    return ""


# ------------------------------------------------------------------ 生成 .topo
def build_topo():
    random.seed(20261018)
    ids = {}
    dev_xml = []
    port = START_PORT
    for idx, (name, model, x, y, is_terminal) in enumerate(P.DEVICES):
        uid = str(uuid.UUID(int=random.getrandbits(128), version=4)).upper()
        ids[name] = uid
        mac = mac_for(idx)
        settings = device_settings(name, model, mac)
        com = 0 if is_terminal else port
        if not is_terminal:
            port += 1
        smac = mac if model in P.TERMINAL_MODELS else ""
        bmode = 0 if is_terminal else 1
        dev_xml.append(
            '        <dev id="%s" name="%s" poe="0" model="%s" '
            'settings="%s" system_mac="%s" com_port="%d" bootmode="%d" '
            'cx="%f" cy="%f" edit_left="%d" edit_top="%d">\n%s\n        </dev>'
            % (uid, name, model, settings, smac, com, bmode,
               float(x), float(y), x + 27, y + 54, build_slots(model)))

    line_xml = []
    pos = {d[0]: (d[2], d[3]) for d in P.DEVICES}
    model_of = {d[0]: d[1] for d in P.DEVICES}
    for a, ifa, b, ifb in P.LINKS:
        ax, ay = pos[a]
        bx, by = pos[b]
        si = iface_index(model_of[a], ifa)
        ti = iface_index(model_of[b], ifb)
        line_xml.append(
            '        <line srcDeviceID="%s" destDeviceID="%s">\n'
            '            <interfacePair lineName="Copper" srcIndex="%d" '
            'srcBoundRectIsMoved="1" srcBoundRect_X="%f" srcBoundRect_Y="%f" '
            'srcOffset_X="-13.000000" srcOffset_Y="-21.000000" tarIndex="%d" '
            'tarBoundRectIsMoved="1" tarBoundRect_X="%f" tarBoundRect_Y="%f" '
            'tarOffset_X="-27.000000" tarOffset_Y="-19.000000" />\n'
            '        </line>'
            % (ids[a], ids[b], si, float(ax), float(ay), ti,
               float(bx), float(by)))

    # 区域框（type=1 矩形；color 为 0xBBGGRR）
    def rect(x, y, w, h, rgb, fill):
        bb, gg, rr = rgb
        color = bb * 65536 + gg * 256 + rr
        return ('        <shape type="1" filloption="%d" color="%d" '
                'upleftcorner="%d,%d" width="%d" height="%d" startpt="0,0" '
                'endpt="0,0" borderStyle="5" borderWidth="1" />'
                % (fill, color, x, y, w, h))

    shapes = [
        rect(20, 30, 560, 830, (232, 240, 250), 1),    # 总部
        rect(480, 30, 500, 560, (204, 226, 245), 1),   # ISP
        rect(900, 30, 360, 560, (232, 240, 250), 1),   # 分支
    ]

    def tip(x, y, w, h, text, size=110):
        esc = text.replace("\r\n", "&#x0D;&#x0A;")
        return ('        <txttip left="%d" top="%d" right="%d" bottom="%d" '
                'content="%s" fontname="宋体" fontstyle="1" editsize="%d" '
                'txtcolor="-16777216" txtbkcolor="-1" charset="1" />'
                % (x, y, x + w, y + h, esc, size))

    tips = [
        tip(30, 40, 90, 30, "总部"),
        tip(500, 40, 70, 30, "ISP"),
        tip(910, 40, 90, 30, "分支"),
        tip(20, 875, 1240, 150,
            "需求：\r\n"
            "1. 自行规划 IP 与 VLAN，每个终端属于一个 VLAN。\r\n"
            "总部：\r\n"
            "  1) PC1 主网关在 LSW3，PC2 主网关在 LSW4，且互为主备（VRRP）。\r\n"
            "  2) PC1、PC2、AP 及 STA 的 IP 地址统一由 DHCP 下发（DHCP 中继）。\r\n"
            "  3) 总部服务器需被公网和分支客户端访问（NAT Server）。\r\n"
            "分支：\r\n"
            "  1) 终端设备网关在路由器上（Eth-Trunk 子接口 dot1q）。\r\n"
            "  2) 路由器与交换机之间采用链路聚合实现备份（LACP Eth-Trunk）。",
            100),
    ]

    xml = ['<?xml version="1.0" encoding="UNICODE" ?>',
           '<topo version="1.2.00.300">',
           '    <devices>']
    xml += dev_xml
    xml += ['    </devices>', '    <lines>']
    xml += line_xml
    xml += ['    </lines>', '    <shapes>']
    xml += shapes
    xml += ['    </shapes>', '    <txttips>']
    xml += tips
    xml += ['    </txttips>', '</topo>', '']
    return "\n".join(xml)


# ------------------------------------------------------------------ 说明文档
def build_md():
    L = []
    A = L.append
    A("# %s" % P.TITLE)
    A("")
    A("## 一、如何导入")
    A("")
    A("1. 打开 eNSP → 菜单 **文件 / File → 打开** → 选择")
    A("   `topology/%s`。" % TOPO_NAME)
    A("2. 全选设备右键 **启动**（共 %d 台，首次启动约 3～5 分钟）。"
      % len(P.DEVICES))
    A("3. 逐台双击进入 CLI，把 `configs/<设备名>.txt` 全文粘贴进去。")
    A("4. 每台配置完执行 `save` → `y` 保存。")
    A("")
    A("> 终端（PC / Server / Client）地址已写在 .topo 里，启动后即生效；")
    A("> PC1、PC2、AP1、STA1 设为 DHCP 获取。")
    A("")
    A("## 二、设备与端口连接")
    A("")
    A("| 设备A | 端口 | 设备B | 端口 |")
    A("|---|---|---|---|")
    for a, ifa, b, ifb in P.LINKS:
        A("| %s | %s | %s | %s |" % (a, ifa, b, ifb))
    A("")
    A("## 三、VLAN 与地址规划（总部）")
    A("")
    A("| VLAN | 用途 | 网段 | 网关/VRRP VIP | LSW3 | LSW4 | 说明 |")
    A("|---|---|---|---|---|---|---|")
    for row in P.VLAN_PLAN:
        A("| %s |" % " | ".join(row))
    A("")
    A("## 四、ISP 互联地址")
    A("")
    A("| 链路 | 网段 | 地址 |")
    A("|---|---|---|")
    for row in P.ISP_PLAN:
        A("| %s | %s | %s |" % row)
    A("")
    A("## 五、分支规划")
    A("")
    A("| VLAN | 终端 | 网段 | 网关 | 说明 |")
    A("|---|---|---|---|---|")
    for row in P.BRANCH_PLAN:
        A("| %s | %s | %s | %s | %s |" % row)
    A("")
    A("## 六、终端地址")
    A("")
    A("| 终端 | 地址 | 网关 | 获取方式 |")
    A("|---|---|---|---|")
    for name, (ip, mask, gw) in P.TERMINAL_IP.items():
        A("| %s | %s/24 | %s | 静态 |" % (name, ip, gw))
    for name in sorted(P.DHCP_CLIENTS):
        A("| %s | DHCP | DHCP 下发 | 动态 |" % name)
    A("")
    A("## 七、NAT 规划")
    A("")
    A("| 用途 | 位置 | 规则 | 作用 |")
    A("|---|---|---|---|")
    for row in P.NAT_PLAN:
        A("| %s | %s | %s | %s |" % row)
    A("")
    A("## 八、需求实现对应关系")
    A("")
    A("| 题目要求 | 实现方式 | 落点 |")
    A("|---|---|---|")
    A("| 每个终端一个 VLAN | VLAN 10/20/30/40/50，接入端口 access 划分 | LSW1、LSW2、LSW5 |")
    A("| PC1 网关在 LSW3、PC2 在 LSW4，互为主备 | VRRP vrid 10/20/30，"
      "LSW3 优先 VLAN10/30，LSW4 优先 VLAN20 | LSW3、LSW4 Vlanif |")
    A("| PC/AP/STA 由 DHCP 下发 | 独立 DHCP 服务器 + 各网关上 `dhcp select relay` "
      "| DHCP、LSW3、LSW4 |")
    A("| 总部服务器被公网与分支访问 | FW1 `nat server` 发布 200.1.1.10:80 | FW1 |")
    A("| 分支终端网关在路由器 | AR4 Eth-Trunk1 上起 .10/.20/.30 子接口 + "
      "`dot1q termination` | AR4 |")
    A("| 路由器与交换机链路聚合备份 | AR4 与 LSW5 之间 LACP Eth-Trunk1（2 成员口） "
      "| AR4、LSW5 |")
    A("")
    A("## 九、关键验证项")
    A("")
    A("| 验证项 | 操作 | 期望 |")
    A("|---|---|---|")
    for row in P.VERIFY:
        A("| %s | %s | %s |" % row)
    A("")
    A("## 十、配置要点")
    A("")
    A("| 设备 | 要点 |")
    A("|---|---|")
    for k in ["FW1", "LSW2", "LSW3", "LSW4", "LSW1", "DHCP", "AC1",
              "AR1", "AR2", "AR3", "LSW6", "AR4", "LSW5"]:
        A("| %s | %s |" % (k, C.NOTES.get(k, "")))
    A("")
    A("## 十一、注意事项")
    A("")
    A("1. **防火墙型号**：本拓扑用 `USG5500`（本机实测可正常加载，"
      "接口为 `GE1/0/0`～`GE1/0/8`）。若要换 `USG6000V`，把设备型号换掉、"
      "并在 `FW1.txt` 中把接口名按实际显示统一即可（配置逻辑不变）。")
    A("2. **防火墙登录**：`USG5500` 默认 `admin` / `Admin@123`；"
      "`USG6000V` 首次登录会强制改密码。")
    A("3. **无线部分**：AP1 需 `ap auth-mode no-auth` 免认证上线；"
      "STA1 搜索 SSID `HQ-WLAN`，密码 `Huawei@123` 关联。")
    A("4. **VRRP 与 STP 已对齐**：VLAN10/30 的根桥与 VRRP 主都在 LSW3，"
      "VLAN20 都在 LSW4，避免流量绕行。")
    A("5. **链路聚合**：两端都要 `mode lacp-static`，AR4 侧先建 Eth-Trunk 再"
      "加入物理口，分支网关子接口必须带 `arp broadcast enable`。")
    A("6. **防火墙命令差异**：`USG5500` 用接口下 `nat outbound 2000` + 系统视图 "
      "`nat server`。若该版本不支持 `security-policy` 视图（V300 早期用 "
      "`policy interzone`），可跳过安全策略那段——此时默认策略为 permit，"
      "实验连通性不受影响，但答辩时应说明这是未收紧的配置。")
    A("7. **eNSP 版本差异**：若某条命令报错，多为该版本不支持，"
      "可跳过并在报告中说明。")
    A("")
    return "\n".join(L)


def main():
    os.makedirs(TOPO_DIR, exist_ok=True)
    os.makedirs(CFG_DIR, exist_ok=True)

    topo = build_topo()
    tpath = os.path.join(TOPO_DIR, TOPO_NAME)
    # 本机 eNSP 1.3.00.100 保存的 .topo 为无 BOM 的 UTF-8（虽声明 encoding="UNICODE"），
    # 与自带 GBK 样例不同；按本机实际写法输出，保证中文标注不乱码。
    io.open(tpath, "w", encoding="utf-8", newline="\r\n").write(topo)

    for name, text in C.CONFIGS.items():
        fpath = os.path.join(CFG_DIR, name + ".txt")
        body = text.replace("\n", "\r\n")
        io.open(fpath, "w", encoding="utf-8", newline="").write(body)

    mpath = os.path.join(BASE, "配置与验证说明.md")
    io.open(mpath, "w", encoding="utf-8", newline="\n").write(build_md())

    print("topo   :", tpath, len(topo), "bytes")
    print("configs:", len(C.CONFIGS), "files")
    print("readme :", mpath)


if __name__ == "__main__":
    main()
