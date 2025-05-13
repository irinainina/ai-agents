# ai-agents

## Installation

### 1. Clone this repository

```shell
git clone https://github.com/irinainina/ai-agents
cd ai-agent-app
```

### 2. Set up environment variables

Create a `.env` file in the `backend` directory with your Groq API key:

```shell
GROQ_API_KEY="your_api_key_here"
```

You can get a Groq API key by signing up at [GroqCloud](https://console.groq.com/keys).

### 3. Set up the backend

```shell
# Create a Python virtual environment
python -m venv venv
source venv/Scripts/activate

# Install Python dependencies
pip install -r requirements.txt

# Start the Flask server
cd backend
python main.py
```

The backend server will run on [http://127.0.0.1:5001](http://127.0.0.1:5001).

### 4. Set up the frontend

In a new terminal window:

```shell
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000).

## Usage

Once both the backend and frontend are running