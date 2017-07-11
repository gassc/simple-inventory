import os
from project.app import app, db
import db_setup

if __name__ == '__main__':
    # Build an empty db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, 'project', app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        db.create_all()
        db_setup.set_trigger_fullname(database_path)
        db_setup.set_trigger_selling_price(database_path)
    # Start app
    app.run(debug=True)