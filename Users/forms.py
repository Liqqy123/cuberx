from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
from .models import CustomUser


class RegisterForm(UserCreationForm):
    country_code = forms.ChoiceField(
        label='Код страны',
        choices=[
            ('+7', '+7 (Россия)'),
            ('+1', '+1 (США/Канада)'),
            ('+44', '+44 (Великобритания)'),
            ('+49', '+49 (Германия)'),
            ('+33', '+33 (Франция)'),
            ('+34', '+34 (Испания)'),
            ('+39', '+39 (Италия)'),
            ('+86', '+86 (Китай)'),
            ('+81', '+81 (Япония)'),
            ('+82', '+82 (Корея)'),
            ('+90', '+90 (Турция)'),
            ('+380', '+380 (Украина)'),
            ('+375', '+375 (Беларусь)'),
            ('+7', '+7 (Казахстан)'),
        ],
        initial='+7',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width: auto; display: inline-block;'
        })
    )
    
    phone_number = forms.CharField(
        label='Номер телефона',
        max_length=10,  
        min_length=10,  
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '9991234567',
            'maxlength': '10',  
            'pattern': '[0-9]{10}',  
            'inputmode': 'numeric'  
        })
    )

    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.ru'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'country_code', 'phone_number', 'email', 'password1', 'password2']
        labels = {
            'username': 'Логин',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем класс form-control для каждого поля
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите логин (только латиница и цифры)'
        })

        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'example@mail.ru'
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Придумайте пароль (не менее 8 символов)'
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })

        # Меняем подписи для полей
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        
        # Настройка поля country_code
        self.fields['country_code'].widget.attrs.update({
            'class': 'form-control',
            'id': 'country_code'
        })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if not username:
            raise ValidationError('Логин обязателен для заполнения')
        
        if not re.fullmatch(r'[A-Za-z0-9]+', username):
            raise ValidationError('Логин должен содержать только латинские буквы и цифры')
        
        if len(username) < 6:
            raise ValidationError('Логин должен быть не короче 6 символов')
        
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')
        
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        
        if not phone_number:
            raise ValidationError('Номер телефона обязателен для заполнения')
        
        # Удаляем все нецифровые символы
        phone_number = re.sub(r'\D', '', phone_number)
        
        # Проверяем, что остались только цифры
        if not phone_number.isdigit():
            raise ValidationError('Номер телефона должен содержать только цифры')
        
        # Проверяем длину (ровно 10 цифр)
        if len(phone_number) != 10:
            raise ValidationError('Номер телефона должен содержать ровно 10 цифр')
        
        return phone_number
    
    def clean(self):
        cleaned_data = super().clean()
        country_code = cleaned_data.get('country_code')
        phone_number = cleaned_data.get('phone_number')
        
        if country_code and phone_number:
            # Формируем полный номер телефона
            full_phone = f"{country_code}{phone_number}"
            cleaned_data['full_phone'] = full_phone
            
            # Проверяем уникальность полного номера
            if CustomUser.objects.filter(phone=full_phone).exists():
                raise ValidationError('Пользователь с таким номером телефона уже существует')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.phone = self.cleaned_data.get('full_phone')  # Сохраняем полный номер
        
        if commit:
            user.save()
        
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите логин'
        })
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )

    error_messages = {
        'invalid_login': 'Неверный логин или пароль',
        'inactive': 'Учётная запись отключена'
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})