from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from PIL import Image
import numpy as np
import os, uuid, json

app = Flask(__name__, static_folder='..', static_url_path='')
CORS(app)

# ── CONFIG ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DB_PATH = os.path.join(BASE_DIR, 'database', 'cropdoc.db')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

# ── MODELS ──
class Scan(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    scan_id    = db.Column(db.String(36), unique=True, nullable=False)
    crop       = db.Column(db.String(50))
    disease    = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    severity   = db.Column(db.String(20))
    severity_pct = db.Column(db.Float)
    health_score = db.Column(db.Float)
    image_path = db.Column(db.String(200))
    treatment  = db.Column(db.Text)
    status     = db.Column(db.String(20), default='detected')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProgressLog(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    scan_id    = db.Column(db.String(36))
    day        = db.Column(db.Integer)
    health_score = db.Column(db.Float)
    severity_pct = db.Column(db.Float)
    note       = db.Column(db.String(200))
    image_path = db.Column(db.String(200))
    logged_at  = db.Column(db.DateTime, default=datetime.utcnow)

# ── DISEASE DATABASE ──
DISEASE_DB = {
    "Early Blight": {
        "scientific": "Alternaria solani",
        "crops": ["Tomato", "Potato"],
        "treatment": [
            {"day": "Day 1–3",  "name": "Neem Oil Spray",        "instruction": "Mix 5ml per litre of water. Apply in the morning or evening.", "dose": "5ml/L · 3 days"},
            {"day": "Day 4–7",  "name": "Compost Tea",           "instruction": "Remove infected leaves first. Apply as a soil drench around the plant base.", "dose": "200ml/plant · 4 days"},
            {"day": "Day 8–14", "name": "Turmeric + Garlic Spray","instruction": "Dissolve turmeric and garlic paste in water and spray on all affected leaves.", "dose": "10ml/L · 7 days"}
        ],
        "preventive": "Improve air circulation, avoid overhead watering, practice crop rotation next season."
    },
    "Late Blight": {
        "scientific": "Phytophthora infestans",
        "crops": ["Tomato", "Potato"],
        "treatment": [
            {"day": "Day 1–3",  "name": "Copper Fungicide Spray", "instruction": "Mix copper sulfate solution and spray on all leaves.", "dose": "3g/L · 3 days"},
            {"day": "Day 4–10", "name": "Baking Soda Spray",      "instruction": "Mix 1 tsp baking soda per litre of water with a few drops of soap.", "dose": "1tsp/L · 7 days"},
            {"day": "Day 11–14","name": "Neem Oil Spray",         "instruction": "Apply neem oil spray as a follow-up preventive treatment.", "dose": "5ml/L · 4 days"}
        ],
        "preventive": "Remove and destroy infected plant material. Avoid wetting foliage when watering."
    },
    "Rust": {
        "scientific": "Puccinia spp.",
        "crops": ["Wheat", "Cotton"],
        "treatment": [
            {"day": "Day 1–5",  "name": "Sulfur Dust",           "instruction": "Apply sulfur dust on affected leaves in the early morning.", "dose": "2g/plant · 5 days"},
            {"day": "Day 6–10", "name": "Garlic Extract Spray",  "instruction": "Blend garlic with water, strain and spray on all surfaces.", "dose": "50ml/L · 5 days"},
            {"day": "Day 11–14","name": "Neem Oil Spray",        "instruction": "Apply neem oil as a final preventive coat.", "dose": "5ml/L · 4 days"}
        ],
        "preventive": "Plant resistant varieties. Ensure proper spacing for air circulation."
    },
    "Leaf Blast": {
        "scientific": "Magnaporthe oryzae",
        "crops": ["Rice"],
        "treatment": [
            {"day": "Day 1–4",  "name": "Silicon Spray",         "instruction": "Apply potassium silicate solution to strengthen leaf tissue.", "dose": "2ml/L · 4 days"},
            {"day": "Day 5–10", "name": "Trichoderma Solution",  "instruction": "Apply Trichoderma-based bio-fungicide to soil and leaves.", "dose": "5g/L · 6 days"},
            {"day": "Day 11–14","name": "Neem Cake Application", "instruction": "Apply neem cake to the soil around the plant base.", "dose": "50g/plant · 4 days"}
        ],
        "preventive": "Avoid excessive nitrogen fertilizer. Maintain proper water levels in paddy fields."
    },
    "Healthy": {
        "scientific": "No disease detected",
        "crops": ["All"],
        "treatment": [],
        "preventive": "Continue regular monitoring. Maintain proper irrigation and nutrition schedule."
    }
}

# ── HELPER: AI DIAGNOSIS (Simulated — replace with real model) ──
def analyze_image(image_path, crop_hint=None):
    """
    Simulates AI diagnosis.
    Replace this function body with real TensorFlow model inference:
        model = tf.keras.models.load_model('model/model.h5')
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=(224,224))
        img_array = tf.keras.preprocessing.image.img_to_array(img) / 255.0
        prediction = model.predict(np.expand_dims(img_array, axis=0))
    """
    img = Image.open(image_path).convert('RGB')
    img_array = np.array(img.resize((224, 224))) / 255.0
    mean_color = img_array.mean(axis=(0, 1))

    # Simulate disease based on image color characteristics
    green_ratio = float(mean_color[1]) / (float(mean_color[0]) + 0.001)

    if green_ratio > 1.3:
        disease, confidence = "Healthy", 0.91
    elif green_ratio > 1.1:
        disease, confidence = "Early Blight", 0.87
    elif green_ratio > 0.9:
        disease, confidence = "Late Blight", 0.82
    elif green_ratio > 0.7:
        disease, confidence = "Rust", 0.79
    else:
        disease, confidence = "Leaf Blast", 0.75

    # Severity
    if confidence > 0.88:
        severity, severity_pct = "mild", round(np.random.uniform(10, 25), 1)
    elif confidence > 0.80:
        severity, severity_pct = "moderate", round(np.random.uniform(30, 55), 1)
    else:
        severity, severity_pct = "severe", round(np.random.uniform(60, 85), 1)

    if disease == "Healthy":
        severity, severity_pct = "mild", 0.0

    health_score = round(100 - (severity_pct * 0.7), 1)
    crop = crop_hint or "Tomato"

    # Top 3 predictions
    all_diseases = list(DISEASE_DB.keys())
    predictions = [{"disease": disease, "confidence": round(confidence * 100, 1)}]
    remaining = [d for d in all_diseases if d != disease]
    leftover = round((1 - confidence) * 100, 1)
    predictions.append({"disease": remaining[0], "confidence": round(leftover * 0.7, 1)})
    predictions.append({"disease": remaining[1], "confidence": round(leftover * 0.3, 1)})

    treatment_info = DISEASE_DB.get(disease, DISEASE_DB["Healthy"])

    return {
        "disease": disease,
        "scientific_name": treatment_info["scientific"],
        "confidence": round(confidence * 100, 1),
        "severity": severity,
        "severity_pct": severity_pct,
        "health_score": health_score,
        "crop": crop,
        "predictions": predictions,
        "treatment": treatment_info["treatment"],
        "preventive": treatment_info["preventive"]
    }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ── ROUTES ──

# Serve frontend
@app.route('/')
def index():
    return send_from_directory('..', 'index.html')

# POST /api/diagnose — upload image and get diagnosis
@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    if 'photo' not in request.files:
        return jsonify({"error": "No photo uploaded"}), 400

    file = request.files['photo']
    crop = request.form.get('crop', 'Tomato')

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Use JPG, PNG or WEBP"}), 400

    scan_id = str(uuid.uuid4())
    filename = f"{scan_id}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    result = analyze_image(filepath, crop)

    scan = Scan(
        scan_id      = scan_id,
        crop         = result['crop'],
        disease      = result['disease'],
        confidence   = result['confidence'],
        severity     = result['severity'],
        severity_pct = result['severity_pct'],
        health_score = result['health_score'],
        image_path   = filename,
        treatment    = json.dumps(result['treatment']),
        status       = 'healthy' if result['disease'] == 'Healthy' else 'detected'
    )
    db.session.add(scan)
    db.session.add(ProgressLog(
        scan_id      = scan_id,
        day          = 1,
        health_score = result['health_score'],
        severity_pct = result['severity_pct'],
        note         = "Initial diagnosis"
    ))
    db.session.commit()

    return jsonify({"scan_id": scan_id, **result}), 200

# GET /api/scans — get all scan history
@app.route('/api/scans', methods=['GET'])
def get_scans():
    scans = Scan.query.order_by(Scan.created_at.desc()).limit(50).all()
    return jsonify([{
        "scan_id":      s.scan_id,
        "crop":         s.crop,
        "disease":      s.disease,
        "confidence":   s.confidence,
        "severity":     s.severity,
        "severity_pct": s.severity_pct,
        "health_score": s.health_score,
        "status":       s.status,
        "image_url":    f"/api/image/{s.image_path}",
        "created_at":   s.created_at.strftime("%Y-%m-%d %H:%M")
    } for s in scans])

# GET /api/dashboard — farm stats
@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    total   = Scan.query.count()
    healthy = Scan.query.filter_by(status='healthy').count()
    diseased = total - healthy
    avg_health = db.session.query(db.func.avg(Scan.health_score)).scalar() or 0

    disease_counts = db.session.query(
        Scan.disease, db.func.count(Scan.disease)
    ).group_by(Scan.disease).all()

    return jsonify({
        "total_scanned": total,
        "healthy":       healthy,
        "diseased":      diseased,
        "farm_health_score": round(avg_health, 1),
        "disease_breakdown": [{"disease": d, "count": c} for d, c in disease_counts]
    })

# GET /api/scan/<scan_id> — get single scan detail
@app.route('/api/scan/<scan_id>', methods=['GET'])
def get_scan(scan_id):
    s = Scan.query.filter_by(scan_id=scan_id).first_or_404()
    logs = ProgressLog.query.filter_by(scan_id=scan_id).order_by(ProgressLog.day).all()
    return jsonify({
        "scan_id":       s.scan_id,
        "crop":          s.crop,
        "disease":       s.disease,
        "confidence":    s.confidence,
        "severity":      s.severity,
        "severity_pct":  s.severity_pct,
        "health_score":  s.health_score,
        "treatment":     json.loads(s.treatment),
        "status":        s.status,
        "image_url":     f"/api/image/{s.image_path}",
        "created_at":    s.created_at.strftime("%Y-%m-%d %H:%M"),
        "progress_logs": [{"day": l.day, "health_score": l.health_score, "severity_pct": l.severity_pct, "note": l.note} for l in logs]
    })

# POST /api/progress/<scan_id> — log a follow-up progress entry
@app.route('/api/progress/<scan_id>', methods=['POST'])
def log_progress(scan_id):
    data = request.get_json()
    scan = Scan.query.filter_by(scan_id=scan_id).first_or_404()
    last_log = ProgressLog.query.filter_by(scan_id=scan_id).order_by(ProgressLog.day.desc()).first()
    next_day = (last_log.day + 1) if last_log else 1

    log = ProgressLog(
        scan_id      = scan_id,
        day          = next_day,
        health_score = data.get('health_score', scan.health_score),
        severity_pct = data.get('severity_pct', scan.severity_pct),
        note         = data.get('note', '')
    )
    if data.get('health_score'):
        scan.health_score = data['health_score']
        scan.status = 'recovered' if data['health_score'] >= 85 else 'treating'

    db.session.add(log)
    db.session.commit()
    return jsonify({"message": "Progress logged", "day": next_day})

# PATCH /api/scan/<scan_id>/status — update scan status
@app.route('/api/scan/<scan_id>/status', methods=['PATCH'])
def update_status(scan_id):
    scan = Scan.query.filter_by(scan_id=scan_id).first_or_404()
    data = request.get_json()
    scan.status = data.get('status', scan.status)
    db.session.commit()
    return jsonify({"message": "Status updated"})

# DELETE /api/scan/<scan_id> — delete a scan
@app.route('/api/scan/<scan_id>', methods=['DELETE'])
def delete_scan(scan_id):
    scan = Scan.query.filter_by(scan_id=scan_id).first_or_404()
    image_path = os.path.join(UPLOAD_FOLDER, scan.image_path)
    if os.path.exists(image_path):
        os.remove(image_path)
    ProgressLog.query.filter_by(scan_id=scan_id).delete()
    db.session.delete(scan)
    db.session.commit()
    return jsonify({"message": "Scan deleted"})

# GET /api/image/<filename> — serve uploaded images
@app.route('/api/image/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# GET /api/weather-risk — simulated weather risk forecast
@app.route('/api/weather-risk', methods=['GET'])
def weather_risk():
    forecast = [
        {"day": "Today",    "temp": 32, "humidity": 65, "condition": "Sunny",       "risk": "low",    "risk_pct": 25},
        {"day": "Tomorrow", "temp": 29, "humidity": 78, "condition": "Partly Cloudy","risk": "medium", "risk_pct": 55},
        {"day": "Day 3",    "temp": 26, "humidity": 92, "condition": "Rainy",        "risk": "high",   "risk_pct": 85},
        {"day": "Day 4",    "temp": 25, "humidity": 88, "condition": "Rainy",        "risk": "high",   "risk_pct": 75},
        {"day": "Day 5",    "temp": 31, "humidity": 60, "condition": "Sunny",        "risk": "low",    "risk_pct": 30},
    ]
    alert = None
    for day in forecast:
        if day['risk'] == 'high':
            alert = f"{day['day']} Alert: High humidity ({day['humidity']}%) combined with {day['condition'].lower()} significantly increases fungal disease risk. Apply preventive neem spray beforehand."
            break
    return jsonify({"forecast": forecast, "alert": alert})

# GET /api/health — server health check
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "message": "CropDoc API is running"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized")
    print("🌿 CropDoc backend running at http://localhost:5000")
    app.run(debug=True, port=5000)
