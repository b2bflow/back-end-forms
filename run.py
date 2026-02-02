import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') == 'production':
        app.run(debug=False, host='0.0.0.0', port=os.getenv('PORT'))
    else:
        app.run(debug=True, host='localhost', port=5000)