# wui-skills 中文说明

这个仓库放的是给 Agent / 自动化工具使用的 WUI.AI skills。

当前的视频制作 skill 是：

```text
wui-agent-video
```

当用户让 Agent 创建视频、写脚本、做分镜、导出 MP4、查询生成进度，或调用 WUI.AI 视频接口时，使用这个 skill。

## 安装

安装视频 skill 到 Cursor：

```bash
npx @wui-ai/wui-skills install wui-agent-video
```

## 更新

当仓库更新后，执行同一条命令覆盖本地 skill：

```bash
npx @wui-ai/wui-skills install wui-agent-video
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
