from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Order


class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Order
        fields = (
            'phone', 'address', 'comment'
        )


class AuthUserForm(forms.ModelForm):

    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

    def __init__(self, *args    , **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].lable = 'Логин'
        self.fields['password'].lable = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Неверный логин')
        user = User.objects.filter(username=username).first()
        if user:
            if not user.check_password(password):
                raise forms.ValidationError("Неверный пароль")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {'username': ('Логин')}


class RegisterUserForm(forms.ModelForm):

    confirm_password = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    phone = forms.CharField(label='Номер телефона', required=False)
    email = forms.EmailField(label='Электронная почта', required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].lable = 'Логин'
        self.fields['password'].lable = 'Пароль'
        self.fields['confirm_password'].lable = 'Подтвердите пароль'
        self.fields['phone'].lable = 'Номер телефона'
        self.fields['first_name'].lable = 'Имя'
        self.fields['last_name'].lable = 'Фамилия'
        self.fields['email'].lable = 'Электронная почта'

    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('.')[-1]
        if domain in ['not']:
            raise forms.ValidationError(f'Регистрация для домена "{domain}" невозможно')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f'Данный почтовый адрес уже зарегистрирован')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Имя {username} занято')
        return username

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'first_name', 'last_name', 'phone', 'email']
        labels = {'username': ('Логин')}