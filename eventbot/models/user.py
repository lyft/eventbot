from datetime import datetime
from typing import (
    Any,
    Dict,
    Iterator,
    Optional,
)

from pynamodb.attributes import (
    UnicodeAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.models import Model

from eventbot import settings


class User(Model):

    class Meta:
        table_name = settings.DYNAMODB_TABLE_USER
        if settings.DYNAMODB_URL:
            host = settings.DYNAMODB_URL

    user_id = UnicodeAttribute(hash_key=True)
    venmo_handle = UnicodeAttribute()
    created_date = UTCDateTimeAttribute()
    modified_date = UTCDateTimeAttribute()

    @classmethod
    def get_all_paged(
            cls,
            next_page: Optional[str] = None,
            limit: Optional[int] = None
    ) -> Iterator['User']:
        last_evaluated_key = cls.format_last_evaluated_key(next_page)
        return cls.scan(limit=limit, last_evaluated_key=last_evaluated_key)

    @classmethod
    def format_last_evaluated_key(
            cls,
            user_id: Optional[str]
    ) -> Optional[dict]:
        if user_id is None:
            return None

        return {
            'user_id': {'S': user_id}
        }

    def save(self, *args, **kwargs) -> Dict[str, Any]:
        if not self.created_date:
            self.created_date = datetime.utcnow()
        self.modified_date = datetime.utcnow()
        return super(User, self).save(*args, **kwargs)
