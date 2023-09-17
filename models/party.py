from pydantic import BaseModel


class Party(BaseModel):
    date_time: str
    destination: str
    departure: str
    max_recruitment: int
    cur_recruitment: int
    party_type: str
    party_recruiter_id: str
    party_member_id: list[str]
    party_coordinate: list[float]

# class LatLng(BaseModel):
#     Lat: float
#     Lng: float
