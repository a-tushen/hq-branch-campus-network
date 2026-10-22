# 运行截图

此目录用于存放 eNSP 中的**运行证据截图**。目前为空，建议补齐下面 6 张——
一张有设备指示灯全绿的拓扑截图，比十行文字更能证明"这东西真的跑起来了"。

## 建议截图清单

| 文件名 | 内容 | 怎么截 |
|---|---|---|
| `01-topology-running.png` | 拓扑全景，所有设备图标为绿色（已启动） | eNSP 画布全屏，Win+Shift+S |
| `02-vrrp-master.png` | LSW3 与 LSW4 的 VRRP 主备状态对比 | 两个 CLI 窗口并排，各执行 `display vrrp` |
| `03-dhcp-ipconfig.png` | PC1 与 PC2 自动获取到地址 | 两台 PC 的「命令行」页签并排 |
| `04-nat-server.png` | 公网侧 PC5 浏览器打开 `http://200.1.1.10` | 浏览器地址栏与页面内容一起截 |
| `05-eth-trunk.png` | 分支聚合链路两成员口 Selected | AR4 / LSW5 执行 `display eth-trunk 1` |
| `06-tracert-branch.png` | 分支网关确实在路由器上 | PC3 执行 `tracert 8.8.8.8`，第一跳为 192.168.110.254 |

## 命名与提交要求

- 统一 `01-`、`02-` 前缀，便于 README 按序引用；
- PNG 格式，宽度建议 1600px 左右，单张控制在 500KB 内（过大的图先压缩）；
- 截图中**不要出现与本机相关的信息**（如主机名、真实 IP、桌面其他文件）。

## 截好后在 README 里引用

在 `README.md` 的「验证结果」一节下方加一段：

```markdown
### 运行截图

![拓扑运行状态](docs/screenshots/01-topology-running.png)
![VRRP 主备](docs/screenshots/02-vrrp-master.png)
```

注意：默认的 `.gitignore` 不会忽略 PNG，截图会正常入库。
