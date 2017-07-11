# Application Properties
ORG_NAME = 'Name of Organization Chiropractic'
APP_TITLE = 'Sales & Inventory DB'
APP_DESC = 'An extremely simple way to track the sales and inventory of things.'

# Create dummy secrey key so we can use sessions
SECRET_KEY = '123456790'

# Flask-Admin config
DEBUG = False
HOST = 'localhost'
PORT = 5000
FLASK_ADMIN_SWATCH = "readable"

# database
DATABASE_FILE = 'inventory_0.1.0.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_LOGGING = False