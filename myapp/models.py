from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# User(회원 테이블)
class User(models.Model):
    user_id = models.AutoField(primary_key=True)  # 기본 키, 자동 증가하는 고유 값
    email = models.EmailField(unique=True)  # 이메일 주소, 로그인 시 사용되며 중복을 허용하지 않음
    password = models.CharField(max_length=100)  # 비밀번호, 최대 길이 100. 비밀번호는 해싱해서 저장
    name = models.CharField(max_length=100)  # 사용자 이름
    birth_date = models.DateField(null=True, blank=True)  # 생일, null=True는 비워둘 수 있음을 의미, blank=True는 폼에서 공백 가능
    phone_number = models.CharField(max_length=15, unique=True)  # 전화번호, 최대 15자, 중복 방지
    is_active = models.BooleanField(default=True)  # 활성화 상태, 기본값은 True
    created_at = models.DateTimeField(auto_now_add=True)  # 계정 생성 시간, 객체가 처음 저장될 때 자동으로 현재 시간 설정
    updated_at = models.DateTimeField(auto_now=True)  # 계정 정보 수정 시간, 객체가 저장될 때마다 자동으로 현재 시간 설정

    def set_password(self, *args, **kwargs):
        """비밀번호 해싱 처리"""
        if not self.password.startswith('pbkdf2_sha256$'):  # 이미 해싱된 경우 중복 해싱 방지
            self.password = make_password(self.password)  # 비밀번호를 안전한 방식으로 해싱하여 저장
        super().save(*args, **kwargs)  # 부모 클래스의 save() 메서드 호출

    def check_password(self, raw_password):
        """비밀번호 검증"""
        return check_password(raw_password, self.password)  # 사용자가 입력한 비밀번호와 저장된 해시된 비밀번호를 비교하여 검증

    def __str__(self):
        return self.name  # 객체를 출력할 때 사용자 이름을 반환


# Schedule(업무 일정 테이블)
class Schedule(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),  # 'pending' 상태 - 대기 중
        ('in_progress', 'In Progress'),  # 'in_progress' 상태 - 진행 중
        ('completed', 'Completed'),  # 'completed' 상태 - 완료됨
    ]

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ]

    schedule_id = models.AutoField(primary_key=True)  # 기본 키, 자동 증가하는 고유 값
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User 모델과의 관계 설정, 사용자가 삭제되면 관련 일정도 삭제
    title = models.CharField(max_length=255)  # 일정 제목, 최대 255자
    description = models.TextField(blank=True)  # 일정 설명, 빈 값 가능
    start_time = models.DateTimeField()  # 일정 시작 시간
    end_time = models.DateTimeField()  # 일정 종료 시간
    priority = models.CharField(max_length=50, choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')])  # 일정 우선순위 (High, Medium, Low 중 선택)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # 업무 진행 상태 (기본값은 'pending')
    created_at = models.DateTimeField(auto_now_add=True)  # 일정 생성 시간, 자동으로 현재 시간 설정
    updated_at = models.DateTimeField(auto_now=True)  # 일정 수정 시간, 저장될 때마다 자동으로 현재 시간 설정

    def __str__(self):
        return self.title  # 객체를 출력할 때 일정 제목을 반환


# Note(메모 테이블)
class Note(models.Model):
    note_id = models.AutoField(primary_key=True)  # 기본 키, 자동 증가하는 고유 값
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)  # 일정과의 관계 설정, 일정 삭제 시 관련 메모도 삭제
    content = models.TextField()  # 메모 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 메모 생성 시간, 자동으로 현재 시간 설정
    updated_at = models.DateTimeField(auto_now=True)  # 메모 수정 시간, 저장될 때마다 자동으로 현재 시간 설정

    def __str__(self):
        return f"Note for {self.schedule.title}"  # 객체를 출력할 때 관련 일정 제목을 반환


# AI_Feedback(AI 분석 결과 저장 테이블)
class AI_Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)  # 기본 키, 자동 증가하는 고유 값
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)  # 일정과의 관계 설정, 일정 삭제 시 관련 피드백도 삭제
    feedback = models.TextField()  # AI 분석 피드백 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 피드백 생성 시간, 자동으로 현재 시간 설정
    updated_at = models.DateTimeField(auto_now=True)  # 피드백 수정 시간, 저장될 때마다 자동으로 현재 시간 설정

    def __str__(self):
        return f"Feedback for {self.schedule.title}"  # 객체를 출력할 때 관련 일정 제목을 반환
