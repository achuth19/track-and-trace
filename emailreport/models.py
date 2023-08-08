from django.db import models
import uuid
import datetime
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class User(AbstractUser):
    is_created_product=models.BooleanField(default=False)
    is_subscribed=models.BooleanField(default=False)
    pass

class report(models.Model):
    daily_report=models.BooleanField(default=False)
    weekly_report=models.BooleanField(default=False)
    date_range_report=models.BooleanField(default=False)
    user_details=models.ForeignKey(User,on_delete=models.CASCADE)

class startenddates(models.Model):
    start_date=models.DateField(default=datetime.date.today)
    end_date=models.DateField(default=datetime.date.today)
    user_details=models.ForeignKey(User,on_delete=models.CASCADE)

class entity_list(models.Model):
    entity_name=models.CharField(max_length=100)
    location=models.CharField(max_length=100)
    role=models.CharField(max_length=100)
    user_details=models.ForeignKey(User,on_delete=models.CASCADE)

class product(models.Model):
    product_name=models.CharField(max_length=100)
    totalserials=models.IntegerField(default=0)
    serialscommissioned=models.IntegerField(default=0)
    serialsdecommissioned=models.IntegerField(default=0)
    serialspacked=models.IntegerField(default=0)
    serialsshipped=models.IntegerField(default=0)
    email_duration=models.CharField(max_length=100)
    linked_entity=models.ForeignKey(entity_list,on_delete=models.CASCADE)
    user_details=models.ForeignKey(User,on_delete=models.CASCADE)

class batch(models.Model):
    batch_name=models.CharField(max_length=100)
    linked_product=models.ForeignKey(product,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=0)

class serials(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    linked_product=models.ForeignKey(product,on_delete=models.CASCADE)
    linked_batch=models.ForeignKey(batch,on_delete=models.CASCADE)
    is_commissioned=models.BooleanField(default=False)
    is_packed=models.BooleanField(default=False)
    is_shipped=models.BooleanField(default=False)
    created_date=models.DateField(default=datetime.date.today)
    commissioned_date=models.DateField(default=datetime.date.today)
    packed_date=models.DateField(default=datetime.date.today)
    shipped_date=models.DateField(default=datetime.date.today)
