from datetime import datetime
from typing import (
    Any,
    Dict,
    Iterator,
    Optional,
    Text,
)

from pynamodb.attributes import (
    BooleanAttribute,
    ListAttribute,
    NumberAttribute,
    MapAttribute,
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from eventbot import settings


class AttendeeMap(MapAttribute):
    attendee = UnicodeAttribute()


class EventStatusIndex(GlobalSecondaryIndex):

    class Meta:
        index_name = settings.DYNAMODB_GSI_EVENT_STATUS
        read_capacity_units = 10
        write_capacity_units = 10
        if settings.DYNAMODB_URL:
            host = settings.DYNAMODB_URL

        projection = AllProjection()

    event_id = UnicodeAttribute(hash_key=True)
    status = UTCDateTimeAttribute(range_key=True)


class Event(Model):

    STATUS_OPEN = 'open'

    class Meta:
        table_name = settings.DYNAMODB_TABLE_EVENT
        if settings.DYNAMODB_URL:
            host = settings.DYNAMODB_URL

    event_id = UnicodeAttribute(hash_key=True)
    name = UnicodeAttribute()
    description = UnicodeAttribute()
    created_date = UTCDateTimeAttribute()
    modified_date = UTCDateTimeAttribute()
    start_date = UTCDateTimeAttribute(null=True)
    end_date = UTCDateTimeAttribute(null=True)
    status = UnicodeAttribute(default=STATUS_OPEN)
    creator = UnicodeAttribute()
    attendees = ListAttribute(of=AttendeeMap, null=True)
    extra_attendees = NumberAttribute(default=0)
    cost = NumberAttribute(default=0)

    event_status_index = EventStatusIndex()

    @classmethod
    def get_all_paged(
            cls,
            next_page: Optional[str] = None,
            limit: Optional[int] = None
    ) -> Iterator['Event']:
        last_evaluated_key = cls.format_last_evaluated_key(next_page)
        return cls.scan(limit=limit, last_evaluated_key=last_evaluated_key)

    @classmethod
    def format_last_evaluated_key(
            cls,
            event_id: Optional[str]
    ) -> Optional[dict]:
        if event_id is None:
            return None

        return {
            'event_id': {'S': event_id}
        }

    @property
    def total_attendees(self) -> int:
        if self.attendees is None:
            attendees = 0
        else:
            attendees = len(self.attendees)
        return attendees + self.extra_attendees

    @property
    def cost_per_attendee(self) -> int:
        return (self.cost / max(self.total_attendees, 1))

    def user_is_attendee(self, user_id: Text) -> bool:
        if self.attendees is None:
            return False
        for attendee in self.attendees:
            if attendee.attendee == user_id:
                return True
        return False

    def add_attendee(self, user_id: Text) -> None:
        attendee = AttendeeMap()
        attendee.attendee = user_id
        if self.attendees:
            self.attendees.append(attendee)
        else:
            self.attendees = [attendee]

    def remove_attendee(self, user_id: Text) -> None:
        if self.attendees is None:
            return
        # TODO: there must be a more efficient way to do this, right?
        attendees = []
        for attendee in self.attendees:
            if attendee.attendee != user_id:
                attendees.append(attendee)
        self.attendees = attendees

    def save(self, *args, **kwargs) -> Dict[str, Any]:
        if not self.created_date:
            self.created_date = datetime.utcnow()
        self.modified_date = datetime.utcnow()
        return super(Event, self).save(*args, **kwargs)
