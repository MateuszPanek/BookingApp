from django.core.mail import send_mail

from BookingApp.settings import EMAIL_HOST_USER, DEBUG, TESTING_EMAIL


def send_email(details: dict):
    email = TESTING_EMAIL if DEBUG is not True else details['recipient'],
    send_mail(details['subject'], details['message'], EMAIL_HOST_USER, email, fail_silently=False)
