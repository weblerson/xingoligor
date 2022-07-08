from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import auth

from .models import TokenAtivacao, TokenRecuperacao
from hashlib import sha256

from django.contrib import messages
from django.contrib.messages import constants

from .utils import Verify, Send

def register(request):
    match request.method:
        case "GET":
            if request.user.is_authenticated:
                return redirect('/')

            return render(request, 'register.html')

        case "POST":
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm-password')

            if Verify.blank_inputs(request, username, email, password, confirm_password):
                return redirect('/auth/register')

            if not Verify.equal_passwords(request, password, confirm_password):
                return redirect('/auth/register')

            _username = User.objects.filter(username=username)
            _email = User.objects.filter(email=email)
            if _username.exists():
                messages.add_message(request, constants.WARNING, f"Já existe um usuário de nome {username} cadastrado. Use outro.")
                return redirect('/auth/register')

            if _email.exists():
                messages.add_message(request, constants.WARNING, f"Já existe um usuário de email {email} cadastrado. Use outro.")
                return redirect('/auth/register')

            try:
                user = User(username=username,
                            email=email,
                            password=password,
                            is_active=False)

                user.save()
                messages.add_message(request, 
                                    constants.SUCCESS, 
                                    f"Usuário cadastrado com sucesso! Um email de confirmação foi enviado para {email} para ativação da conta.")
                
                hash = sha256(f"{username}{email}".encode()).hexdigest()

                token = TokenAtivacao(token=hash,
                                      usuario=user)

                token.save()

                url = f"/auth/activate/{hash}"

                Send.email(settings.ACTIVATION_TEMPLATE, "Ativação de conta", email, username=username, url=url)

                return redirect('/auth/register')

            except:
                messages.add_message(request, constants.ERROR, "Erro interno do sistema. Não foi possível realizar o cadastro.")

                return redirect('/auth/register')

def activate(request, token):
    _token = get_object_or_404(TokenAtivacao, token=token)

    if not _token.usado:
        try:
            user = User.objects.get(username = _token.usuario.username)
            user.is_active = True

            user.save()

            _token.usado = True
            _token.save()

            messages.add_message(request, constants.SUCCESS, "Conta ativada com sucesso! Faça login.")
            return redirect('/auth/login')
        
        except:
            messages.add_message(request, constants.SUCCESS, "Erro interno do sistema! Não foi possível ativar a conta. Tente novamente.")
            return redirect('/auth/register')

def login(request):
    match request.method:
        case "GET":
            if request.user.is_authenticated:
                return redirect('/')

            return render(request, 'login.html')

        case "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')

            if Verify.blank_inputs(request, username, password):
                return redirect('/auth/login')

            user = auth.authenticate(username=username, password=password)
            if not user:
                messages.add_message(request, constants.WARNING, "Esse usuário não existe.")
                return redirect('/auth/login')

            else:
                auth.login(request, user)
                return redirect('/')

def logout(request):
    auth.logout(request)
    return redirect('/auth/login')

def recover_menu(request):
    match request.method:
        case "GET":
            return render(request, 'recover_menu.html')

        case "POST":
            email = request.POST.get('email')
            user = User.objects.filter(email=email)

            if Verify.blank_inputs(request, email):
                return redirect('/auth/recover')

            if not user.exists():
                messages.add_message(request, constants.WARNING, f"Não existe um usuário de email {email} cadastrado.")
                return redirect('/auth/recover')

            try:
                user = User.objects.get(email=email)
                token = TokenRecuperacao.objects.filter(usuario=user)
                hash = sha256(f"{email}".encode()).hexdigest()

                if token.exists():
                    token = TokenRecuperacao.objects.get(usuario=user)
                    token.solicitado = True
                    token.save()

                    Send.email(settings.RECOVER_TEMPLATE, "Recuperação de senha", email, username=user.username, token=hash)
                    messages.add_message(request, constants.SUCCESS, f"E-mail de recuperação enviado com sucesso para {email}.")
                    return redirect('/auth/login')

                else:
                    token = TokenRecuperacao(token=hash,
                                            usuario=user)

                    token.save()

                    Send.email(settings.RECOVER_TEMPLATE, "Recuperação de senha", email, username=user.username, token=hash)
                    messages.add_message(request, constants.SUCCESS, f"E-mail de recuperação enviado com sucesso para {email}.")
                    return redirect('/auth/login')

            except:
                messages.add_message(request, constants.ERROR, "Erro interno do sistema. Não foi possível solicitar a recuperação de senha.")
                return redirect('/auth/recover')

def recover_password(request, token):
    _token = get_object_or_404(TokenRecuperacao, token=token)

    match request.method:
        case "GET":
            if not _token.solicitado:
                messages.add_message(request, constants.WARNING, f"Token de recuperação para {_token.usuario.email} não solicitado.")
                return redirect('/auth/login')

            return render(request, 'recover.html', {"token": token})

        case "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm-password')

            if not Verify.equal_passwords(request, password, confirm_password):
                return redirect(f'/auth/recover/{token}')

            try:
                user = User.objects.get(username=_token.usuario.username)
                user.set_password(password)
                user.save()

                messages.add_message(request, constants.SUCCESS, "Senha alterada com sucesso!")
                return redirect('/auth/login')

            except:
                messages.add_message(request, constants.ERROR, "Erro interno do sistema. Não foi possível alterar a senha.")
                return redirect(f'/auth/recover/{token}')

def no_recover(request, token):
    _token = get_object_or_404(TokenRecuperacao, token=token)
    if not _token.solicitado:
        messages.add_message(request, constants.WARNING, f"Token de recuperação para {_token.usuario.email} não solicitado.")
        return redirect('/auth/login')

    _token.solicitado = False
    _token.save()
    
    messages.add_message(request, constants.SUCCESS, f"Token de recuperação para {_token.usuario.email} recusado com sucesso!")
    return redirect('/auth/login')