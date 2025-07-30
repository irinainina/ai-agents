from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from agents.welcome_agent import WelcomeAgent
from agents.research_agent import ResearchAgent
from agents.copywriter_agent import CopywriterAgent

load_dotenv()

app = Flask(__name__)
CORS(app)
welcome_agent = WelcomeAgent()
research_agent = ResearchAgent()
copywriter_agent = CopywriterAgent()

@app.route('/api/welcome', methods=['POST'])
def handle_welcome():
    data = request.json
    user_message = data.get('message', '').strip()
    model = data.get('model', 'llama3-8b-8192')
    chat_history = data.get('chat_history', [])
    
    response = welcome_agent.get_response(
        query=user_message,
        model=model,
        chat_history=chat_history
    )
    
    return jsonify({'response': response})

@app.route('/api/research', methods=['POST'])
def research_agent_endpoint():
    data = request.json
    message = data.get('message', '')
    model = data.get('model', 'llama3-8b-8192')
    chat_history = data.get('chat_history', [])

    response = research_agent.search_web(
        message, 
        model=model,
        chat_history=chat_history)
    
    return jsonify({'response': response})

@app.route('/api/copywriter', methods=['POST'])
def copywriter_agent_endpoint():
    data = request.json
    message = data.get('message', '').strip()
    model = data.get('model', 'llama3-8b-8192')
    chat_history = data.get('chat_history', [])
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    html_content = copywriter_agent.write_article(
        topic=message,
        model=model,
        chat_history=chat_history
    )
    
    return jsonify({'response': html_content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
    