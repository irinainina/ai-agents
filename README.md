# ai-agents

AI-агенты для демонстрации кейсов Halo Lab на основе пользовательского запроса.

## Installation

### 1. Clone this repository

```shell
git clone https://github.com/irinainina/ai-agents
cd ai-agents
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
source venv/Scripts/activate  # or source venv/bin/activate on macOS/Linux

# Install Python dependencies
pip install -r requirements.txt

# Generate project embeddings (one-time step)
python backend/generate_embeddings.py

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

Once both the backend and frontend are running, open [http://localhost:3000](http://localhost:3000) in your browser and start chatting with the AI agents.

## Notes

* The `project_embeddings.pt` file is generated once and reused to improve performance.
* You can update it by running `python backend/generate_embeddings.py` again after editing `projects.json`.
