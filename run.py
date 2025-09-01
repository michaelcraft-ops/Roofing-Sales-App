# This is the main entry point for our application.
# Its only job is to import the app instance and run it.

from app import app, db
# --- MODIFIED LINE: Add the new models here ---
from app.models import Lead, Deal, DailyActivity, Settings 

# --- NEW: This block makes the 'db' and model instances available to the Flask shell ---
@app.shell_context_processor
def make_shell_context():
    # --- MODIFIED LINE: Add the new models here too ---
    return {'db': db, 'Lead': Lead, 'Deal': Deal, 'DailyActivity': DailyActivity, 'Settings': Settings}

if __name__ == '__main__':
    # The 'debug=True' argument allows us to see errors in the browser
    # and automatically reloads the server when we make changes to the code.
    # IMPORTANT: This should be set to False in a production environment.
    app.run(debug=True)


