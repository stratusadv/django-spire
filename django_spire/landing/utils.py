# def subject_verbose(inquiry):
#     from app.landing.forms import SUBJECT_TOPIC_CHOICES
#     return dict(SUBJECT_TOPIC_CHOICES)[inquiry]
#
#
# def send_contact_us_email(**kwargs):
#     from django.core.mail import EmailMultiAlternatives
#     from django.template.loader import get_template
#
#     text_content = f'''
#         New message from {kwargs['name']} ({kwargs['email']}).
#         {kwargs['company']}
#         {kwargs['message']}
#     '''
#
#     subject = 'Company Name - New Inquiry'
#     html = get_template('core/email/contact_us_email_template.html')
#
#     context_data = {
#         'name': kwargs['name'], 'company': kwargs['company'], 'email': kwargs['email'],
#         'inquiry': kwargs['inquiry'], 'message': kwargs['message']
#     }
#
#     subject, from_email, to = subject, 'companyname@example.com', 'example@example.com'
#     html_content = html.render(context_data)
#     msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
#     msg.attach_alternative(html_content, "text/html")
#     msg.send()
