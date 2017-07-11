import os
from project.app import app, db
import db_setup
#import webbrowser

if __name__ == '__main__':
    '''
    # Build an empty db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, 'project', app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        db.create_all()
        db_setup.set_trigger_fullname(database_path)
        db_setup.set_trigger_selling_price(database_path)
    '''
    # Start app
    app.run(
        debug=app.config['DEBUG'],
        host=app.config.get("HOST", "localhost"),
        port=app.config.get("PORT", 8700)
    )
    '''
    url = "http://{0}:{1}".format(app.config['HOST'], app.config['PORT'])
    print(url)
    webbrowser.open_new(url)
    '''