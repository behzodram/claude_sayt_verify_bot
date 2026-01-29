from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
from config import SECRET_KEY, REDIS_HOST, REDIS_PORT, REDIS_DB, VERIFICATION_QUEUE, CODE_EXPIRE_TIME
import firebase_admin
from firebase_admin import credentials, db
import redis
import logging
from datetime import datetime

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Initialize Firebase (faqat ma'lumot yozish uchun)
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://claude-sayt-verify-bot-default-rtdb.firebaseio.com'
})

# Redis connection (faqat bot bilan aloqa uchun)
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)




from flask_cors import CORS

# GitHub Pages frontend uchun CORS
CORS(app, origins=["https://username.github.io"], supports_credentials=True)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json() or {}
    code = data.get('code', '').strip()

    if not code or len(code) != 4 or not code.isdigit():
        return jsonify(success=False, message='4 xonali kod kiriting'), 400

    metadata = pop_verification_from_queue(code)  # Redis’dan olingan

    if not metadata:
        return jsonify(success=False, message='Noto‘g‘ri yoki eskirgan kod'), 401

    user_id = metadata['user_id']
    save_user_to_firebase(user_id, metadata)  # Firebase yozish

    session['user_id'] = user_id  # browser bilan bog‘lash

    return jsonify(success=True, message='Tasdiqlash muvaffaqiyatli!')







def get_verification_from_queue(code):
    """Get verification metadata from Redis queue by code"""
    try:
        queue_length = redis_client.llen(VERIFICATION_QUEUE)
        
        for _ in range(queue_length):
            data = redis_client.rpop(VERIFICATION_QUEUE)
            if data:
                metadata = json.loads(data)
                
                if metadata.get('code') == code:
                    user_id = metadata.get('user_id')
                    
                    # Verify code hasn't expired
                    key = f"verification:{user_id}"
                    stored_code = redis_client.get(key)
                    
                    if stored_code == code:
                        redis_client.delete(key)
                        logger.info(f"Kod tasdiqlandi: {user_id}")
                        return metadata
        
        return None
    except Exception as e:
        logger.error(f"Queue xatosi: {e}")
        return None

def save_user_to_firebase(user_id, metadata):
    """Save verified user to Firebase Realtime Database"""
    try:
        ref = db.reference('verified_users')
        
        user_data = {
            'telegram_id': user_id,
            'username': metadata.get('username', ''),
            'first_name': metadata.get('first_name', ''),
            'last_name': metadata.get('last_name', ''),
            'verified_at': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'status': 'active',
            'verification_method': 'telegram_bot'
        }
        
        # Save user data under telegram_id
        ref.child(user_id).set(user_data)
        
        # Also create a users_by_date reference for analytics
        date_ref = db.reference(f'users_by_date/{datetime.now().strftime("%Y-%m-%d")}')
        date_ref.child(user_id).set({
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"User Firebase ga saqlandi: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Firebase xatosi: {e}")
        return False

@app.route('/')
def index():
    """Main page - show verification form"""
    return render_template('index.html')

# @app.route('/verify', methods=['POST'])
# def verify():
#     """Verify user with code only"""
#     data = request.get_json()
#     code = data.get('code', '').strip()
    
#     if not code:
#         return jsonify({
#             'success': False,
#             'message': 'Kodni kiriting'
#         }), 400
    
#     if len(code) != 4 or not code.isdigit():
#         return jsonify({
#             'success': False,
#             'message': '4 xonali kod kiriting'
#         }), 400
    
#     # Get metadata from Redis queue
#     metadata = get_verification_from_queue(code)
    
#     if metadata:
#         user_id = metadata.get('user_id')
        
#         # Save to Firebase
#         if save_user_to_firebase(user_id, metadata):
#             return jsonify({
#                 'success': True,
#                 'message': 'Tasdiqlash muvaffaqiyatli!',
#                 'user_id': user_id,
#                 'user_data': {
#                     'username': metadata.get('username', ''),
#                     'first_name': metadata.get('first_name', ''),
#                     'last_name': metadata.get('last_name', '')
#                 }
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'message': 'Firebase xatosi. Qaytadan urinib ko\'ring.'
#             }), 500
#     else:
#         return jsonify({
#             'success': False,
#             'message': 'Noto\'g\'ri kod yoki kod muddati tugagan'
#         }), 401

@app.route('/firebase-data', methods=['POST'])
def firebase_data():
    """Handle data operations for Firebase from frontend"""
    if not request.is_json:
        return jsonify({'success': False, 'message': 'JSON format expected'}), 400
    
    data = request.get_json()
    action = data.get('action')
    
    if action == 'write':
        # Frontend Firebase dan yozgandan so'ng bu endpoint ga ham yuborishi mumkin
        # Bu opsiyonel, tracking uchun
        logger.info(f"Frontend Firebase yozdi: {data.get('path')}")
        return jsonify({'success': True, 'message': 'Log qabul qilindi'})
    
    return jsonify({'success': False, 'message': 'Noto\'g\'ri action'}), 400

@app.route('/api/redis-status')
def redis_status():
    """Check Redis connection status"""
    try:
        redis_client.ping()
        queue_length = redis_client.llen(VERIFICATION_QUEUE)
        return jsonify({
            'status': 'connected',
            'queue_length': queue_length
        })
    except Exception as e:
        return jsonify({
            'status': 'disconnected',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Test Redis connection
    try:
        redis_client.ping()
        logger.info("Redis ulanishi muvaffaqiyatli! Bot bilan aloqa tayyor.")
    except Exception as e:
        logger.error(f"Redis ulanish xatosi: {e}")
        logger.error("Iltimos Redis serverini ishga tushiring!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)