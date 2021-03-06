from django.core.mail import send_mail


def send_invitation(email, activation_code):
    send_mail(
        subject='[Invitation] Rethink the way you play table football!',
        message='''
            Hi!

            You have been invited to TFoosball. Join us here: https://tfoosball.herokuapp.com/accept/{0}/

            Best regards,
            TFoosball Team
        '''.format(activation_code),
        # html_message='Here is the message.',
        from_email='tfoosball@piotrstaniow.pl',
        recipient_list=[email],
        fail_silently=False,
    )
