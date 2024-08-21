from fastapi import APIRouter
from server.routers.schemas.meet import MeetSchema, MeetResultScheme, PointSchema
from server.db.models import MeetResultModel, PointModel
from server.db.repo import meeting_repo

from server.domains.appointments import appoint_meeting

router = APIRouter()


@router.get("/appoint")
async def appoint(meet: MeetSchema):
    meet = await meeting_repo.get_meet_by_id(meet.meet_id)

    if meet is None:
        return None

    meet = await appoint_meeting(meet)

    if meet is None:
        return None

    result = {"representative_id": meet.representative_id}

    return result


@router.post("/meet-result")
async def post_meet_result(meetResult: MeetResultScheme):

    result = MeetResultModel(meetResult.meet_id, meetResult.success)

    await meeting_repo.create_meeting_result(result)

    return {"result": "ok"}


@router.get("/meet-result")
async def get_meet_result(meetResult: MeetResultScheme):

    result = await meeting_repo.get_result_by_meet_id(meetResult.meet_id)

    if result is None:
        return None

    result = MeetResultScheme(meet_id=meetResult.meet_id, success=result)

    return {"result": "ok"}


@router.post("/debug/new-point")
async def debug_new_point(point: PointSchema):
    point = PointModel(point.latitude, point.longtitude)
    point = await meeting_repo.create_point(point)
    return point


@router.post("/debug/clear_cache")
async def debug_appoint():

    await meeting_repo.delete_cache()

    return {"result": "ok"}
