# Discourse 平台案例

Discourse 案例用于证明：论坛 topic/post 也可以作为 ChatRSS 的事件来源。它比实时聊天更适合作为长期讨论、任务记录和决策沉淀空间。

![Discourse RexWang 对话证据截图](../assets/platform-cases/discourse-rexwang-conversation.png)

## 当前验证状态

| 字段 | 值 |
| --- | --- |
| 平台 | Discourse |
| Public URL | https://discourse.public.lookeng.cn |
| Category | `Agent Runs` |
| Actor | `RexWang` / user id `4` / 普通用户 |
| Agent/action account | `ark-code-latest1` |
| Actor post | https://discourse.public.lookeng.cn/t/chatrss-discourse-trigger-practice-2026-08-05-0259-utc/18/1 |
| Reply post | https://discourse.public.lookeng.cn/t/chatrss-discourse-trigger-practice-2026-08-05-0259-utc/18/2 |
| Trigger marker | `chatrss-discourse-trigger-20260805022954` |
| Event id | `discourse:post:25:mention:system` |
| Action | `discourse.post.reply` |
| Evidence screenshot | `docs/assets/platform-cases/discourse-rexwang-conversation.png` |

## 触发机制

```text
RexWang 在 Discourse Agent Runs 分类创建 topic/post 并 @system
  -> Discourse 产生真实 post
  -> discourse.posts watcher 读取 topic/post metadata 与正文
  -> connector 标准化为 TriggerEvent
  -> router 判定 act
  -> action account 用 Discourse 写真实 reply
  -> 登录态/API/服务端回读确认 post 与 reply 存在
```

这里的 **前置动作** 是 `RexWang 创建/回复一个 Discourse post 并 @system`。行动内容来自 post 正文。

## 标准事件

```json
{
  "source": "discourse",
  "connector": "discourse.posts",
  "event_type": "community.mention.created",
  "event_id": "discourse:post:25:mention:system",
  "subject": {
    "kind": "post",
    "id": 25,
    "topic_id": 18,
    "post_number": 1,
    "category": "Agent Runs"
  },
  "actor": {
    "kind": "user",
    "id": 4,
    "username": "RexWang"
  },
  "payload": {
    "mentions": ["system"],
    "marker": "chatrss-discourse-trigger-20260805022954"
  }
}
```

## 接入方式

Discourse 适合接成 **forum/topic connector**：

1. 监听特定 category、tag、topic、mention 或 notification。
2. 将 topic/post 统一转成 `TriggerEvent`。
3. Router 判断是否需要 agent 处理；外部写动作默认走 `draft -> approve -> execute`，受控实践可直接写回。
4. Action executor 通过 Discourse API / plugin / server-side safe writer 写 reply，并回读验证。

匿名访问 Discourse topic JSON 可能返回 `403` 或只返回 shell；验收时必须用登录态、API key 或服务端 readback，不要把匿名页面不可见误判为事件不存在。
