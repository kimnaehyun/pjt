from django.contrib.auth.models import AbstractUser
from django.db import models

# 기본 프로필 이미지 선택지
DEFAULT_AVATAR_CHOICES = [
    ('default1', '기본 프로필 1'),
    ('default2', '기본 프로필 2'),
    ('default3', '기본 프로필 3'),
]

class User(AbstractUser):
    # 이메일을 고유 필수 필드로 설정
    email          = models.EmailField(unique=True)
    name           = models.CharField(max_length=100, blank=True, help_text='실명')
    nickname       = models.CharField(max_length=50, blank=True)
    age            = models.PositiveIntegerField(null=True, blank=True)
    phone          = models.CharField(max_length=20, blank=True)
    birthdate      = models.DateField(null=True, blank=True)
    address        = models.TextField(blank=True)
    
    # 업로드된 프로필 이미지 파일
    avatar         = models.ImageField(
        upload_to='avatars/', blank=True, null=True
    )
    default_avatar = models.CharField(
        max_length=50,
        choices=DEFAULT_AVATAR_CHOICES,
        blank=True,
        help_text='기본 프로필 이미지 선택'
    )
    status_message = models.TextField(blank=True)
    
    # 직업, 성별, 관심사 필드 추가
    OCCUPATION_CHOICES = [
        ('student', '학생'),
        ('office', '회사원'),
        ('unemployed', '백수'),
        ('homemaker', '주부'),
        ('jobseeker', '취준생'),
    ]
    GENDER_CHOICES = [
        ('male', '남성'),
        ('female', '여성'),
        ('other', '기타'),
    ]

    occupation = models.CharField(max_length=20, choices=OCCUPATION_CHOICES, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    interests = models.TextField(blank=True, help_text='사용자가 입력한 관심사(자유 텍스트)')
    favorites      = models.ManyToManyField(
        'api.Book', blank=True, related_name='favored_by'
    )
    read_books     = models.ManyToManyField(
        'api.Book', blank=True, related_name='read_by'
    )
    
    # 이메일로 로그인하도록 설정
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # createsuperuser 시 요구되는 필드

    def get_avatar_url(self):
        """
        1) 업로드된 avatar 파일이 있으면 그 URL 반환
        2) 없으면 default_avatar 선택지에 대응하는 정적 파일 경로 반환
        """
        if self.avatar:
            return self.avatar.url
        choice_map = {
            'default1': '/static/avatars/default1.png',
            'default2': '/static/avatars/default2.png',
            'default3': '/static/avatars/default3.png',
        }
        return choice_map.get(self.default_avatar, choice_map['default1'])