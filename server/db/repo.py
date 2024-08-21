from datetime import timedelta, datetime
from uuid import UUID
from server.config import TIME_GAP, TIME_FREED
from server.db.settings import async_session

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, delete
from server.db.models import (
    LastReprPoint,
    MeetModel,
    PointRelation,
    RepresentativeModel,
    MeetResultModel,
    PointModel,
    TimeSlot,
    OperationsModel,
)


class Repo:

    def __init__(self, connection_provider):
        self.__connection_provider = connection_provider

    async def get_meet_by_id(self, id: UUID):
        async with self.__connection_provider() as session:
            q = select(MeetModel).where(MeetModel.id == id)
            res = (await session.execute(q)).scalar()
            return res

    async def get_free_representors(self, limit=10, offset=0):
        async with self.__connection_provider() as session:

            q = (
                select(RepresentativeModel)
                .where(
                    select(MeetModel.representative_id)
                    .where(MeetModel.datetime >= datetime.now())
                    .where(MeetModel.datetime < datetime.now() + TIME_FREED)
                    .exists()
                    .is_(False)
                )
                .limit(limit)
                .offset(offset)
            )

            res = await session.execute(q)

            res = res.scalars().all()

            return res

    async def update_meet(self, meet: MeetModel) -> MeetModel | None:
        async with self.__connection_provider() as session:
            model_in_db = await session.get(MeetModel, meet.id)

            if model_in_db is None:
                return None

            model = MeetModel(
                id=meet.id,
                client_id=meet.client_id,
                datetime=meet.datetime,
                place_address=meet.place_address,
                place_longtitude=meet.place_longtitude,
                place_latitude=meet.place_latitude,
                operations_ids=meet.operations_ids,
                representative_id=meet.representative_id,
            )

            await session.merge(model)

            await session.commit()

            return await self.get_meet_by_id(model.id)

    async def get_point_by_coordinates(self, lat, lng):
        async with self.__connection_provider() as session:
            q = (
                select(PointModel)
                .where(PointModel.latitude == lat)
                .where(PointModel.longtitude == lng)
            )

            res = (await session.execute(q)).scalar()

            return res

    async def get_all_points(self):
        async with self.__connection_provider() as session:
            q = select(PointModel)

            res = await session.execute(q)
            res = res.scalars().all()
            print(res)
            return res

    async def create_point(self, point: PointModel):
        async with self.__connection_provider() as session:

            db_point = await self.get_point_by_coordinates(
                point.latitude, point.longtitude
            )
            if db_point is not None:
                return db_point

            session.add(point)
            await session.commit()

            points = await self.get_all_points()
            for target in points:
                print("_____\nPoint:")
                print(target is None)
                print()
                if target.id == point.id:
                    continue
                point_relation = PointRelation(point, target)
                target_relation = PointRelation(target, point)
                session.add(point_relation)
                session.add(target_relation)

            await session.commit()

            return point

    async def find_reprs_for_slot(self, point, time, duration):
        async with self.__connection_provider() as session:
            q = (
                select(RepresentativeModel, PointRelation)
                .select_from(RepresentativeModel)
                .where(
                    RepresentativeModel.id.not_in(
                        select(TimeSlot.representative_id)
                        .where(TimeSlot.end_time > time)
                        .where(TimeSlot.start_time < time + duration)
                    )
                )
                .where(PointRelation.target_id == point.id)
                .where(PointRelation.point_id == TimeSlot.point_id)
                .order_by(PointRelation.time)
            )

            res = (await session.execute(q)).all()

            if res == []:
                return await self.get_free_representors()

            return res

    async def is_time_slot_achievable(self, point, repr_id, time, duration):
        async with self.__connection_provider() as session:
            q = (
                select(TimeSlot)
                .where(TimeSlot.representative_id == repr_id)
                .where(TimeSlot.end_time >= time)
            )
            slots = await session.execute(q)

            slots = slots.scalars().all()

            for slot in slots:
                q = select(PointRelation.time).where(
                    PointRelation.target_id == slot.point_id,
                    PointRelation.point_id == point.id,
                )
                res = (await session.execute(q)).scalar()

                if res is None:
                    res = timedelta(0, 0, 0)
                else:
                    res = timedelta(
                        seconds=res.second,
                        minutes=res.minute,
                        hours=res.hour,
                        microseconds=res.microsecond,
                    )

                if slot.start_time < time + res + duration:
                    return False

            return True

    async def get_meet_duration(self, meet: MeetModel):
        async with self.__connection_provider() as session:
            q = select(func.sum(OperationsModel.duration)).where(
                OperationsModel.id.in_(meet.operations_ids)
            )

            res = (await session.execute(q)).scalar()

            return res

    async def create_time_slot(self, time_slot: TimeSlot):
        async with self.__connection_provider() as session:
            session.add(time_slot)
            await session.commit()

    async def create_meeting_result(self, meet_result: MeetResultModel):
        async with self.__connection_provider() as session:
            session.add(meet_result)
            await session.commit()

    async def get_result_by_meet_id(self, meet_id: UUID):
        async with self.__connection_provider() as session:
            q = select(MeetResultModel.result).where(MeetResultModel.meet_id == meet_id)

            res = (await session.execute(q)).scalar()

            return res

    async def delete_cache(self):
        async with self.__connection_provider() as session:
            await session.execute(delete(TimeSlot))
            await session.execute(delete(PointRelation))
            await session.execute(delete(PointModel))
            await session.commit()


meeting_repo = Repo(async_session)
