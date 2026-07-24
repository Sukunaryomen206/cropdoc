# 🌿 CropDoc — AI-Powered Offline Crop Disease Diagnostician

> Upload a leaf photo. Get an instant disease diagnosis, severity score, and a day-by-day organic treatment plan — built for farmers, in their own language.

Built for the **[Odoo x LDCE Ahmedabad Hackathon 26](https://hackathon.odoo.com/event/odoo-x-ldce-ahmedabad-hackathon-26-29/register)**.

---

## 📖 About

Crop diseases destroy an estimated 20–40% of global agricultural yield every year, and smallholder farmers are hit hardest — they often lack access to agronomists, reliable internet, or affordable early-detection tools. By the time disease symptoms are visible to the naked eye, treatment is more expensive and less effective.

**CropDoc** lets a farmer photograph a leaf and instantly receive:

- 🔍 Disease name, scientific name, and AI confidence score
- 📊 Severity rating (Mild / Moderate / Severe) with an exact percentage
- ❤️ An overall Crop Health Score out of 100
- 🌱 A day-by-day **organic treatment plan** using locally available materials (neem, turmeric, garlic, etc.)
- 🔊 **Voice guidance** in English, Hindi, and Gujarati
- 📈 A **farm dashboard** to track scan history and disease trends
- 🌦️ A **5-day weather-based disease risk forecast**

---

## ✨ Features

| Feature | Description |
|---|---|
| AI Leaf Diagnosis | Drag-and-drop or browse to upload a leaf photo for instant disease prediction |
| Severity Scoring | Mild / Moderate / Severe classification with a precise severity % |
| AI Heatmap Overlay | Highlights the affected regions of the leaf |
| Organic Treatment Plans | Step-by-step, day-wise treatment schedules using low-cost organic remedies |
| Crop Health Score | Single 0–100 score summarizing plant health at a glance |
| Voice Guidance | Reads results aloud in English, Hindi, or Gujarati (Web Speech API) |
| Farm Dashboard | Total scans, healthy vs. diseased counts, weekly analytics |
| Disease Risk Prediction | 5-day fungal disease risk forecast based on weather |
| Progress Tracking | Before/after comparison to track recovery over time |
| Multilingual UI | Full interface translation: English, Hindi, Gujarati |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, vanilla JavaScript (ES6), Font Awesome, Google Fonts |
| Backend | Python 3, Flask, Flask-CORS |
| Database | SQLite via Flask-SQLAlchemy |
| Image Processing | Pillow (PIL), NumPy |
| Voice | Browser-native Web Speech API |

---

## 📁 Project Structure

```
cropdoc/
├── backend/
│   ├── app.py              # Flask app: models, routes, diagnosis engine
│   ├── requirements.txt    # Python dependencies
│   ├── database/           # SQLite database (auto-created on first run)
│   ├── uploads/             # Uploaded leaf images (auto-created)
│   └── model/                # Reserved for a future trained ML model
├── index.html               # Single-page frontend
├── script.js                 # Frontend logic (upload, dashboard, voice, i18n)
├── styles.css                 # Styling
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- pip

### 1. Clone the repo
```bash
git clone https://github.com/Sukunaryomen206/cropdoc.git
cd cropdoc
```

### 2. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run the server
```bash
python app.py
```
You should see:
```
✅ Database initialized
🌿 CropDoc backend running at http://localhost:5000
```

### 4. Open the app
Go to **`http://localhost:5000/`** in your browser — Flask serves the frontend directly, so no separate web server is needed.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/diagnose` | Upload a leaf photo + crop type → full diagnosis JSON |
| `GET` | `/api/scans` | Most recent 50 scans |
| `GET` | `/api/dashboard` | Aggregated farm statistics |
| `GET` | `/api/scan/<id>` | Full detail for one scan, incl. progress log |
| `POST` | `/api/progress/<id>` | Log a follow-up progress entry |
| `PATCH` | `/api/scan/<id>/status` | Update a scan's status |
| `DELETE` | `/api/scan/<id>` | Delete a scan and its image |
| `GET` | `/api/image/<file>` | Serve an uploaded leaf image |
| `GET` | `/api/weather-risk` | 5-day disease-risk forecast |
| `GET` | `/api/health` | Server health check |

---

## 🗺️ Roadmap

- [ ] Replace the simulated diagnosis logic with a real trained CNN (e.g. MobileNet / TensorFlow Lite fine-tuned on PlantVillage)
- [ ] Integrate a live weather API for location-based risk forecasting
- [ ] Progressive Web App (PWA) support for true offline installability
- [ ] Migrate to PostgreSQL + cloud image storage for production deployment
- [ ] Farmer accounts / authentication for personalized dashboards

> **Note:** The current diagnosis engine (`analyze_image()` in `app.py`) uses a simplified, color-ratio-based simulation as a placeholder for a real machine learning model. This keeps the full-stack flow demonstrable end-to-end while the ML model is developed.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to open a pull request or issue.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

Built for the **Odoo x LDCE Ahmedabad Hackathon 26**, organized by Odoo IN Private Limited in association with L.D. College of Engineering, Ahmedabad.

🌾 *Built to help farmers grow better.*
