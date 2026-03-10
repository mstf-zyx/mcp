# coding: utf-8

from enum import Enum
from pydantic import BaseModel
from typing import Optional, List


class BaseResp(BaseModel):
    error_msg: str
    ret: int
    log_id: str


class EvaluateIDType(str, Enum):
    PLUGIN = "plugin"
    ABILITY = "ability"


class GetEvaluateIDsResp(BaseModel):
    base: BaseResp
    data: List[int]


class PluginTriggerReq(BaseModel):
    id: int
    params: dict
    quantity: int


class TriggerDataEvent(str, Enum):
    ACK = "ack"
    TICK = "tick"
    MESSAGE = "message"
    FIN = "fin"


class PluginTriggerData(BaseModel):
    id: int
    event: TriggerDataEvent
    data: Optional[str] = None


class PluginTriggerResp(BaseModel):
    base: Optional[BaseResp] = None
    data: Optional[List[PluginTriggerData]] = []


class AbilityTriggerReq(BaseModel):
    id: int
    params: str
    query: Optional[str] = ""
    eval_str: Optional[str] = ""
    creator: Optional[str] = ""


class AbilityTriggerRespData(BaseModel):
    is_available: bool
    is_expected: bool
    task_id: int
    ability_id: int
    round_idx: int
    eval_pass_result: int
    is_valid: bool
    task_status: str
    eval_ability_type: str
    result_str: str
    extra_info_str: str
    ability_name: str
    query: str
    source_data_id: str


class AbilityTriggerResp(BaseModel):
    base: Optional[BaseResp] = None
    data: Optional[AbilityTriggerRespData] = None
