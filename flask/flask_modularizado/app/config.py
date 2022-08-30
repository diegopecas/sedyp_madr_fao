import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') if (os.environ.get('SECRET_KEY')) else 'fbfundplankey' # for the token

    # EMAIL_SENDER = os.environ.get('EMAIL_SENDER') if(os.environ.get('EMAIL_SENDER')) else 'testingemails266@gmail.com'
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER') if(os.environ.get('EMAIL_SENDER')) else 'HRDPFAO@hotmail.com'

    EMAIL_CONFIG = dict(
        # MAIL_SERVER = 'smtp.gmail.com',
        MAIL_SERVER = 'smtp.office365.com',
        MAIL_PORT = 587,
        MAIL_USERNAME = EMAIL_SENDER,
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') if(os.environ.get('MAIL_PASSWORD')) else 'testing123*',
        MAIL_USE_TLS = True,
        MAIL_USE_SSL = False,
    )

    # initialing sql
    _USER = os.environ.get('DB_USER') if (os.environ.get('DB_USER')) else 'itim'
    _PASSWORD = os.environ.get('DB_PASSWORD') if (os.environ.get('DB_PASSWORD')) else 'pgFaoApp2021$'
    _HOST = os.environ.get('DB_IP') if (os.environ.get('DB_IP')) else 'pgfaoserv.postgres.database.azure.com'
    _PORT = os.environ.get('DB_PORT') if (os.environ.get('DB_PORT')) else '5432'
    _DATABASE = os.environ.get('DB_NAME') if (os.environ.get('DB_NAME')) else 'faodb'

    UPLOAD_FOLDER = './adjuntos'
    UPLOAD_SEGUIMIENTO = '/seguimiento'
    UPLOAD_EVENTO = '/evento' 
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'xlsx'}


    