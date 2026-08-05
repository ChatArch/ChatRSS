# Zulip 平台案例

Zulip 案例用于证明：**用户先在聊天平台做一个前置动作，然后 ChatRSS 才从平台事件中提取行动内容**。

![Zulip RexWang 对话证据截图](../assets/platform-cases/zulip-rexwang-conversation.png)

## 当前验证状态

| 字段 | 值 |
| --- | --- |
| 平台 | Zulip |
| Public URL | https://zulip.public.lookeng.cn |
| Stream / Topic | `chatrss-quickstart` / `trigger-router-action` |
| Actor | `RexWang` |
| Watcher | `ChatRSS Watcher Bot` |
| Action bot | `ChatRSS Agent Bot` |
| Trigger message | https://zulip.public.lookeng.cn/#narrow/channel/chatrss-quickstart/topic/trigger-router-action/near/24 |
| Reply message | https://zulip.public.lookeng.cn/#narrow/channel/chatrss-quickstart/topic/trigger-router-action/near/25 |
| Event id | `zulip:message:24:mention:watcher@example.invalid` |
| Action | `zulip.message.reply` |
| Evidence screenshot | `docs/assets/platform-cases/zulip-rexwang-conversation.png` |

## 触发机制

```text
RexWang 在 Zulip stream/topic 中 @ ChatRSS Watcher Bot
  -> Zulip 产生真实 message event
  -> watcher 用自己的 API key 读取消息并看到 flags=[mentioned]
  -> connector 标准化为 TriggerEvent
  -> router 判定 act
  -> action bot 在同一 topic 中真实回帖
  -> ledger 记录完整因果链
```

这里的 **前置动作** 是 `RexWang @ ChatRSS Watcher Bot`。行动内容来自这条 Zulip message 的正文，而不是 agent 私下收到隐藏指令。

## 标准事件

```json
{
  "source": "zulip",
  "connector": "zulip.messages",
  "event_type": "community.mention.created",
  "event_id": "zulip:message:24:mention:watcher@example.invalid",
  "actor": {
    "type": "zulip_user",
    "display_name": "RexWang"
  },
  "subject": {
    "type": "zulip.message",
    "stream": "chatrss-quickstart",
    "topic": "trigger-router-action",
    "message_id": 24
  },
  "raw": {
    "mentioned": true,
    "flags": ["mentioned"]
  }
}
```

## 接入方式

Zulip 适合接成 ChatRSS 的 **chat/community connector**：

1. 用 watcher/bot account 的 API key 读取指定 stream/topic 或 event queue。
2. 只把符合规则的消息转成 `TriggerEvent`，例如 `mentioned=true`。
3. Router 再判断是否要执行 `agent.run` 和 `zulip.message.reply`。
4. action bot 负责真实回帖，watcher 负责读事件，两者权限分离。

Zulip 不需要先转成 RSSHub 才能工作；RSSHub 更适合 issue/feed 类来源。Zulip 的直接 API connector 更自然。
