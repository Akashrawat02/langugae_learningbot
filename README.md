# langugae_learningbot
Features
🌍 Multiple Languages: Practice conversations in Spanish, French, German, Chinese, Japanese, and more
🎭 Realistic Scenarios: Choose from various conversation scenes like cafes, airports, shopping, etc.
🔍 Real-time Error Detection: Get immediate feedback on grammar, vocabulary, and other language mistakes
📊 Performance Analysis: Review conversation summaries with patterns of mistakes and areas to improve
📝 Personalized Feedback: Receive tailored suggestions based on your proficiency level and specific errors
💬 Natural Conversations: Chat with an AI that adapts to your language proficiency
How It Works
Select Your Learning Path: Choose a target language, your native language, and proficiency level
Pick a Scenario: Select a conversation scene like restaurant, airport, or job interview
Practice Conversation: Chat with the AI assistant in your target language
Get Real-Time Feedback: See mistakes highlighted and explained as you chat
Review Performance: End the conversation to get a comprehensive analysis and improvement suggestions
Tech Stack
Backend: Python with Flask framework
Frontend: HTML, CSS, JavaScript with Bootstrap 5
Database: SQLAlchemy with SQLite
AI: Google Gemini 1.5 Pro API for natural language processing
Deployment: Ready for deployment on Replit
Project Structure
├── app.py                # Flask application setup
├── gemini_utils.py       # Google Gemini API integration
├── main.py               # Application entry point
├── models.py             # Database models
├── routes.py             # Application routes and controllers
├── static/               # Static assets
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
└── templates/            # HTML templates
    ├── layout.html       # Base template
    ├── index.html        # Home page
    ├── chat.html         # Conversation interface
    └── summary.html      # Performance analysis page
Requirements
Python 3.11+
Flask and Flask-SQLAlchemy
Google Generative AI Python SDK
Gunicorn (for production deployment)
Google Gemini API key
Setup and Installation
Clone the repository
git clone https://github.com/yourusername/linguachat.git
cd linguachat
Install dependencies
pip install -r requirements.txt
Set up environment variables
Create a .env file in the project root and add:

GEMINI_API_KEY=your_gemini_api_key_here
Initialize the database
python -c "from app import db; db.create_all()"
Run the application
python main.py
The application will be available at http://localhost:5000

Usage Guide
For Language Learners
Starting a Conversation

Select your target language and native language
Choose your proficiency level
Select a conversation scene
Click "Start Conversation"
During the Conversation

Respond to the AI in your target language
Check the "Mistakes" panel on the right to see corrections
Continue the conversation naturally
Ending the Session

Click "End & Review" to finish your practice session
Review your mistakes and the performance summary
Take note of suggestions for improvement
Start a new conversation when ready
For Developers
models.py contains the database schema
gemini_utils.py handles all AI interactions
routes.py contains the application logic
The frontend JavaScript in static/js/chat.js manages the chat interface
How to Get a Gemini API Key
Visit Google AI Studio
Sign up or log in with your Google account
Navigate to the API section
Create a new API key
Copy the key and add it to your environment variables
Future Enhancements
Audio pronunciation practice and feedback
Vocabulary tracking and spaced repetition
Progress tracking across multiple sessions
Downloadable conversation transcripts
Additional conversation scenarios and difficulty levels
