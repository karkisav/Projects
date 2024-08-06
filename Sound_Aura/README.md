# Sound Aura

Welcome to Sound Aura, my first ever project! This web application integrates with Spotify to provide a unique audio experience.

## Installation

Follow these steps to set up and run Sound Aura on your local machine:

1. Clone the repository or download the project files.

2. Open a terminal and navigate to the project folder:
cd path/to/sound-aura
3. Activate the virtual environment:
ource venv/bin/activate
4. Install the required dependencies:
pip install -r requirements.txt
5. Create a `.env` file in the root directory:
touch .env
6. Open the `.env` file and add the following content:
FLASK_APP=run.py
FLASK_ENV=development
SPOTIFY_CLIENT_ID=xxxxx
SPOTIFY_CLIENT_SECRET=xxxx

Replace `xxxxx`s with your actual Spotify API credentials.

## Spotify API Credentials

To obtain the necessary Spotify API credentials:

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Log in with your Spotify account or create a new one.
3. Click on "Create an App" and follow the prompts.
4. Once created, you'll find your `Client ID` and `Client Secret` on the app's dashboard.
5. Copy these values into your `.env` file.

## Running the Application

After completing the setup, you can run the application using one of the following methods:

Option 1: Using Flask
flask run
Option 2: Using Python
python3 run.py

Your web application should now be up and running! Open a web browser and navigate to http://localhost:5000 (or the address provided in the terminal) to start using Sound Aura.