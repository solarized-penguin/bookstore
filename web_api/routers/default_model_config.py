from pydantic import ConfigDict

default_model_config = ConfigDict(use_enum_values=True, extra="ignore", str_strip_whitespace=True)
