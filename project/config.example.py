# Application Properties
ORG_NAME = 'Name of Organization Chiropractic'
APP_TITLE = 'Sales & Inventory DB'
APP_DESC = 'An extremely simple way to track the sales and inventory of things.'

# Create dummy secrey key so we can use sessions
SECRET_KEY = '123456790'

# Flask-Admin config
FLASK_ADMIN_SWATCH = "readable"

# Create in-memory database
DATABASE_FILE = 'inventory.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = True