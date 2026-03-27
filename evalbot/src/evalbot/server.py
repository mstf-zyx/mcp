# coding:utf-8

import argparse
import json
import logging
import os

from typing import List, Optional
from mcp.server.fastmcp import FastMCP, Context
from starlette.requests import Request

from .config import load_config
from .client import EvalbotClient
from .model import PluginTriggerReq, TriggerDataEvent, AbilityTriggerReq, EvaluateIDType, \
    AbilityTriggerRespData

logger = logging.getLogger(__name__)

config = None
evalbot_client: Optional[EvalbotClient] = None

server = FastMCP(
    "Evalbot-Server",
    host=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_SERVER_PORT", "8000")),
)


def get_token_from_context(ctx: Context) -> Optional[str]:
    """从请求上下文中获取 token，优先使用请求头中的 Authorization"""
    try:
        if ctx.request_context.request and isinstance(ctx.request_context.request, Request):
            auth_header = ctx.request_context.request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                return auth_header[7:]  # 去掉 "Bearer " 前缀
            return auth_header
    except Exception:
        pass
    return None


@server.tool(name="data_generation")
async def data_generation(generate_type: str, params: dict[str, str], ctx: Context) -> Optional[str | List[str]]:
    """Generate Data

    Args:
        generate_type (str): The type for generating data, only support hot_topic currently.
        params (dict[str, str]): The params used to generate data, support key as below.
                                 top_n: target the top n hot topic.

    Returns:
        Optional[str | List[str]]: The error info or the generated data list
    """
    # 获取 token：优先从请求头获取，否则使用启动时传入的兜底 token
    token = get_token_from_context(ctx) or config.user_access_token
    if not token:
        return "Authorization token is required"

    # 根据 generate_type 获取插件 ID
    id_resp = evalbot_client.get_evaluate_ids(EvaluateIDType.PLUGIN, generate_type, token)
    if not id_resp or not id_resp.data:
        return "Invalid generate type"
    # 兜底转换参数名称格式
    resolve_params = dict()
    for k, v in params.items():
        new_k = k if k.startswith("{{") and k.endswith("}}") else "{{" + k + "}}"
        resolve_params[new_k] = v
    # 获取结果
    quantity = min(10, int(params.get("top_n", "1")))
    resp = evalbot_client.plugin_trigger(PluginTriggerReq(id=id_resp.data[0], params=resolve_params, quantity=quantity), token)
    if not resp:
        return "Failed to generate data"
    return [data.data for data in resp.data if data.event == TriggerDataEvent.MESSAGE and data.data]


@server.tool(name="model_evaluation")
async def model_evaluation(evaluate_type: str, params: dict[str, str], ctx: Context) -> Optional[str | AbilityTriggerRespData]:
    """Evaluate Model

    Args:
        evaluate_type (str): The type for evaluating model. Supported values:
                             - "knowledge-instruction_following": Requires keys location, scene, query, reply.
                             - "knowledge-scalable-comprehensive_key_points": Requires keys scene, query, reply.
                             - "knowledge-authentic_and_accurate-general": Requires keys base_time, query, reply.
                             - "knowledge-richness": Requires keys query, reply.
                             - "knowledge-gsb-compare": Requires keys query, domain, reply_a, reply_b, evaluation_criteria.
        params (dict[str, str]): Dictionary of  parameters for the evaluation. The allowed keys depend on `evaluate_type`:
                                 - location: The geographical location entered by the user, such as "Shenzhen xx".
                                 - scene: The scenario to which the user's input query belongs, such as "Knowledge Question - Local Life".
                                 - query: The user input.
                                 - reply: The reply of the user input, such as "It's 28 degrees today...".
                                 - base_time: Define the test verification time for the evaluation task, such as "2025-10-11".
                                 - domain: The domain to which the user's input query belongs, such as "education".
                                 - reply_a: Multiple replies input by the user.
                                 - reply_b: Multiple replies input by the user.
                                 - evaluation_criteria: .


    Returns:
        Optional[str | AbilityTriggerRespData]: The error info or the result for the model evaluation.
    """
    # 获取 token：优先从请求头获取，否则使用启动时传入的兜底 token
    token = get_token_from_context(ctx) or config.user_access_token
    if not token:
        return "Authorization token is required"

    # 根据 evaluate_type 获取指标 ID
    id_resp = evalbot_client.get_evaluate_ids(EvaluateIDType.ABILITY, evaluate_type, token)
    if not id_resp or not id_resp.data:
        return "Invalid evaluate type"
    # 兜底转换参数名称格式
    resolve_params = dict()
    for k, v in params.items():
        new_k = k if k.startswith("{{") and k.endswith("}}") else "{{" + k + "}}"
        resolve_params[new_k] = v
    # 获取结果
    response = evalbot_client.ability_trigger(AbilityTriggerReq(id=id_resp.data[0], params=json.dumps(resolve_params, ensure_ascii=False)), token)
    if not response:
        return "Failed to evaluate model"
    return response.data


def main():
    parser = argparse.ArgumentParser(description="Run the Evalbot MCP Server")
    parser.add_argument(
        "--transport",
        "--t",
        choices=["streamable-http", "stdio"],
        default="streamable-http",
        help="Transport protocol to use (streamable-http or stdio)",
    )
    parser.add_argument(
        "--config",
        "--c",
        default="",
        help="The path to the config file"
    )
    parser.add_argument(
        "--token",
        "--u",
        default=None,
        help="The auth token"
    )

    args = parser.parse_args()

    global config, evalbot_client
    config = load_config(args.config, args.token)
    evalbot_client = EvalbotClient(config)

    server.run(transport=args.transport)
