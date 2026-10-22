# 设备配置说明

本目录是 13 台网络设备的完整配置，一台设备一个文件，文件名即设备名。
配置按"可直接粘贴"的格式书写：每行一条命令，用 `system-view` 进入系统视图，
结尾 `return` 返回用户视图。

## 文件与设备对应

| 文件 | 设备型号 | 角色 | 关键配置 |
|---|---|---|---|
| `FW1.txt` | USG5500 | 出口防火墙 | 安全域划分、默认路由、源 NAT（Easy-IP）、NAT Server、域间策略 |
| `LSW2.txt` | S5700 | 核心交换 | VLAN 创建、服务器区/管理区网关、到网关双机的静态路由、默认路由 |
| `LSW3.txt` | S5700 | 双网关（主 VLAN10/30） | VRRP 三备份组、MSTP 实例1 根桥、DHCP 中继 |
| `LSW4.txt` | S5700 | 双网关（主 VLAN20） | 与 LSW3 对称，MSTP 实例2 根桥 |
| `LSW1.txt` | S5700 | 总部接入 | 终端 VLAN 划分、双上行 trunk、边缘端口 |
| `LSW5.txt` | S5700 | 分支接入 | Eth-Trunk 双成员口、三 VLAN 接入端口 |
| `LSW6.txt` | S5700 | 公网服务器区接入 | VLAN 200 |
| `AR1.txt` | AR2220 | ISP 边缘（近总部） | 公网互联、OSPF |
| `AR2.txt` | AR2220 | ISP 核心 | 三方向互联、公网服务器区网关、OSPF |
| `AR3.txt` | AR2220 | ISP 边缘（近分支） | 公网互联、OSPF |
| `AR4.txt` | AR2220 | 分支网关兼出口 | Eth-Trunk 子接口（dot1q）、`arp broadcast enable`、源 NAT、默认路由 |
| `DHCP.txt` | AR2220 | 独立 DHCP 服务器 | 三个全局地址池，网关指向 VRRP 虚拟地址 |
| `AC1.txt` | AC6005 | 无线控制器 | CAPWAP 源接口、SSID/安全/VAP 模板、AP 免认证 |

## 使用方式

1. eNSP 中先把对应设备启动，双击进入 CLI；
2. 打开对应 `.txt`，**全选复制**后粘贴到 CLI（eNSP 支持多行粘贴）；
3. 粘贴完成后执行 `save` → `y` 保存。

## 粘贴时的两个注意点

- **接口名要与实际设备一致**。本仓库以 `GE1/0/0`、`GE0/0/1` 这类名字书写，
  若你的 eNSP 版本防火墙显示为 `GE0/0/x`，只需把 `FW1.txt` 里的接口名整体替换。
- **命令报错不一定是配置错**。少数命令在不同 VRR 版本上不支持（例如老版本
  USG5500 的 `security-policy` 视图），跳过该段并记录即可，详见
  `docs/排错记录.md` 与 `docs/网络规划与验证说明.md` 的注意事项一节。

## 与脚本的关系

这些 `.txt` 由 `tools/lab_configs.py` 定义、`tools/build_lab.py` 生成。
**建议改配置时改 `lab_configs.py` 再重新生成**，不要直接手改 `.txt`，
否则下次生成会被覆盖。
