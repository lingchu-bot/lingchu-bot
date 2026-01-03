from pydantic import BaseModel


class Config(BaseModel):
    sub_plugins: list[str] = []
    core_plugins: list[str] = []
