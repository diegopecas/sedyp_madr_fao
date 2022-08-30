from flask_mail import Mail

mail = Mail()

# Initialize the email service 
def init_email_service(app):
     mail.init_app(app) 

# Returns the email service to be accesible from everywhere
def get_email_service():
    return mail 