from django.db import models

from codex.baseerror import LogicError


class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    student_id = models.CharField(max_length=32, unique=True, db_index=True)

    @classmethod
    def get_by_openid(cls, openid):
        try:
            return cls.objects.get(open_id=openid)
        except cls.DoesNotExist:
            raise LogicError('User not found')


class Activity(models.Model):
    name = models.CharField(max_length=128)
    key = models.CharField(max_length=64, db_index=True)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    place = models.CharField(max_length=256)
    book_start = models.DateTimeField(db_index=True)
    book_end = models.DateTimeField(db_index=True)
    total_tickets = models.IntegerField()
    status = models.IntegerField()
    pic_url = models.CharField(max_length=256)
    remain_tickets = models.IntegerField()

    STATUS_DELETED = -1
    STATUS_SAVED = 0
    STATUS_PUBLISHED = 1

    @classmethod
    def get_by_id(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            raise LogicError('Activity not found')


class Ticket(models.Model):
    student_id = models.CharField(max_length=32, db_index=True)
    unique_id = models.CharField(max_length=64, db_index=True, unique=True)
    activity = models.ForeignKey(Activity)
    status = models.IntegerField()

    STATUS_CANCELLED = 0
    STATUS_VALID = 1
    STATUS_USED = 2

    @classmethod
    def get_a_ticket(cls, student_id, unique_id):
        try:
            ticket = cls.objects.get(student_id=student_id, unique_id=unique_id)
            foreignkey = ticket.activity
            res = {
                'activityName': foreignkey.name,
                'place': foreignkey.place,
                'activityKey': foreignkey.key,
                'uniqueId': ticket.unique_id,
                'startTime': int(foreignkey.start_time.timestamp()),
                'endTime': int(foreignkey.end_time.timestamp()),
                'currentTime': 0,
                'status': ticket.status
            }
            return res
        except cls.DoesNotExist:
            raise LogicError('Ticket not found')

    @classmethod
    def get_by_id(cls, unique_id):
        try:
            return cls.objects.get(unique_id=unique_id)
        except cls.DoesNotExist:
            raise LogicError('Ticket not found')

    @classmethod
    def get_by_studentId(cls, student_id):
        try:
            return cls.objects.filter(student_id=student_id)
        except cls.DoesNotExist:
            raise LogicError('Ticket not found')