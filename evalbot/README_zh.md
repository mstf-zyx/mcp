# Evalbot MCP Server

[English](README.md) | 简体中文

## 工具

提示：你可以在找到所有参数定义——<https://bytedance.larkoffice.com/sheets/Ex0IsHwlLhqxgStXRbLcgTC6nDc>

1. `data_generation`
   - 生成模型评估数据
   - 必需参数：
     - `generate_type` (str): 生成数据的类型，目前仅支持 `hot_topic`
     - `params` (dict\[str, str]): 生成数据的参数，支持的参数：
       ```
       "top_n": 获取前 N 个热门话题
       ```
   - 返回值：Optional\[str | List\[str]]: 错误信息或生成的数据列表
2. `model_evaluation`
   - 评估模型
   - 必需参数：
     - `evaluate_type` (str): 评估类型，支持的值：
       ```
       "knowledge-instruction_following": 需要 location, scene, query, reply
       "knowledge-scalable-comprehensive_key_points": 需要 scene, query, reply
       "knowledge-authentic_and_accurate-general": 需要 base_time, query, reply
       "knowledge-richness": 需要 query, reply
       "knowledge-gsb-compare": 需要 query, domain, reply_a, reply_b, evaluation_criteria
       ```
     - `params` (dict\[str, str]): 评估参数字典，允许的键取决于 `evaluate_type`：
       ```
       location: 用户输入的地理位置，如 "深圳 xx"
       scene: 用户输入查询所属的场景，如 "知识问答 - 本地生活"
       query: 用户输入
       reply: 用户输入的回复，如 "今天气温28度..."
       base_time: 定义评估任务的测试验证时间，如 "2025-10-11"
       domain: 用户输入查询所属的领域，如 "教育"
       reply_a: 用户输入的多个回复
       reply_b: 用户输入的多个回复
       evaluation_criteria: 评估标准
       ```
   - 返回值：Optional\[str | AbilityTriggerRespData]: 错误信息或模型评估结果

## 配置

1. 获取 User-Access-Token

   访问 Evalbot 官网获取 token：<https://evalbot.bytedance.com>
2. 选择连接方式

   **注意**：将 `User-Access-Token` 替换为第1步获取的实际 token。
   ### 方式一：远程 MCP（推荐）
   直接通过 HTTP 使用我们托管的 MCP 服务器：

   **Claude Desktop 配置：**
   ```json
   {
     "mcpServers": {
       "evalbot": {
         "url": "https://evalbot.zijieapi.com/mcp/",
         "headers": {
           "Authorization": "Bearer User-Access-Token"
         }
       }
     }
   }
   ```
   **通用 MCP 客户端：**
   ```python
   from mcp import ClientSession
   from mcp.client.streamable_http import streamable_http_client

   async with streamable_http_client(
       url="https://evalbot.zijieapi.com/mcp/",
       headers={"Authorization": "Bearer User-Access-Token"}
   ) as session:
       await session.initialize()
       # 使用 session...
   ```
   ### 方式二：本地 MCP 服务器
   使用以下命令在本地运行服务器：
   ```bash
   uvx --from git+https://github.com/mstf-zyx/mcp@main#subdirectory=evalbot \
       mcp-server-evalbot \
       --transport streamable-http \
       --token User-Access-Token
   ```
   **Claude Desktop 集成：**
   ```json
   {
     "mcpServers": {
       "evalbot": {
         "command": "uvx",
         "args": [
           "--from",
           "git+https://github.com/mstf-zyx/mcp@main#subdirectory=evalbot",
           "mcp-server-evalbot",
           "--transport",
           "streamable-http",
           "--token",
           "User-Access-Token"
         ]
       }
     }
   }
   ```

