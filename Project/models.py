from django.db import models
from django.contrib.auth.models import User

WEEKDAYS = [
    ('Monday','Monday'),('Tuesday','Tuesday'),('Wednesday','Wednesday'),
    ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),
    ('Sunday','Sunday'),
]


class TimeTable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    class_name = models.CharField(max_length=20)
    no_of_days = models.IntegerField()
    no_of_period = models.IntegerField()
    start_time = models.TimeField()
    duration = models.IntegerField()
    no_of_breaks = models.IntegerField()

    def __str__(self):
        return f"{self.class_name} ({self.user.username})"


class Break(models.Model):
    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE)
    break_number = models.IntegerField()
    after_period = models.IntegerField()
    duration = models.IntegerField()


    def __str__(self):
        return f"Break {self.break_number} after Period {self.after_period}"

class TimeSlot(models.Model):
    timetable = models.ForeignKey(TimeTable, on_delete=models.CASCADE)
    weekday = models.CharField(max_length=10, choices=WEEKDAYS)
    slot_number = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)
    subject = models.CharField(max_length=100, blank=True)
    teacher = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return f"{self.weekday} Slot {self.slot_number} - {self.subject} ({'Break' if self.is_break else 'Class'})"

