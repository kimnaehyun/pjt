# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # 기본적인 유저 정보
    age = models.PositiveIntegerField(null=True, blank=True)  # 나이
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], null=True, blank=True)  # 성별
    occupation = models.CharField(
        max_length=20, 
        choices=[('student', '학생'), ('unemployed', '무직'), ('employed', '직장인'), ('housewife', '주부')], 
        null=True, blank=True
    )  # 직업 (학생, 무직, 직장인, 주부 선택)
    interests = models.TextField(null=True, blank=True)  # 관심사

    def __str__(self):
        return self.username