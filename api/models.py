from django.db import models


class Staff(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    nick_name = models.CharField(max_length=100, blank=True, default='')
    name = models.CharField(max_length=100, blank=True, default='')
    open_id = models.CharField(max_length=100, blank=True, default='')
    staff_id = models.CharField(max_length=10, blank=False, default='0000000000', primary_key=True)
    winning = models.BooleanField(default=False)
    times = models.IntegerField(default=3)
    prize = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ('created',)


class ProcessingStaff(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, default='')
    open_id = models.CharField(max_length=100, blank=True, default='')
    staff_id = models.CharField(max_length=10, blank=False, default='0000000000', primary_key=True)

    class Meta:
        ordering = ('created',)


class Activity(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    activity_id = models.CharField(max_length=3, blank=False, default='000', primary_key=True)
    activity_name = models.CharField(max_length=100, blank=True, default='')
    activity_memo = models.CharField(max_length=200, blank=True, default='')
    processing = models.BooleanField(default=False)
    prize = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ('created',)


class Prize(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    prize_id = models.CharField(max_length=3, blank=False, default='000', primary_key=True)
    prize_name = models.CharField(max_length=100, blank=True, default='')
    prize_memo = models.CharField(max_length=200, blank=True, default='')
    distribution = models.BooleanField(default=False)

    class Meta:
        ordering = ('created',)


class Empty1(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=3, blank=False, default='000', primary_key=True)

    class Meta:
        ordering = ('created',)


class Empty2(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    id = models.CharField(max_length=3, blank=False, default='000', primary_key=True)

    class Meta:
        ordering = ('created',)
