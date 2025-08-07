from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from agents.welcome_agent import WelcomeAgent
from agents.research_agent import ResearchAgent
from agents.copywriter_agent import CopywriterAgent
from agents.project_agent import ProjectAgent

load_dotenv()

app = Flask(__name__)
CORS(app)

welcome_agent = WelcomeAgent()
research_agent = ResearchAgent()
copywriter_agent = CopywriterAgent()
project_agent = ProjectAgent()

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
    try:
        data = request.json
        message = data.get('message', '').strip()
        length = data.get('length', 'medium')
        length_mapping = {
            'short': 2000,
            'medium': 5000,
            'long': 10000
        }
        length_chars = length_mapping.get(length, 5000)
        tone = data.get('tone', 'neutral')
        audience = data.get('audience', 'general public')
        chat_history = data.get('chat_history', [])

        if len(message) < 15:
            return jsonify({'error': 'Topic must be at least 15 characters'}), 400

        html_content = copywriter_agent.write_article(
            topic=message,
            length=length_chars,
            tone=tone,
            audience=audience,
            chat_history=chat_history
        )

        if len(html_content) < length_chars * 0.5:
            app.logger.warning(f"Short article generated: {len(html_content)}/{length_chars} chars")

        return jsonify({'response': html_content})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/project', methods=['POST'])
def handle_project():
    data = request.json
    user_message = data.get('message', '').strip()
    model = data.get('model', 'llama3-8b-8192')
    chat_history = data.get('chat_history', [])
    shown_project_ids = data.get('shown_project_ids', [])

    result = project_agent.get_response(
        query=user_message,
        model=model,
        chat_history=chat_history,
        shown_project_ids=shown_project_ids
    )

    return jsonify({
        'response': result["text"],
        'project_ids': result.get("project_ids", [])
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
