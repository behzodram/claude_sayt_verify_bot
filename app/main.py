from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import json
import os
from config import SECRET_KEY
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

def load_verifications():
    """Load verification codes from bot's storage"""
    if os.path.exists('verification_data.json'):
        try:
            with open('verification_data.json', 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def verify_code(user_id, code):
    """Verify the code from user input"""
    verifications = load_verifications()
    
    if user_id in verifications:
        data = verifications[user_id]
        expire_time = datetime.fromisoformat(data['expires_at'])
        
        # Check if code is valid and not expired
        if datetime.now() < expire_time and data['code'] == code:
            # Remove used code
            del verifications[user_id]
            with open('verification_data.json', 'w') as f:
                json.dump(verifications, f)
            return True
    return False

def save_user_to_firebase(user_id):
    """Save verified user to Firebase Realtime Database"""
    ref = db.reference('verified_users')
    ref.child(user_id).set({
        'user_id': user_id,
        'verified_at': datetime.now().isoformat(),
        'status': 'active'
    })

@app.route('/')
def index():
    """Main page - check if user is verified"""
    if 'user_id' in session and session.get('verified'):
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    """Verify user with Telegram ID and code"""
    data = request.get_json()
    user_id = data.get('user_id', '').strip()
    code = data.get('code', '').strip()
    
    if not user_id or not code:
        return jsonify({
            'success': False,
            'message': 'Telegram ID va kodni kiriting'
        }), 400
    
    # Verify the code
    if verify_code(user_id, code):
        # Save to Firebase
        try:
            save_user_to_firebase(user_id)
            
            # Set session
            session['user_id'] = user_id
            session['verified'] = True
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Tasdiqlash muvaffaqiyatli!',
                'redirect': url_for('dashboard')
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Xatolik yuz berdi: {str(e)}'
            }), 500
    else:
        return jsonify({
            'success': False,
            'message': 'Noto\'g\'ri kod yoki kod muddati tugagan'
        }), 401

@app.route('/dashboard')
def dashboard():
    """Main dashboard after verification"""
    if 'user_id' not in session or not session.get('verified'):
        return redirect(url_for('index'))
    
    return render_template('dashboard.html', user_id=session['user_id'])

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/check-session')
def check_session():
    """Check if user session is valid"""
    if 'user_id' in session and session.get('verified'):
        return jsonify({
            'authenticated': True,
            'user_id': session['user_id']
        })
    return jsonify({'authenticated': False}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)