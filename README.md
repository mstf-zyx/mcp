# 专项 MCP Server 仓库
## 注意事项
### 1. 单个 MPC Server 单独一个目录
### 2. 编写语言统一为 Python，并且需要支持 [uvx](https://docs.astral.sh/uv/concepts/tools/) 直接启动
### 3. 需要在启动命令中支持通过 --transport/-t  streamable-http 和 --port xxxx 来支持远程访问 [stdio|streamable-http]  (sse 目前社区已经废弃，新建 mcp server，使用 mcp>=1.9.4,  只需要支持 stdio|streamable-http 两种服务实现)，参考PR：https://github.com/volcengine/mcp-server/pull/160/files
### 4. 其他参考：[Lark MCP](https://code.byted.org/machinelearning/mcp/tree/master/server/mcp_server_lark)、[实现规范](https://bytedance.larkoffice.com/wiki/LytvwfEIEijGOxkstlwcUQfYnrh)

## 启动命令
    uvx --from git+https://github.com/mstf-zyx/mcp@分支名#subdirectory=evalbot mcp-server-evalbot \
    --transport streamable-http --token auth_token

