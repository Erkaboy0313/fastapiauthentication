from tortoise.models import Model
from tortoise.fields import IntField,CharField


class User(Model):
    id = IntField(pk=True)
    username = CharField(max_length=200)
    first_name = CharField(max_length=200)
    last_name = CharField(max_length=200)
    phone = CharField(max_length=200)
    password = CharField(max_length=200)

    def __str__(self):
        return self.username