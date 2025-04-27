import os
print("Current working directory:", os.getcwd())
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

