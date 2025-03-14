import json, os, re, random, string, logging, openai, requests
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from rest_framework.exceptions import ValidationError
from .models import User, Schedule, Note, AI_Feedback
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime

def main_page(request):
    return render(request, 'my_app/main_page.html')  # 'main_page.html'은 메인 페이지를 위한 템플릿 파일입니다.

# 사용자 등록
@csrf_protect
def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        name = request.POST.get("name")
        phone_number = request.POST.get("phone_number")
        birth_date = request.POST.get("birth_date")

        # 1. 이메일 형식 검증
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"success": False, "message": "유효한 이메일 형식이 아닙니다."})

        # 2. 비밀번호 확인
        if password != password_confirm:
            return JsonResponse({"success": False, "message": "비밀번호가 일치하지 않습니다."})

        # 3. 비밀번호 검증 (8~16자, 영문 대소문자, 숫자, 특수문자 포함)
        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,16}$"
        if not re.match(password_pattern, password):
            return JsonResponse({"success": False, "message": "비밀번호는 8~16자 영문 대소문자, 숫자, 특수문자를 포함해야 합니다."})

        # 4. 이메일 및 전화번호 중복 확인
        if User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "이미 가입된 이메일입니다."})
        if User.objects.filter(phone_number=phone_number).exists():
            return JsonResponse({"success": False, "message": "이미 등록된 전화번호입니다."})

        # 5. 사용자 생성 및 저장
        hashed_password = make_password(password)  # 비밀번호 해싱
        user = User.objects.create(
            email=email,
            password=hashed_password,
            name=name,
            phone_number=phone_number,
            birth_date=birth_date,
        )

        return JsonResponse({"success": True, "message": "회원가입이 완료되었습니다!"})

    return JsonResponse({"success": False, "message": "잘못된 요청입니다."})

# 로그인
@csrf_protect
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            # 이메일을 기준으로 사용자 조회
            user = User.objects.get(email=email)

            # 사용자 활성화 상태 확인
            if not user.is_active:
                return JsonResponse({"status": "error", "message": "아이디 또는 비밀번호가 올바르지 않습니다."}, status=403)

            # 비밀번호 확인
            if check_password(password, user.password):
                # 세션에 사용자 정보 저장
                request.session["user_email"] = user.email
                request.session["user_name"] = user.name
                return JsonResponse({"status": "success", "redirect_url": reverse('myapp:main_page')})
            else:
                raise User.DoesNotExist
        except User.DoesNotExist:
            return JsonResponse({"status": "error", "message": "아이디 또는 비밀번호가 올바르지 않습니다."}, status=400)
    else:
        return JsonResponse({"status": "error", "message": "POST 요청만 허용됩니다."}, status=405)

def logout_view(request):
    request.session.flush()  # 세션 데이터 초기화
    return redirect('myapp:main_page')

# 일정 추가
@login_required
def create_schedule(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')
        priority = request.POST.get('priority')

        # start_time, end_time을 datetime 객체로 변환
        start_time = parse_datetime(start_time_str)
        end_time = parse_datetime(end_time_str)

        # 일정 생성
        schedule = Schedule(
            user=request.user,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            priority=priority,
            status='pending',  # 기본값
        )
        schedule.save()
        return redirect('dashboard')  # 일정 추가 후 대시보드로 리다이렉트

    return render(request, 'my_app/create_schedule.html')

# 일정 수정
@login_required
def update_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)

    if request.method == "POST":
        schedule.title = request.POST.get('title', schedule.title)
        schedule.description = request.POST.get('description', schedule.description)
        schedule.start_time = parse_datetime(request.POST.get('start_time', schedule.start_time))
        schedule.end_time = parse_datetime(request.POST.get('end_time', schedule.end_time))
        schedule.priority = request.POST.get('priority', schedule.priority)
        schedule.status = request.POST.get('status', schedule.status)

        schedule.save()
        return redirect('dashboard')  # 일정 수정 후 대시보드로 리다이렉트

    return render(request, 'my_app/update_schedule.html', {'schedule': schedule})

# 일정 삭제
@login_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    schedule.delete()
    return redirect('dashboard')  # 일정 삭제 후 대시보드로 리다이렉트

# 메모 추가
@login_required
def create_note(request, schedule_id):
    if request.method == "POST":
        schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
        content = request.POST.get('content')

        note = Note(schedule=schedule, content=content)
        note.save()
        return redirect('schedule_detail', schedule_id=schedule.id)  # 메모 추가 후 일정 상세 페이지로 리다이렉트

    return render(request, 'my_app/create_note.html')

# 메모 수정
@login_required
def update_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    if request.method == "POST":
        note.content = request.POST.get('content', note.content)
        note.save()
        return redirect('schedule_detail', schedule_id=note.schedule.id)  # 메모 수정 후 일정 상세 페이지로 리다이렉트

    return render(request, 'my_app/update_note.html', {'note': note})

# 메모 삭제
@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.delete()
    return redirect('schedule_detail', schedule_id=note.schedule.id)  # 메모 삭제 후 일정 상세 페이지로 리다이렉트

# AI 분석 피드백 생성
@login_required
def ai_feedback(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)

    # AI 분석 로직 (예시)
    # 실제 AI 모델을 호출하는 로직을 구현해야 합니다.
    feedback = f"AI 분석: 당신의 일정 {schedule.title}은 매우 중요해 보입니다. 우선순위가 높고 효율적인 시간 관리를 권장합니다."

    ai_feedback = AI_Feedback(schedule=schedule, feedback=feedback)
    ai_feedback.save()
    return redirect('schedule_detail', schedule_id=schedule.id)  # AI 피드백 후 일정 상세 페이지로 리다이렉트

# 사용자의 일정 목록 조회
@login_required
def dashboard(request):
    schedules = Schedule.objects.filter(user=request.user)
    return render(request, 'my_app/schedule_list.html', {'schedules': schedules})

# 비밀번호 검증
@login_required
def check_user_password(request):
    if request.method == "POST":
        raw_password = request.POST.get('password')
        user = request.user

        if user.check_password(raw_password):
            return render(request, 'my_app/password_check.html', {'message': 'Password is correct'})
        else:
            return render(request, 'my_app/password_check.html', {'error': 'Invalid password'})
