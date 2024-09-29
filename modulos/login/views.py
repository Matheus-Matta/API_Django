from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    return render(request, 'account/login.html')


# View para login
def login_auth(request):
    if request.method == 'POST':
        # Coleta o username e a senha do formulário de login
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Autentica o usuário
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Se a autenticação for bem-sucedida, realiza o login
            login(request, user)
            # Redireciona o usuário para uma página inicial index
            return redirect('index')
        else:
            # Se a autenticação falhar, exibe uma mensagem de erro
            messages.error(request, 'Usuário ou senha incorretos.')

    return render(request, 'custom/auth-pages/auth-login.html')

# View para logout
@login_required
def login_logout(request):
    # Realiza o logout do usuário
    logout(request)
    # Redireciona para a página de login ou para outra página
    return redirect('login_view') 
