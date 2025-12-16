from flask import Flask, request, jsonify
import requests
import base64
import json

app = Flask(__name__)

def call_cyberx_api(search_type, query):
    """Call the CyberXWorm API"""
    payload = {'t': search_type, 'q': query, 'k': 'ForApp'}
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    
    try:
        response = requests.post(
            'https://danger-vip-key.shop/proxy.php',
            data=encoded,
            headers={'Content-Type': 'text/plain'},
            timeout=10
        )
        return response.json() if response.status_code == 200 else []
    except:
        return []

@app.route('/api/mobile')
def mobile_api():
    """Mobile number lookup"""
    number = request.args.get('number')
    
    if not number or len(number) != 10 or not number.isdigit():
        return jsonify({
            'success': False,
            'error': 'Invalid mobile number. Must be 10 digits.',
            'credit': 'SALAAR | @osintgroupp'
        })
    
    data = call_cyberx_api('number', number)
    
    return jsonify({
        'success': True,
        'data': data,
        'credit': 'SALAAR | @osintgroupp'
    })

@app.route('/api/aadhaar')
def aadhaar_api():
    """Aadhaar lookup"""
    aadhaar = request.args.get('aadhaar')
    
    if not aadhaar or len(aadhaar) != 12 or not aadhaar.isdigit():
        return jsonify({
            'success': False,
            'error': 'Invalid Aadhaar number. Must be 12 digits.',
            'credit': 'SALAAR | @osintgroupp'
        })
    
    data = call_cyberx_api('aadhaar', aadhaar)
    
    return jsonify({
        'success': True,
        'data': data,
        'credit': 'SALAAR | @osintgroupp'
    })

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
<html>
<head>
    <title>CyberXWorm API</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #0f0f0f; color: white; }
        .box { background: #1a1a1a; padding: 20px; margin: 15px 0; border-radius: 10px; border: 1px solid #00ff41; }
        code { background: #333; color: #00ff41; padding: 5px 10px; border-radius: 4px; font-family: monospace; }
        a { color: #00ff41; text-decoration: none; }
        .glitch { text-shadow: 0 0 5px #00ff41; }
    </style>
</head>
<body>
    <h1 class="glitch">🔍 CYBERXWORM API</h1>
    <p>Direct API access to danger-vip-key.shop</p>
    
    <div class="box">
        <h3>📱 MOBILE LOOKUP</h3>
        <p><code>GET /api/mobile?number=9876543210</code></p>
        <p><a href="/api/mobile?number=9876543210" target="_blank">➤ TEST NOW</a></p>
    </div>
    
    <div class="box">
        <h3>🆔 AADHAAR LOOKUP</h3>
        <p><code>GET /api/aadhaar?aadhaar=123456789012</code></p>
        <p><a href="/api/aadhaar?aadhaar=123456789012" target="_blank">➤ TEST NOW</a></p>
    </div>
    
    <p><em>API by: SALAAR | @osintgroupp</em></p>
</body>
</html>
    '''

# ⚠️ VERCEL REQUIRED - Last line mein yeh hona chahiye
app = app