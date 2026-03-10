# coding:utf-8

import argparse
import json
import logging
import os

from typing import List, Optional
from mcp.server.fastmcp import FastMCP

from .config import load_config
from .client import EvalbotClient
from .model import PluginTriggerReq, TriggerDataEvent, AbilityTriggerReq, EvaluateIDType, \
    AbilityTriggerRespData

logger = logging.getLogger(__name__)

config = None
evalbot_client: Optional[EvalbotClient] = None

server = FastMCP(
    "Evalbot-Server",
    host=os.getenv("MCP_SERVER_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_SERVER_PORT", "8000")),
)


@server.tool(name="data_generation")
async def data_generation(generate_type: str, params: dict[str, str]) -> Optional[str | List[str]]:
    """Generate Data

    Args:
        generate_type (str): The type for generating data, only support hot_topic currently.
        params (dict[str, str]): The params used to generate data, support key as below.
                                 top_n: target the top n hot topic.

    Returns:
        Optional[str | List[str]]: The error info or the generated data list
    """
    # 根据 generate_type 获取插件 ID
    id_resp = evalbot_client.get_evaluate_ids(EvaluateIDType.PLUGIN, generate_type)
    if not id_resp or not id_resp.data:
        return "Invalid generate type"
    # 兜底转换参数名称格式
    resolve_params = dict()
    for k, v in params.items():
        new_k = k if k.startswith("{{") and k.endswith("}}") else "{{" + k + "}}"
        resolve_params[new_k] = v
    # 获取结果
    quantity = min(10, int(params.get("top_n", "1")))
    resp = evalbot_client.plugin_trigger(PluginTriggerReq(id=id_resp.data[0], params=resolve_params, quantity=quantity))
    if not resp:
        return "Failed to generate data"
    return [data.data for data in resp.data if data.event == TriggerDataEvent.MESSAGE and data.data]


@server.tool(name="model_evaluation")
async def model_evaluation(evaluate_type: str, params: dict[str, str]) -> Optional[str | AbilityTriggerRespData]:
    """Evaluate Model

    Args:
        evaluate_type (str): The type for evaluating model. Supported values:
                             - "knowledge-instruction_following": Requires keys location, scene, question, reply.
                             - "knowledge-scalable-comprehensive_key_points": Requires keys scene, question, reply.
                             - "knowledge-authentic_and_accurate-general": Requires keys base_time, question, reply.
                             - "knowledge-richness": Requires keys query, reply.
                             - "knowledge-gsb-compare": Requires keys query, domain, reply_a, reply_b, evaluation_criteria.
        params (dict[str, str]): Dictionary of  parameters for the evaluation. The allowed keys depend on `evaluate_type`:
                                 - location: The geographical location entered by the user, such as "Shenzhen xx".
                                 - scene: The scenario to which the user's input query belongs, such as "Knowledge Question - Local Life".
                                 - question: The user input.
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
    # 根据 evaluate_type 获取指标 ID
    id_resp = evalbot_client.get_evaluate_ids(EvaluateIDType.ABILITY, evaluate_type)
    if not id_resp or not id_resp.data:
        return "Invalid evaluate type"
    # 兜底转换参数名称格式
    resolve_params = dict()
    for k, v in params.items():
        new_k = k if k.startswith("{{") and k.endswith("}}") else "{{" + k + "}}"
        resolve_params[new_k] = v
    # 获取结果
    response = evalbot_client.ability_trigger(AbilityTriggerReq(id=id_resp.data[0], params=json.dumps(resolve_params, ensure_ascii=False)))
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
        help="Transport protocol to use (sse or stdio)",
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
