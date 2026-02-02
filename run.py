import os
import subprocess
from app import create_app

app = create_app()


if __name__ == '__main__':
    port = os.getenv('PORT', 5000)

    if os.getenv('APP_ENV') == 'production':
        subprocess.run(["gunicorn", "run:app", "--bind", f"0.0.0.0:{port}"])
    else:
        subprocess.run(["flask", "run", "--host", "localhost", "--port", port, "--debug"])