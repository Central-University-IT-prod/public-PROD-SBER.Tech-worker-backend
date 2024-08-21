from pydantic import BaseModel
from uuid import UUID


class MeetSchema(BaseModel):
    meet_id: UUID


class RepresentativeScheme(BaseModel):
    representative_id: int | None


class MeetResultScheme(BaseModel):
    meet_id: UUID
    success: bool


class PointSchema(BaseModel):
    latitude: float
    longtitude: float
