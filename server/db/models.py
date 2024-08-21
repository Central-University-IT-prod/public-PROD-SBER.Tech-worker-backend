import simplejson
from server.db.settings import Base as BaseModel
from urllib.request import urlopen
from sqlalchemy import (
    Column,
    Integer,
    String,
    Uuid,
    Float,
    ForeignKey,
    DateTime,
    ARRAY,
    TIME,
    Boolean,
)
from datetime import time


class RepresentativeModel(BaseModel):
    __tablename__ = "representatives"

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String)
    surname = Column(String)
    photo_inner_url = Column(String)


class MeetModel(BaseModel):
    __tablename__ = "meets"

    id = Column(Uuid, primary_key=True, unique=True)
    client_id = Column(Integer, nullable=True, default=None)  # None = MVPs
    datetime = Column(DateTime)
    place_address = Column(String)
    place_longtitude = Column(Float)
    place_latitude = Column(Float)
    operations_ids = Column(ARRAY(Integer))
    representative_id = Column(ForeignKey(RepresentativeModel.id), nullable=True)


class OperationsModel(BaseModel):
    __tablename__ = "operations"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    name = Column(String)
    product = Column(String)
    documents = Column(ARRAY(String))
    duration = Column(TIME)


class PointModel(BaseModel):
    __tablename__ = "points"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    longtitude = Column(Float)
    latitude = Column(Float)

    def __init__(self, lat, lng):
        self.longtitude = float(lng)
        self.latitude = float(lat)

    def calculate_time_to(self, lat, lng):
        coord = self.latitude, self.longtitude
        dest_coord = lat, lng
        """ rewrite to yandex api destination matrix
        url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(
            str(coord), str(dest_coord)
        )
        result = simplejson.load(urlopen(url))
        driving_time = result["rows"][0]["elements"][0]["duration"]["value"]
        """
        driving_time = time(hour=1)
        return driving_time


class PointRelation(BaseModel):
    __tablename__ = "point_relations"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    point_id = Column(ForeignKey(PointModel.id))
    target_id = Column(ForeignKey(PointModel.id))
    time = Column(TIME)

    def __init__(self, point: PointModel, target):
        self.point_id = point.id
        self.target_id = target.id
        self.time = point.calculate_time_to(target.latitude, target.longtitude)


class LastReprPoint(BaseModel):
    __tablename__ = "last_repr_meet"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    point_id = Column(ForeignKey(PointModel.id))
    repr_id = Column(ForeignKey(RepresentativeModel.id))
    time_end = Column(DateTime)


class TimeSlot(BaseModel):
    __tablename__ = "time_slots"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    representative_id = Column(ForeignKey(RepresentativeModel.id), nullable=True)
    point_id = Column(ForeignKey(PointModel.id))

    def __init__(self, start_time, end_time, representative_id, point_id):
        self.start_time = start_time
        self.end_time = end_time
        self.representative_id = representative_id
        self.point_id = point_id

    def __str__(self):
        return f"Slot: {self.point_id} from {self.start_time} to {self.end_time} by {self.representative_id}"

    def get_point_id(self):
        return self.point_id


class MeetResultModel(BaseModel):
    __tablename__ = "meet_results"

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    meet_id = Column(ForeignKey(MeetModel.id))
    result = Column(Boolean)

    def __init__(self, meet_id, result):
        self.meet_id = meet_id
        self.result = result
