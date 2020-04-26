import pathlib
from . import UMRLogging
from .UMRType import ChatType, ForwardTypeEnum, DefaultForwardTypeEnum, LogLevel
from pydantic import BaseModel, validator
from typing import Dict, List, Union, Type, Optional, Generic, AnyStr, DefaultDict
from typing_extensions import Literal
import importlib
import yaml
import json

# load config from home directory

__ALL__ = [
    'config',
    'register_driver_config',
    'register_extension_config',
    'reload_config',
    'save_config',
    'load_extensions'
]

logger = UMRLogging.get_logger('Config')


def load_extensions():
    """
    Shared logic for loading both drivers and extensions (import and register only)

    """
    ext_names = config.Extensions
    if ext_names:
        for e in ext_names:
            globals()[e] = importlib.import_module(e)


class BaseDriverConfig(BaseModel):
    Base: str


class BaseExtensionConfig(BaseModel):
    Extension: str


class Default(BaseModel):
    From: str
    To: str
    ToChat: Union[int, str]
    ToChatType: ChatType
    ForwardType: DefaultForwardTypeEnum


class Topology(BaseModel):
    From: str
    FromChat: Union[int, str]
    FromChatType: ChatType
    To: str
    ToChat: Union[int, str]
    ToChatType: ChatType
    ForwardType: ForwardTypeEnum


class ForwardList(BaseModel):
    Topology: Optional[List[Topology]]
    Default: Optional[List[Default]]
    Accounts: Dict[str, Union[int, str]] = {}

    @validator('Topology')
    def generate_empty_list_if_none(cls, v):
        if not v:
            return []
        else:
            return v

    @validator('Default')
    def generate_empty_list_if_none2(cls, v):
        if not v:
            return []
        else:
            return v


def construct_union(modules: List, names):
    eval_string = ', '.join([i.__module__ + '.' + i.__name__ for i in modules])
    if names:
        if eval_string:
            eval_string += ', ' + names.__name__
        else:
            eval_string = names.__name__
    return eval(f'Union[{eval_string}]')


class BasicConfig(BaseModel):
    DataRoot: str = '/root/coolq/data/image'
    LogRoot: str = '/var/log/umr'
    CommandPrefix: str = '!!'
    Extensions: Optional[List[str]]
    BotAdmin: Optional[Dict[str, List[Union[int, str]]]]
    LogLevel: Optional[Dict[str, LogLevel]]

    ForwardList: ForwardList
    Driver: Optional[Dict[str, BaseDriverConfig]]

    ExtensionConfig: Optional[Dict[str, BaseExtensionConfig]]

    @validator('Extensions', pre=True, always=True)
    def generate_empty_list_if_none(cls, v):
        return v or []

    @validator('Driver', pre=True, always=True)
    def generate_empty_dict_if_none(cls, v):
        return v or {}

    @validator('ExtensionConfig', pre=True, always=True)
    def generate_empty_dict_if_none2(cls, v):
        return v or {}

    @validator('BotAdmin', pre=True, always=True)
    def generate_empty_dict_if_none3(cls, v):
        return v or {}

    @validator('LogLevel', pre=True, always=True)
    def generate_empty_dict_if_none4(cls, v):
        return v or {}


home = str(pathlib.Path.home())
config = BasicConfig(**yaml.load(open(f'{home}/.umr/config.yaml'), yaml.FullLoader))

driver_config = []
extension_config = []


def register_driver_config(custom_config):
    driver_config.append(custom_config)


def register_extension_config(custom_config):
    extension_config.append(custom_config)


def reload_config():
    global config

    class FullConfig(BaseModel):
        DataRoot: str = '/root/coolq/data/image'
        LogRoot: str = '/var/log/umr'
        CommandPrefix: str = '!!'
        Extensions: Optional[List[str]]
        BotAdmin: Optional[Dict[str, List[Union[int, str]]]]
        LogLevel: Optional[Dict[str, LogLevel]]

        ForwardList: ForwardList
        Driver: Optional[Dict[str, construct_union(driver_config, BaseDriverConfig)]]

        ExtensionConfig: Optional[Dict[str, construct_union(extension_config, BaseExtensionConfig)]]

        @validator('Extensions', pre=True, always=True)
        def generate_empty_list_if_none(cls, v):
            return v or []

        @validator('Driver', pre=True, always=True)
        def generate_empty_dict_if_none(cls, v):
            return v or {}

        @validator('ExtensionConfig', pre=True, always=True)
        def generate_empty_dict_if_none2(cls, v):
            return v or {}

        @validator('BotAdmin', pre=True, always=True)
        def generate_empty_dict_if_none3(cls, v):
            return v or {}

        @validator('LogLevel', pre=True, always=True)
        def generate_empty_dict_if_none4(cls, v):
            return v or {}

    config = FullConfig(**yaml.load(open(f'{home}/.umr/config.yaml'), yaml.FullLoader))


def save_config():
    yaml.dump(json.loads(config.json()), open(f'{home}/.umr/config.yaml', 'w'), default_flow_style=False)
