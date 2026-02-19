# Quick Reference Card

## 🚀 Getting Started (Copy-Paste)

### 1. Setup (5 min)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with AWS credentials
```

### 2. Run Server (1 min)
```bash
python main.py
# Visit: http://localhost:8000/docs
```

### 3. Train Model (depends on data size)
```bash
# First download dataset to data/train/ and data/val/
python scripts/train_model.py
```

### 4. Test API (2 min)
```bash
python example_usage.py
```

---

## 📡 API Quick Reference

### Create Patient
```bash
curl -X POST http://localhost:8000/patients/ \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","age":45,"email":"john@example.com"}'
```

### Predict DR
```bash
curl -X POST http://localhost:8000/predict/ \
  -F "patient_id=<id>" \
  -F "visit_type=pre-treatment" \
  -F "file=@image.jpg"
```

### Get History
```bash
curl http://localhost:8000/predict/patient/<patient_id>/history
```

### Health Check
```bash
curl http://localhost:8000/health
```

---

## 🐳 Docker Commands

```bash
# Build
docker build -t clarity-in-care:latest .

# Run locally
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down

# Push to ECR
docker tag clarity-in-care:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/clarity:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/clarity:latest
```

---

## 📂 Directory Map

```
backend/
├── main.py              ← FastAPI entry point
├── app/
│   ├── api/             ← Endpoints (patients, predictions)
│   └── schemas.py       ← Data validation
├── config/
│   └── settings.py      ← Configuration
├── database/
│   └── models.py        ← DB schema (Patient, Scan)
├── preprocessing/
│   └── image_processor.py ← Image processing
├── models/
│   └── dr_model.py      ← Model inference
├── explainability/
│   └── grad_cam.py      ← XAI heatmaps
├── cloud_storage/
│   └── s3_storage.py    ← AWS S3
├── scripts/
│   └── train_model.py   ← Model training
├── requirements.txt     ← Dependencies
├── .env.example        ← Config template
└── README.md           ← Full documentation
```

---

## ⚙️ Key Files to Modify

### Add New Endpoint
**File**: `app/api/predictions.py` (or create new file)
```python
@router.get("/my-endpoint/{id}")
def my_endpoint(id: str, db: Session = Depends(get_db)):
    return {"message": "your response"}
```

### Change Model Input Size
**File**: `config/settings.py`
```python
INPUT_IMAGE_SIZE = (224, 224)  # Change here
```

### Add New Database Field
**File**: `database/models.py`
```python
class Scan(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True)
    new_field = Column(String)  # Add here
```

### Adjust Model Training
**File**: `scripts/train_model.py`
```python
trainer = DRDetectionTrainer(
    num_epochs=10,      # Change here
    batch_size=32,      # Or here
    learning_rate=0.001 # Or here
)
```

---

## 🔧 Environment Variables (.env)

```
DEBUG=False
HOST=0.0.0.0
PORT=8000
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
S3_BUCKET_NAME=clarity-in-care-images
DATABASE_URL=sqlite:///./clarity_in_care.db
MODEL_PATH=./models/dr_detection_model.pth
```

---

## 📊 API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | Health check |
| POST | /patients/ | Create patient |
| GET | /patients/{id} | Get patient |
| GET | /patients/ | List patients |
| POST | /predict/ | Predict DR |
| GET | /predict/patient/{id}/history | Scan history |

---

## 🐛 Debugging

```bash
# Check logs
docker-compose logs api

# Check database
sqlite3 clarity_in_care.db
> .tables
> SELECT * FROM patients;

# Check S3
aws s3 ls s3://clarity-in-care-images/

# Check Python
python -c "import torch; print(torch.cuda.is_available())"
```

---

## ⚡ Common Commands

```bash
# Start API
python main.py

# Train model
python scripts/train_model.py

# Test API
python example_usage.py

# Docker
docker-compose up -d
docker-compose down
docker-compose logs -f

# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Deploy to AWS
git push origin main  # CI/CD triggers
```

---

## 📚 Documentation Files

| File | Content |
|------|---------|
| README.md | Full documentation |
| SETUP_GUIDE.md | Quick setup |
| DEPLOYMENT.md | Cloud deployment |
| FILE_STRUCTURE.md | File explanations |
| IMPLEMENTATION_CHECKLIST.md | Step-by-step checklist |
| example_usage.py | Python examples |

---

## 🎯 MVP Checklist (Quick Version)

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure `.env` with AWS credentials
- [ ] Download DR dataset
- [ ] Train model: `python scripts/train_model.py`
- [ ] Start API: `python main.py`
- [ ] Test endpoints: `python example_usage.py`
- [ ] Push to GitHub
- [ ] Deploy to AWS (see DEPLOYMENT.md)

---

## ❓ FAQ

**Q: Where's the model?**
A: `models/dr_detection_model.pth` (created after training)

**Q: How to change image size?**
A: Edit `INPUT_IMAGE_SIZE` in `config/settings.py`

**Q: Where's the database?**
A: `clarity_in_care.db` (created on first run)

**Q: How to use GPU?**
A: Automatic! FastAPI detects CUDA and uses GPU

**Q: How to deploy?**
A: See `DEPLOYMENT.md` for full AWS guide

**Q: How to add new endpoint?**
A: Add route to `app/api/*.py` and include in `main.py`

**Q: How to change database?**
A: Edit `DATABASE_URL` in `.env`

**Q: Problem with S3?**
A: Check AWS credentials in `.env` and bucket name

---

## 🚀 Production Deployment (One-Liner)

```bash
# On AWS EC2
git clone <repo> && cd Clarity-In-Care/backend && \
docker-compose up -d && \
echo "✓ API running at http://localhost:8000"
```

---

## 📖 Learning Path

1. **First 30 min**: Read SETUP_GUIDE.md
2. **Next hour**: Get dependencies running
3. **Next 2 hours**: Train small model
4. **Next hour**: Test API with example_usage.py
5. **Next day**: Deploy to AWS

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Run `pip install -r requirements.txt` |
| "Port 8000 in use" | Kill process or change port in `.env` |
| "Model not loading" | Train model: `python scripts/train_model.py` |
| "S3 error" | Check `.env` AWS credentials |
| "Prediction fails" | Check logs: `docker-compose logs api` |
| "Database error" | Delete `clarity_in_care.db` and restart |

---

**Pro Tips:**
- Use `--help` flag for more info: `python main.py --help`
- Check API docs in browser: `http://localhost:8000/docs`
- Use VS Code REST Client extension for testing
- Enable GPU with `CUDA_VISIBLE_DEVICES=0`
- Cache model after first load (already implemented)

---

**Keep this card handy for quick reference!**
