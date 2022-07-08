from django.conf import settings

from django.contrib import messages
from django.contrib.messages import constants
from django.http import HttpRequest

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Verify:
    @staticmethod
    def blank_inputs(request: HttpRequest, *args):
        if any(len(v.strip()) == 0 for v in args):
            messages.add_message(request, constants.WARNING, "Preencha todos os campos!")

            return True

        return False

    @staticmethod
    def equal_passwords(request: HttpRequest, password: str, confirm_password: str):
        if password != confirm_password:
            messages.add_message(request, constants.WARNING, "As senhas não coincidem.")

            return False
        
        return True

class Send:
    @staticmethod
    def email(template_path: str, subject: str, to: str, **kwargs):
        html_content = render_to_string(template_path, kwargs)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [to])

        msg.attach_alternative(html_content, 'text/html')
        msg.send()

        return {"status": 1}