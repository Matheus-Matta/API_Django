from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import BadHeaderError
from smtplib import SMTPException 
from django.core.validators import validate_email

def send_mail(nome, produto, email, msg, codigo, tracking_link = None, avaliacao_link = None):
    # Assunto do email
    try:
        validate_email(email)
        
        subject = 'Detalhes do seu pedido'
        
        # Carregar o template HTML e renderizar com os dados dinâmicos
        html_content = render_to_string('emails/email_tracking.html', {
            'nome': nome,
            'produto': produto,
            'email': email,
            'tracking_link': tracking_link,
            'avaliacao_link': avaliacao_link,
            'msg': msg,
            'codigo': codigo
        })

        # Enviar o email
        email = EmailMultiAlternatives(
            subject=subject,
            body="Este é o corpo do email em texto simples (caso o HTML não funcione).",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        
        # Anexar a versão HTML do email
        email.attach_alternative(html_content, "text/html")
        
        result = email.send()

        if result == 0:
            raise ValueError("Falha no envio do email")
        
        return True

    except BadHeaderError:
        raise ValueError("Erro no cabeçalho do email")
    except SMTPException as e:
        raise ValueError(f"Erro SMTP: {str(e)}")
    except Exception as e:
        raise ValueError(f"Erro inesperado: {str(e)}")