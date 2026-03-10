# coding:utf-8

import functools
import json
import logging
import requests as rq

from typing import TypeVar, Callable, Optional

from .config import Config
from .model import PluginTriggerReq, AbilityTriggerReq, AbilityTriggerResp, PluginTriggerData, BaseResp, \
    PluginTriggerResp, EvaluateIDType, GetEvaluateIDsResp, AbilityTriggerRespData

logger = logging.getLogger(__name__)

T = TypeVar("T")


def evalbot_api_call(method: Callable[..., T]) -> Callable[..., Optional[T]]:
    """
    wraps a method returning a Evalbot API response.
      - Catch exceptions,
      - Check if the response is successful,
      - Log errors when needed,
      - Return the successful response or None on failure.
    """

    @functools.wraps(method)
    def wrapper(*args, **kwargs) -> Optional[T]:
        self = args[0]
        cur_logger = getattr(self, "_logger", logging.getLogger(__name__))
        if not cur_logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            cur_logger.addHandler(handler)
        cur_logger.setLevel(logging.INFO)
        cur_logger.propagate = False

        try:
            cur_logger.info("Start Evalbot API call")
            response: T = method(*args, **kwargs)
        except Exception as e:
            cur_logger.error("Evalbot Exception: %s", str(e))
            return None

        if not hasattr(response, "base"):
            return None
        base: BaseResp = getattr(response, "base")
        cur_logger.info("Evalbot API call. code: %d, msg: %s, log_id: %s\nResponse:\n%s",
                        base.ret, base.error_msg, base.log_id, response.model_dump_json())
        return response

    return wrapper


class EvalbotClient:
    def __init__(self, config: Config):
        self.__config = config
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

    @evalbot_api_call
    def get_evaluate_ids(self, id_type: EvaluateIDType, id_key: str) -> GetEvaluateIDsResp:
        url = f"https://evalbot.zijieapi.com/evaluate/get_ids?id_type={id_type.value}&id_key={id_key}"
        response = rq.get(url, headers={"Authorization": f"Bearer {self.__config.user_access_token}"}).json()
        return GetEvaluateIDsResp(**response)

    @evalbot_api_call
    def ability_trigger(self, req: AbilityTriggerReq) -> AbilityTriggerResp:
        response = AbilityTriggerResp()
        with rq.post("https://evalbot.zijieapi.com/evaluate/ability/trigger",
                     headers={"Authorization": f"Bearer {self.__config.user_access_token}"},
                     json=req.model_dump(),
                     stream=True) as resp:
            response.base = BaseResp(ret=0, error_msg="", log_id=resp.headers.get("Trace_id", ""))
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if not line or "data" not in line:
                    continue
                resp_data = line.lstrip("data: ")
                response.data = AbilityTriggerRespData(**json.loads(resp_data))
                return response
        return response

    @evalbot_api_call
    def plugin_trigger(self, req: PluginTriggerReq) -> PluginTriggerResp:
        response = PluginTriggerResp()
        with rq.post("https://evalbot.zijieapi.com/evaluate/plugin/trigger",
                     headers={"Authorization": f"Bearer {self.__config.user_access_token}"},
                     json=req.model_dump(),
                     stream=True) as resp:
            response.base = BaseResp(ret=0, error_msg="", log_id=resp.headers.get("Trace_id", ""))
            resp.raise_for_status()
            tmp = {}
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                # 每一个 event 按照 id: int 起始
                if "id" in line and tmp:
                    response.data.append(PluginTriggerData(**tmp))
                    tmp = {}
                split_data = line.split(": ")
                tmp[split_data[0]] = split_data[1]
            if tmp:
                response.data.append(PluginTriggerData(**tmp))
        return response
