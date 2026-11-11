from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

class ProjectFields(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    technologies: list[Annotated[str, Field(min_length=1, max_length=50)]] = Field(min_length=1, max_length=20)


class ProjectCreate(ProjectFields):
    pass


class ProjectUpdate(ProjectFields):
    pass


class Project(ProjectFields):
    # Our database returns SWLAlchemy model objects, not ordinary dictionaries. This setting allows Pydantic to read their attributes and serialize them into the API response.
    model_config = ConfigDict(from_attributes=True)

    id: int
