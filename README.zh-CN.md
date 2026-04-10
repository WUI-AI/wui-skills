# wui-skills 中文说明

这个仓库放的是给 Agent / 自动化工具使用的 WUI.AI skills。

当前的视频制作 skill 是：

```text
wui-agent-video
```

当用户让 Agent 创建视频、写脚本、做分镜、导出 MP4、查询生成进度，或调用 WUI.AI 视频接口时，使用这个 skill。

## 安装

推荐全局安装视频 skill：

```bash
npx skills add https://github.com/WUI-AI/wui-skills -g --skill wui-agent-video
```

参数含义：

- `https://github.com/WUI-AI/wui-skills` 是技能仓库地址。
- `--skill wui-agent-video` 表示从这个仓库里选择名为 `wui-agent-video` 的 skill 安装。它不是给 skill 改名。
- `-g` 表示安装到用户全局 skills 目录，让这个 skill 在多个项目里都可用。

如果安装器询问安装方式，优先选择 **Symlink**。Symlink 会让各个 Agent 指向同一份 skill，后续更新更方便。只有在环境不支持软链接时才选择 Copy。

非交互安装可以使用：

```bash
npx skills add https://github.com/WUI-AI/wui-skills -g --skill wui-agent-video -y
```

## 使用

安装后，直接让 Agent 使用 skill 名称：

```text
Use wui-agent-video to turn this idea into a 30-second YouTube Shorts script and storyboard: ...
```

```text
Use wui-agent-video to generate a WUI.AI video and export the MP4.
```

这个 skill 内置了一个脚本，用来跑 WUI Agent Video API 的完整 workflow：

```bash
python scripts/wui_agent_video.py --prompt "Make a 30-second video about ..."
```

运行脚本前需要设置 API token：

```bash
export WUI_AGENT_API_TOKEN="..."
```
