from server.db.models import MeetModel, PointModel, RepresentativeModel, TimeSlot
from server.routers.schemas.meet import MeetSchema
from server.db.repo import meeting_repo

from sqlalchemy.engine.row import Row


async def find_representor(point, meet: MeetModel):
    duration = await meeting_repo.get_meet_duration(meet)

    reprs = await meeting_repo.find_reprs_for_slot(point, meet.datetime, duration)

    for representor in reprs:
        if isinstance(representor, Row):
            representor = representor[0]
        print(
            representor,
            repr(representor),
            isinstance(representor, tuple),
            type(representor),
        )
        assert isinstance(representor, RepresentativeModel)
        if representor is None:
            continue
        if await meeting_repo.is_time_slot_achievable(
            point, representor.id, meet.datetime, duration
        ):
            return representor

    return None


async def appoint_meeting(meet: MeetModel):

    point = PointModel(meet.place_latitude, meet.place_longtitude)

    point = await meeting_repo.create_point(point)

    representor = await find_representor(point, meet)

    if representor is None:
        return None

    duration = await meeting_repo.get_meet_duration(meet)

    slot = TimeSlot(
        point_id=point.id,
        representative_id=representor.id,
        start_time=meet.datetime,
        end_time=meet.datetime + duration,
    )

    await meeting_repo.create_time_slot(slot)

    meet.representative_id = representor.id
    return await meeting_repo.update_meet(meet)
