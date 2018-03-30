from app import app, db
from app.models import Document, Raw_Text

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Document': Document, 'Raw_Text': Raw_Text}
