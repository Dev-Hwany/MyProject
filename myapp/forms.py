from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import re
from .models import User


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        max_length=16,
        help_text="비밀번호는 8~16자이며, 대소문자, 숫자, 특수문자를 포함해야 합니다."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="비밀번호 확인"
    )

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm", "name", "phone_number", "birth_date"]

    def clean_email(self):
        """이메일 중복 확인"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("이미 가입된 이메일입니다.")
        return email

    def clean_phone_number(self):
        """전화번호 중복 확인"""
        phone_number = self.cleaned_data.get("phone_number")
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("이미 등록된 전화번호입니다.")
        return phone_number

    def clean_password(self):
        """비밀번호 유효성 검사"""
        password = self.cleaned_data.get("password")
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\'":\\|,.<>\/?]).{8,16}$'

        if not re.match(password_pattern, password):
            raise ValidationError("비밀번호는 8~16자이며, 대소문자, 숫자, 특수문자를 포함해야 합니다.")

        return password

    def clean(self):
        """비밀번호 확인 일치 여부 검사"""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})

    def save(self, commit=True):
        """비밀번호 해싱 후 저장"""
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password"])  # 비밀번호 해싱
        if commit:
            user.save()
        return user
