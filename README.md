<div align="center">
  <h1>✨Re-灵初bot✨</h1>
  <div align="center">
    <a name="readme-logo"><img width="256" height="256" alt="logo" src="docs/assets/logo-clr.svg" /></a>
  </div><br/>


[![][license-shield]][license-link] [![][github-release-shield]][github-release-link] [![][github-stars-shield]][github-stars-link]

![][CodeRabbit-link]

[![][docs-shield]][docs-link] [![zread][zread-shield]][zread-link] [![deepwiki][deepwiki-shield]][deepwiki-link]

![ide-link-1] ![ide-link-2] ![managed-link]

 
</div>

> [!WARNING]
> 🚧Pre-alpha阶段，项目暂不可用🚧
> 
> 最新进展请关注[dev分支](https://github.com/lingchu-bot/lingchu-bot/tree/dev)

<div>

## 简介

灵初bot是一款基于NoneBot2框架开发的QQ管理机器人，旨在为用户提供强大且易用的群管理和互动功能。通过集成多种插件和工具，灵初bot能够帮助群管理员更高效地管理群组，同时为群成员带来丰富的娱乐体验。

#### 功能与生态

<div>
    <h3>核心系统</h3>
    <ul>
        <li>数据库支持: 内置 SQLite 数据库支持,连接池管理,支持多数据库并发访问</li>
        <li>可视化管理: 提供基于Web的可视化管理界面,方便用户配置和监控机器人</li>
        <li>自定义协议: 拓展OneBot11协议,支持自定义事件处理</li>
    </ul>
    <h3>插件系统</h3>
    <ul>
        <li>
            内置插件
            <ul>
                <li>
                    群管理
                    <ul>
                        <li>发言管理</li>
                        <li>成员管理</li>
                        <li>群聊管理</li>
                        <li>定时任务</li>
                    </ul>
                </li>
            </ul>
        </li>
        <li>
            拓展插件
            <ul>
                <li>完全支持 NoneBot2 插件生态,可以无缝安装使用</li>
                <li>提供丰富的插件接口,方便开发者自定义功能</li>
            </ul>
        </li>
    </ul>
</div>


</div>
<div>

# 如何开始

安装 Python (必须)

```bash
https://www.python.org/downloads/latest/python3.13/
```

安装 uv (推荐)

```bash
# 我们使用 uv 管理依赖，也可仅使用Python自带的pip以及其他包管理，但不保证兼容性
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# MacOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装nb-cli (推荐)

```bash
# 生产推荐、使用 pipx ( nonebot 官方使用)
pipx install nb-cli 
# 快速安装pipx:
python -m pip install --user pipx
python -m pipx ensurepath
```

```bash
# 开发推荐、使用 uv （tip: 安装的nb-cli部分功能异常，仅用于不想额外安装pipx的情况）
uv tool install nb-cli 
```

</div>
<div>

## 开始使用

[项目文档](https://lingchu.zone.id/)

## 快速开始

##### 以下操作需在终端执行，且目录无中文字符(带有中文字符可能出现意料之外的错误)

克隆或下载项目到本地

```bash
# 生产克隆
git clone --depth 1 --single-branch --branch main https://github.com/lingchu-bot/lingchu-bot.git
# 开发克隆
git clone --single-branch --branch dev https://github.com/lingchu-bot/lingchu-bot.git
# 生产下载
从本仓库的 Release 发行资产页面获取
# 开发下载
从本仓库的 ci-builds 工作流资产页面获取
```

进入项目目录

```bash
cd lingchu-bot
```

安装项目依赖

```bash
uv sync --no-dev  # 仅安装生产依赖
```
```bash
uv sync  # 安装全部依赖(包含开发和可选依赖)
```

启动项目

```bash
uv run run.py # 启动项目(生产环境)
```

```bash
nb run  # 启动项目(生产环境)
```

```bash
nb run -reload  # 自动重载(开发环境)，参数可缩写为`-r`
```

```bash
uv run zensical serve # 启动文档开发服务器(开发环境)
```

</div>
<div>

## 项目配置

```env
ENVIRONMENT=prod                                     #环境，dev为开发环境，prod为生产环境
HOST=127.0.0.1                                       #主机地址，默认127.0.0.1，公网部署时需修改该值为0.0.0.0
PORT=8080                                            #主机端口，默认8080
ONEBOT_ACCESS_TOKEN=abcd                             #onebot 访问令牌
SUPERUSERS=["12345789","987654321"]                  #超级用户列表，多个用户用逗号分隔
DEFAULT_COMMAND_START=""                             #默认命令前缀，多个前缀用逗号分隔，留空表示无前缀
```

</div>
<div>

## 兼容问题

- 暂无


## 许可证

本项目使用复合许可证，包含 LGPL-3.0 和 GNU FDL。
详细说明请参见[Repository Policy](Repository-Policy.md)。
许可证文本参见[LICENSE-code](LICENSE-code)和[LICENSE-docs](./LICENSE-docs)。

## 感谢

##### 感谢下列项目提供的底层支撑,没有这些项目,本项目就无法实现:

[NoneBot2](https://nonebot.dev/)

[OneBot11](https://11.onebot.dev/)

[nonebot-adapter-onebot](https://github.com/nonebot/adapter-onebot)

[nonebot-plugin-apscheduler](https://github.com/nonebot/plugin-apscheduler)

[nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore)

[nonebot-plugin-orm](https://github.com/nonebot/plugin-orm)

### 本项目依赖下列依赖:

[依赖列表](https://github.com/lingchu-bot/lingchu-bot/network/dependencies)

</div>
<!--
  <div align="center">
    <a name="readme-top"><img src="https://socialify.git.ci/lingchu-bot/lingchu-bot/image?custom_description=%E7%94%B1Nonebot2%E9%A9%B1%E5%8A%A8%E7%9A%84QQ%E7%AE%A1%E7%90%86%E6%9C%BA%E5%99%A8%E4%BA%BA&description=1&font=Inter&forks=1&issues=1&language=1&name=1&owner=1&pattern=Overlapping+Hexagons&pulls=1&theme=Auto" alt="lingchu-bot" width="640" height="320" /></a>
    <a name="readme-banner"><img width="899" height="567" alt="banner" src="https://github.com/user-attachments/assets/db779db0-e2b1-493b-9fa3-0efcac22a2ac" /></a>
  </div>
-->
<div>
<!-- official link -->

[docs-link]: https://lingchu.zone.id/

<!-- Other link-->
[license-link]: https://www.gnu.org/licenses/lgpl-3.0.html
[github-release-link]: https://github.com/lingchu-bot/lingchu-bot/releases/latest
[github-stars-link]: https://github.com/lingchu-bot/lingchu-bot
[managed-link]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json

<!-- Shield link-->
[docs-shield]: https://img.shields.io/badge/Documentation-00b0aa
[github-release-shield]: https://img.shields.io/github/v/release/lingchu-bot/lingchu-bot
[github-stars-shield]: https://img.shields.io/github/stars/lingchu-bot/lingchu-bot?color=%231890FF&style=flat-square
[license-shield]: https://img.shields.io/github/license/lingchu-bot/lingchu-bot
[zread-shield]: https://img.shields.io/badge/Ask_Zread-_.svg?style=plastic&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff
[zread-link]: https://zread.ai/lingchu-bot/lingchu-bot
[deepwiki-shield]: https://img.shields.io/badge/Ask_DeepWiKi-_.svg?style=plastic&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff
[deepwiki-link]: https://deepwiki.com/lingchu-bot/lingchu-bot
[CodeRabbit-link]: https://img.shields.io/coderabbit/prs/github/lingchu-bot/lingchu-bot?utm_source=oss&utm_medium=github&utm_campaign=lingchu-bot%2Flingchu-bot&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews
[ide-link-1]: https://img.shields.io/badge/IDE-Visual%20Studio%20Code-blue?style=flat&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/PjwhRE9DVFlQRSBzdmcgUFVCTElDICItLy9XM0MvL0RURCBTVkcgMS4xLy9FTiIgImh0dHA6Ly93d3cudzMub3JnL0dyYXBoaWNzL1NWRy8xLjEvRFREL3N2ZzExLmR0ZCI+PHN2ZyB0PSIxNzI4MTA5NDQzMzg2IiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjU5OTAiIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB3aWR0aD0iMjQiIGhlaWdodD0iMjQiPjxwYXRoIGQ9Ik03MjUuMzMzMzMzIDcwMi43MlYzMTUuMzA2NjY3bC0yNTYgMTkzLjcwNjY2Nk05NC43MiAzOTIuMTA2NjY3YTM2LjYwOCAzNi42MDggMCAwIDEtMC44NTMzMzMtNDkuMDY2NjY3bDUxLjItNDcuMzZjOC41MzMzMzMtNy42OCAyOS40NC0xMS4wOTMzMzMgNDQuOCAwbDE0NS45MiAxMTEuMzYgMzM4LjM0NjY2Ni0zMDkuMzMzMzMzYzEzLjY1MzMzMy0xMy42NTMzMzMgMzcuMTItMTkuMiA2NC01LjEybDE3MC42NjY2NjcgODEuNDkzMzMzYzE1LjM2IDguOTYgMjkuODY2NjY3IDIzLjA0IDI5Ljg2NjY2NyA0OS4wNjY2Njd2NTc2YzAgMTcuMDY2NjY3LTEyLjM3MzMzMyAzNS40MTMzMzMtMjUuNiA0Mi42NjY2NjZsLTE4Ny43MzMzMzQgODkuNmMtMTMuNjUzMzMzIDUuNTQ2NjY3LTM5LjI1MzMzMyAwLjQyNjY2Ny00OC4yMTMzMzMtOC41MzMzMzNsLTM0Mi4xODY2NjctMzExLjQ2NjY2Ny0xNDUuMDY2NjY2IDExMC45MzMzMzRjLTE2LjIxMzMzMyAxMS4wOTMzMzMtMzYuMjY2NjY3IDguMTA2NjY3LTQ0LjggMGwtNTEuMi00Ni45MzMzMzRjLTEzLjY1MzMzMy0xNC4wOC0xMS45NDY2NjctMzcuMTIgMi4xMzMzMzMtNTEuMmwxMjgtMTE1LjIiIGZpbGw9IiNmZmZmZmYiIHAtaWQ9IjU5OTEiPjwvcGF0aD48L3N2Zz4=
[ide-link-2]: https://img.shields.io/badge/IDE-PyCharm-green?style=flat&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMjEgMTVjMCAxLjY1Ny0xLjM0MyAzLTMgM3MtMy0xLjM0My0zLTNzMS4zNDMtMyAzLTNzMyAxLjM0MyAzIDN6TTMgMTVjMCAxLjY1NyAxLjM0MyAzIDMgM3MzLTEuMzQzIDMtM3MtMS4zNDMtMy0zLTNzLTMgMS4zNDMtMyAzem0xMy42LTguOGwtLjQgMi40LTYuNC02LjQgMi40LS40IDQuOCA0LjggNC44LTQuOHoiPjwvcGF0aD48L3N2Zz4=

</div>
