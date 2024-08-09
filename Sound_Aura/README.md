# 🎵 Sound Aura
Welcome to Sound Aura, my first-ever project! This web application integrates with Spotify to provide a unique audio experience.

## 🚀 Installation
Follow these steps to set up and run Sound Aura on your local machine:

Clone the repository or download the project files.

Open a terminal and navigate to the project folder:

`cd path/to/sound-aura`
Activate the virtual environment:

`source venv/bin/activate`
Install the required dependencies


`pip install -r requirements.txt`
Create a .env file in the root directory:

`touch .env`
Open the `.env` file and add the following content:

env

`FLASK_APP=run.py`
`FLASK_ENV=development`
`SPOTIFY_CLIENT_ID=xxxxx`
`SPOTIFY_CLIENT_SECRET=xxxxx`
`Replace xxxxx with your actual Spotify API credentials.`
`SPOTIFY_REDIRECT_URI='http://127.0.0.1:5000/callback`
## 🔑 Spotify API Credentials
To obtain the necessary Spotify API credentials:

Go to the Spotify Developer Dashboard.
Log in with your Spotify account or create a new one.
Click on "Create an App" and follow the prompts.
Once created, you'll find your Client ID and Client Secret on the app's dashboard.
Copy these values into your .env file.
## ▶️ Running the Application
After completing the setup, you can run the application using one of the following methods:

### Option 1: Using Flask

`flask run`
### Option 2: Using Python

`python3 run.py`
Your web application should now be up and running! Open a web browser and navigate to http://localhost:5000 (or the address provided in the terminal) to start using Sound Aura.