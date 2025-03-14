from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    # 메인 페이지
    path('', views.main_page, name='main_page'),  # 기본 URL은 main_page 뷰로 연결
    # 사용자 등록
    path('signup/', views.signup, name='signup'),  # /signup/는 signup 뷰로 연결
    # 로그인
    path('login/', views.login_view, name='login'),  # /login/은 login 뷰로 연결
    # 로그아웃
    path('logout/', views.logout_view, name='logout'),
    # 대시보드 (사용자의 일정 목록 조회)
    path('dashboard/', views.dashboard, name='dashboard'),  # 대시보드 URL은 dashboard 뷰로 연결

    # 일정 관련
    path('schedule/create/', views.create_schedule, name='create_schedule'),  # 일정 추가
    path('schedule/update/<int:schedule_id>/', views.update_schedule, name='update_schedule'),  # 일정 수정
    path('schedule/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),  # 일정 삭제

    # 메모 관련
    path('note/create/<int:schedule_id>/', views.create_note, name='create_note'),  # 메모 추가
    path('note/update/<int:note_id>/', views.update_note, name='update_note'),  # 메모 수정
    path('note/delete/<int:note_id>/', views.delete_note, name='delete_note'),  # 메모 삭제

    # AI 피드백 관련
    path('schedule/feedback/<int:schedule_id>/', views.ai_feedback, name='ai_feedback'),  # AI 피드백 생성

    # 비밀번호 확인
    path('check-password/', views.check_user_password, name='check_user_password'),  # 비밀번호 검증
]
