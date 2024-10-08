from django.core.mail import send_mail, EmailMessage


def send_html_email():
    subject = 'HTML email'
    html = """
    <h1>Hello, World!</h1>
    <p>This is HTML email</p>
    <a href="https://vitalii.tech">Vitalii Tech</a>
    <br>
    <img src="https://picsum.photos/200/300" alt="Vitalii Tech">
    """

    send_mail(
        subject,
        message="Fallback message",
        from_email="vitalii@vitalii.tech",
        recipient_list=["pavliuk96@gmail.com"],
        html_message=html,
    )


def send_email_with_attachments():
    subject = 'Email with attachments'
    message = 'This is email with attachments'

    mail = EmailMessage(
        subject,
        message,
        from_email="vitalii@vitalii.tech",
        to=["pavliuk96@gmail.com"],
    )

    mail.attach_file('Some document.docx')

    mail.send()
