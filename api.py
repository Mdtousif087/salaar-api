from flask import Flask, request, jsonify
import requests
from faker import Faker
import random
import string
import json
import time
import concurrent.futures
import threading

app = Flask(__name__)
fake = Faker()

# Thread-safe session storage
thread_local = threading.local()

def get_session():
    """Get or create thread-local session"""
    if not hasattr(thread_local, "session"):
        thread_local.session = create_session()
    return thread_local.session

def gen_pass():
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(12))

def create_session():
    """Create a requests session with optimized settings"""
    session = requests.Session()
    
    # Optimized headers for speed
    session.headers.update({
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://darkosint.in",
        "referer": "https://darkosint.in/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="120", "Not_A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "priority": "u=1, i"
    })
    
    # Optimize connection pooling
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,
        pool_maxsize=10,
        max_retries=2
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session

# Cache for sessions (reuse sessions)
session_cache = {}
CACHE_TIMEOUT = 300  # 5 minutes

def get_cached_session():
    """Get cached session or create new one"""
    current_time = time.time()
    session_key = threading.get_ident()
    
    if session_key in session_cache:
        session, timestamp = session_cache[session_key]
        if current_time - timestamp < CACHE_TIMEOUT:
            return session
    
    # Create new session and cache it
    session = create_session()
    session_cache[session_key] = (session, current_time)
    return session

def signup_user_fast(session):
    """Fast signup with minimal delay"""
    try:
        name = fake.first_name()
        email = f"{name.lower()}{random.randint(100,999)}@gmail.com"
        password = gen_pass()
        
        payload = {
            "action": "signup",
            "name": name,
            "email": email,
            "password": password
        }
        
        # Quick signup with timeout
        response = session.post(
            "https://darkosint.in/api/auth.php", 
            data=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    return True
            except:
                return True  # If JSON fails but status is 200
        return False
        
    except:
        return False

def clean_text(text):
    """Fast text cleaning"""
    if not text:
        return "N/A"
    return ' '.join(str(text).strip().split())

def clean_address(address):
    """Fast address cleaning"""
    if not address:
        return "N/A"
    
    # Replace separators
    address = address.replace("!", ",").replace("!!", ",").replace("!!", ",")
    
    # Clean up
    parts = [part.strip() for part in address.split(",") if part.strip()]
    return ", ".join(parts)

def process_lookup_parallel(session, lookup_type, query):
    """Perform lookup with timeout"""
    try:
        payload = {"type": lookup_type, "query": query}
        
        # Fast request with timeout
        response = session.post(
            "https://darkosint.in/api/lookup.php",
            data=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            return None
        
        return response.json()
        
    except Exception as e:
        print(f"Lookup error: {e}")
        return None

def perform_lookup_fast(lookup_type, query):
    """Optimized lookup function"""
    start_time = time.time()
    
    # Get cached session
    session = get_cached_session()
    
    # Signup if needed (do it once per session)
    if not hasattr(session, 'signed_up'):
        if signup_user_fast(session):
            session.signed_up = True
    
    # Perform lookup
    result = process_lookup_parallel(session, lookup_type, query)
    
    if not result:
        return {
            "success": False,
            "error": "Lookup failed or timeout",
            "response_time": round(time.time() - start_time, 2),
            "Developer": "Basic Coders | @SajagOG"
        }
    
    # Fast processing
    try:
        data = result.get("data", {})
        raw_results = data.get("result", [])
        
        if not raw_results:
            return {
                "success": True,
                "count": 0,
                "query": query,
                "type": lookup_type,
                "results": [],
                "response_time": round(time.time() - start_time, 2),
                "Developer": "Basic Coders | @SajagOG"
            }
        
        # Process results quickly
        processed_results = []
        for row in raw_results[:50]:  # Limit to 50 results for speed
            processed_results.append({
                "id": row.get("id", ""),
                "name": clean_text(row.get("name")),
                "father_name": clean_text(row.get("father_name")),
                "address": clean_address(row.get("address")),
                "mobile": clean_text(row.get("mobile")),
                "alt_mobile": clean_text(row.get("alt_mobile")),
                "aadhaar": clean_text(row.get("id_number")),
                "email": clean_text(row.get("email")),
                "circle": clean_text(row.get("circle"))
            })
        
        # For mobile lookup, prioritize exact matches
        if lookup_type == "mobile":
            exact_matches = []
            other_matches = []
            
            for result in processed_results:
                if result["mobile"] == query or result["alt_mobile"] == query:
                    exact_matches.append(result)
                else:
                    other_matches.append(result)
            
            processed_results = exact_matches + other_matches
        
        return {
            "success": True,
            "count": len(processed_results),
            "query": query,
            "type": lookup_type,
            "results": processed_results,
            "response_time": round(time.time() - start_time, 2),
            "credit": data.get("credit", "@DarkTrace_Networks"),
            "Developer": "Basic Coders | @SajagOG"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Processing error: {str(e)}",
            "response_time": round(time.time() - start_time, 2),
            "Developer": "Basic Coders | @SajagOG"
        }

# Fast validation functions
def validate_mobile(number):
    if not number or not number.isdigit() or len(number) != 10:
        return None
    return number

def validate_aadhar(aadhar):
    if not aadhar or not aadhar.isdigit() or len(aadhar) != 12:
        return None
    return aadhar

# Fast route handlers
@app.route("/num", methods=["GET"])
def lookup_num():
    """Fast mobile number lookup"""
    start_time = time.time()
    
    number = request.args.get("number", "")
    clean_number = validate_mobile(''.join(filter(str.isdigit, number)))
    
    if not clean_number:
        return jsonify({
            "success": False,
            "error": "Invalid mobile number. Must be 10 digits.",
            "response_time": round(time.time() - start_time, 3),
            "Developer": "Basic Coders | @SajagOG"
        })
    
    result = perform_lookup_fast("mobile", clean_number)
    result["response_time"] = round(time.time() - start_time, 3)
    return jsonify(result)

@app.route("/aadhar", methods=["GET"])
def lookup_aadhar():
    """Fast Aadhaar lookup"""
    start_time = time.time()
    
    aadhar = request.args.get("aadhar", "")
    clean_aadhar = validate_aadhar(''.join(filter(str.isdigit, aadhar)))
    
    if not clean_aadhar:
        return jsonify({
            "success": False,
            "error": "Invalid Aadhaar number. Must be 12 digits.",
            "response_time": round(time.time() - start_time, 3),
            "Developer": "Basic Coders | @SajagOG"
        })
    
    result = perform_lookup_fast("aadhaar", clean_aadhar)
    result["response_time"] = round(time.time() - start_time, 3)
    return jsonify(result)

@app.route("/bulk", methods=["POST"])
def bulk_lookup():
    """Bulk lookup for multiple numbers (FAST)"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided",
                "response_time": round(time.time() - start_time, 3),
                "Developer": "Basic Coders | @SajagOG"
            })
        
        mobiles = data.get("mobiles", [])
        aadhars = data.get("aadhars", [])
        
        if not mobiles and not aadhars:
            return jsonify({
                "success": False,
                "error": "Provide mobiles or aadhars array",
                "response_time": round(time.time() - start_time, 3),
                "Developer": "Basic Coders | @SajagOG"
            })
        
        results = {}
        
        # Process mobiles
        if mobiles:
            mobile_results = {}
            for mobile in mobiles[:10]:  # Limit to 10 for speed
                clean_mobile = validate_mobile(''.join(filter(str.isdigit, str(mobile))))
                if clean_mobile:
                    result = perform_lookup_fast("mobile", clean_mobile)
                    mobile_results[mobile] = result
            results["mobiles"] = mobile_results
        
        # Process aadhars
        if aadhars:
            aadhar_results = {}
            for aadhar in aadhars[:10]:  # Limit to 10 for speed
                clean_aadhar = validate_aadhar(''.join(filter(str.isdigit, str(aadhar))))
                if clean_aadhar:
                    result = perform_lookup_fast("aadhaar", clean_aadhar)
                    aadhar_results[aadhar] = result
            results["aadhars"] = aadhar_results
        
        return jsonify({
            "success": True,
            "results": results,
            "total_time": round(time.time() - start_time, 3),
            "Developer": "Basic Coders | @SajagOG"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Bulk lookup error: {str(e)}",
            "response_time": round(time.time() - start_time, 3),
            "Developer": "Basic Coders | @SajagOG"
        })

@app.route("/status", methods=["GET"])
def status():
    """Quick status check"""
    return jsonify({
        "success": True,
        "status": "🚀 API is running FAST",
        "timestamp": time.time(),
        "endpoints": {
            "GET /num?number=9876543210": "Mobile lookup (fast)",
            "GET /aadhar?aadhar=123456789012": "Aadhaar lookup (fast)",
            "POST /bulk": "Bulk lookup (JSON)",
            "GET /status": "API status"
        },
        "optimizations": [
            "Cached sessions",
            "Connection pooling",
            "Fast validation",
            "Response time tracking",
            "Thread-safe design"
        ],
        "Developer": "Basic Coders | @SajagOG",
        "version": "3.0-FAST"
    })

@app.route("/", methods=["GET"])
def index():
    """Root endpoint"""
    return jsonify({
        "success": True,
        "message": "⚡ DarkOSINT API - Ultra Fast Version",
        "endpoints": {
            "/num": "Mobile lookup - GET ?number=MOBILE",
            "/aadhar": "Aadhaar lookup - GET ?aadhar=AADHAAR",
            "/bulk": "Bulk lookup - POST JSON with mobiles/aadhars",
            "/status": "API status"
        },
        "features": [
            "Ultra fast responses (cached sessions)",
            "Bulk lookup support",
            "Response time tracking",
            "Vercel optimized",
            "24/7 hosting ready"
        ],
        "Developer": "Basic Coders | @SajagOG",
        "github": "https://github.com/SajagOG"
    })

# Error handlers for fast error responses
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "Developer": "Basic Coders | @SajagOG"
    }), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "Developer": "Basic Coders | @SajagOG"
    }), 500

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "Developer": "Basic Coders | @SajagOG"
    }), 405

# Optimize Flask settings for production
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
else:
    # For Vercel
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False  # Faster JSON
    app.config['JSON_SORT_KEYS'] = False  # Faster response
