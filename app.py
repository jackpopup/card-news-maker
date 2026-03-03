import sys
import io
import base64
from pathlib import Path
from flask import Flask, request, jsonify, render_template

sys.path.insert(0, str(Path(__file__).parent))
from card_news_maker import CardRenderer, THEMES

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/themes')
def get_themes():
    return jsonify(list(THEMES.keys()))


@app.route('/api/generate', methods=['POST'])
def generate():
    content = request.get_json()
    if not content:
        return jsonify({'error': 'JSON body required'}), 400

    theme = content.get('theme', 'blue')
    brand = content.get('brand', '')
    cards = content.get('cards', [])

    if not cards:
        return jsonify({'error': '카드가 없습니다'}), 400

    if theme not in THEMES:
        theme = 'blue'

    renderer = CardRenderer(theme, brand, len(cards))
    results = []

    for i, card in enumerate(cards):
        img = renderer.render_card(card, i)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        results.append({
            'filename': f'card_{i+1:02d}_{card.get("type","card")}.png',
            'data': b64
        })

    return jsonify({'cards': results, 'count': len(results)})


if __name__ == '__main__':
    print('[카드뉴스 웹 서버 시작]')
    print('   http://localhost:5000')
    app.run(debug=False, port=5000)
