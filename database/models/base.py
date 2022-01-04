from datetime import datetime
from odmantic import Model

class Base(Model):
    created_at: datetime = datetime.now()