# coding:utf-8

import os
import yaml

from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    user_access_token: str


def load_config(file_path: str, input_token: str) -> Config:
    if input_token:
        return Config(user_access_token=input_token)

    if not file_path:
        return Config(user_access_token=os.getenv("USER_ACCESS_TOKEN"))

    try:
        path = Path(file_path)
        return Config(**yaml.safe_load(path.read_text()))
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Config file not found: {file_path}") from e
