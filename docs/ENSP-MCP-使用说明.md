# 用 ENSP-MCP 插件操作本实验

## 1. 为什么需要它

eNSP 是个 Windows GUI 程序，批量配置只能靠"点开设备窗口 → 粘贴 → 保存"重复十几次。
但 eNSP 会给**每台网络设备开一个本地控制台端口**（默认 2000 起，本质是串口转 TCP），
所以只要能连上这些端口，就能像坐进串口一样下发命令、读回显，完全不碰界面。

**ENSP-MCP** 就是把这件事做成标准工具的开源项目：

- 项目：<https://github.com/dawnight0x/ENSP-MCP>
- 语言：Python（3.11–3.13）
- 形态：MCP 服务器（stdio）+ 浏览器版拓扑查看器
- 能力：设备自动发现、单条命令执行、批量下发配置、保存配置、健康检查、
  Ping/Traceroute、解析 `.topo` 拓扑

## 2. 安装

依赖 [uv](https://docs.astral.sh/uv/)：

```powershell
git clone https://github.com/dawnight0x/ENSP-MCP.git
cd ENSP-MCP
uv sync            # 若 lockfile 过期用 uv sync，不带 --locked
```

> 实测：本机 `uv sync --locked` 会报 "lockfile needs to be updated"，
> 去掉 `--locked` 即可，会重新解析并安装 76 个依赖。

## 3. 启动

```powershell
uv run python -m ensp_mcp_server.server
```

启动后除了 MCP 服务，还会拉起拓扑查看器：<http://127.0.0.1:18080/index.html>

## 4. 在本实验上的用法

### 4.1 先让插件知道有哪些设备

三种方式，任选其一：

| 方式 | 做法 | 适用场景 |
|---|---|---|
| 自动发现 | 调用 `auto_discover` | eNSP 已打开并启动设备，最省事 |
| 手动注册 | `register_device(name="LSW3", port=2004)` | 只想操作个别设备 |
| 导入拓扑 | 在 Web UI 上传本仓库的 `.topo` | eNSP 没开，只想看结构 |

本实验的端口已经解析好，直接查表即可（详见 [拓扑解析.md](拓扑解析.md)）：

| 设备 | 端口 | 设备 | 端口 | 设备 | 端口 |
|---|---|---|---|---|---|
| FW1 | 2000 | LSW2 | 2001 | DHCP | 2002 |
| AC1 | 2003 | LSW3 | 2004 | LSW4 | 2005 |
| LSW1 | 2006 | AP1 | 2007 | AR1 | 2008 |
| AR2 | 2009 | AR3 | 2010 | LSW6 | 2011 |
| AR4 | 2012 | LSW5 | 2013 | | |

终端设备（PC1–PC5、Server1/2、Client1/2、STA1）**没有 CLI**，无控制台端口，属正常。

### 4.2 典型操作

接好 MCP 客户端后，用自然语言即可，插件会映射到具体工具：

| 我想做什么 | 说的话 | 背后调用的工具 |
|---|---|---|
| 看 LSW3 的 VRRP 状态 | "查一下 LSW3 的 VRRP" | `execute_cli` |
| 把配置刷到 13 台设备 | "把这些配置下发下去" | `push_config` / `multi_device_push_config` |
| 保存配置 | "保存所有设备配置" | `save_config` |
| 全网点检 | "检查所有设备健康状态" | `multi_health_check` |
| 从 AR4 ping 分支终端 | "AR4 ping 一下 192.168.110.10" | `ping_from_device` |
| 导入拓扑 | "解析这个 .topo" | `discover_topology` |

注意：批量下发前插件会**先校验全部设备和命令**，遇到拒绝或超时会停止后续并报告
"已确认 / 失败 / 未执行"三段状态；已经生效的配置不会自动回滚。

## 5. 本机的实测结论

在 eNSP V1.3.00.100 上验证过（2026-11-04）：

- `discover_topology` 解析本仓库拓扑：**24 台设备、24 条链路**，与文件内容一致
- 解析出的 14 个控制台端口，与上一轮登录真机时记录的端口 **14/14 完全一致**
  （对比表见 [拓扑解析.md](拓扑解析.md) 第 3 节）
- 生成的机器可读拓扑见 [topology.json](topology.json)

这带来一个实用结论：**`.topo` 里的 `com_port` 是稳定的**，
写自动化脚本可以直接照它取端口，不必每次打开 eNSP 手工查串口号。

## 6. 局限

- **需要 MCP 客户端**才能发挥全部能力（Claude Desktop / Claude Code / Cursor 等）；
  没有客户端时只能当普通的拓扑解析库用。
- **不能操作终端设备**：PC 的 `ipconfig`、Client 的浏览器访问都在 GUI 里，
  插件和任何控制台方案都碰不到，这部分只能人工截图。
- **不解决镜像差异**：本实验遇到的 USG5500 无源 NAT、AR2220 不支持 `portswitch`
  属于 eNSP 镜像限制，与本插件无关，详见 [排错记录.md](排错记录.md) 问题六、七。
- 插件只管"下发与查看"，**不管规划一致性**。地址是否冲突、VRRP 与 DHCP 网关是否对得上，
  仍由本仓库 `tools/check_lab.py` 负责校验。

## 7. 与本仓库自带脚本的分工

| | ENSP-MCP 插件 | 本仓库 `tools/` |
|---|---|---|
| 定位 | 交互式、AI 驱动、通用 | 面向本实验、批处理、可复现 |
| 依赖 | 需要 MCP 客户端 + uv + 插件仓库 | 只需 Python 标准库 |
| 适合 | 边看边改、排障、探索 | CI/回归、一键重建拓扑与配置 |
| 校验 | 无 | `check_lab.py` 交叉校验 |

两者互补：先用 `tools/` 保证规划自洽，再用插件做现场操作。
