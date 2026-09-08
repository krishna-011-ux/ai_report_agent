# AI Agent for Automated Data Pipeline & Report Generation

Ye ek complete, working automation system hai jo kisi bhi data source se data
uthata hai, use clean karta hai, AI (Claude) se insights nikalta hai, aur
professional PDF/Excel report bana kar (chahe to email se) bhej deta hai.

```
Data Source → Cleaning → AI Analysis → Report Generation → Delivery
  (CSV/Excel/    (Pandas)    (Claude API)     (PDF/Excel)      (Email)
   SQL/API/
   Google Sheet)
```

## 📁 Project Structure

```
ai_report_agent/
├── main.py                  # Entry point - poora pipeline yahan se chalta hai
├── scheduler.py             # Automation - daily/weekly auto-run ke liye
├── requirements.txt         # Saari zaroori libraries
├── config/
│   └── config.yaml          # SAB KUCH YAHAN SE CONTROL HOTA HAI
├── connectors/               # Data sources
│   ├── csv_connector.py
│   ├── excel_connector.py
│   ├── sql_connector.py
│   ├── api_connector.py
│   └── gsheet_connector.py
├── processing/
│   └── cleaner.py            # Data cleaning logic
├── ai_agent/
│   └── analyzer.py           # Claude API se insights generate karta hai
├── reports/
│   ├── pdf_report.py
│   ├── excel_report.py
│   └── email_sender.py
├── sample_data/
│   └── sample_sales.csv      # Testing ke liye demo data
└── outputs/                  # Generated reports yahan aayenge
```

## 🚀 Setup (Pehli Baar)

### 1. Dependencies install karo
```bash
pip install -r requirements.txt
```

### 2. AI insights ke liye API key set karo (optional par recommended)
```bash
export ANTHROPIC_API_KEY="your-key-here"
```
Key yahan se milegi: https://console.anthropic.com

> Agar key nahi doge, to bhi pipeline chalega — bas AI insights ki jagah
> basic statistical summary (average, min, max) use hoga.

### 3. `config/config.yaml` kholo aur apni requirement ke hisaab se set karo

## 🌐 Web App (Streamlit) — Sab Log Use Kar Sakein

Command-line ki jagah agar ek **browser-based web app** chahiye jise koi bhi
(non-technical log bhi) file upload karke use kar sake:

```bash
streamlit run streamlit_app.py
```

Ye local browser mein khul jayega. **Public link banake sabke saath share
karna ho** (WhatsApp, email, etc.), to **`DEPLOY.md`** file dekho — usme
Streamlit Community Cloud (free) pe 10-minute deployment guide hai.

## ▶️ Chalane Ka Tarika (Command-Line Version)

**Ek baar run karna ho:**
```bash
python main.py
```

**Automatic scheduling (roz/weekly khud chalta rahe):**
```bash
python scheduler.py
```
config.yaml mein `schedule.enabled: true` karo pehle.

**Production mein Linux cron job se chalana** (sabse reliable):
```bash
crontab -e
# Har roz subah 9 baje chalayega:
0 9 * * * cd /path/to/ai_report_agent && python3 main.py >> logs.txt 2>&1
```

## 🔌 Data Source Kaise Change Karein

`config/config.yaml` mein sirf ek line change karni hai:

```yaml
data_source:
  source_type: "csv"     # <- ye badlo: csv / excel / sql / api / gsheet
```

### CSV
```yaml
csv:
  path: "sample_data/sample_sales.csv"
```

### Excel
```yaml
excel:
  path: "sample_data/sample_sales.xlsx"
  sheet_name: 0
```

### SQL Database (PostgreSQL / MySQL / SQLite)
```yaml
sql:
  connection_string: "postgresql://user:password@host:5432/dbname"
  query: "SELECT * FROM sales"
```

### REST API
```yaml
api:
  url: "https://api.example.com/sales-data"
  method: "GET"
  headers:
    Authorization: "Bearer YOUR_TOKEN"
```

### Google Sheets
1. Google Cloud Console mein Service Account banao, JSON key download karo
2. Apni Sheet ko us service account email ke saath share karo
3. Config mein:
```yaml
gsheet:
  sheet_id: "YOUR_SHEET_ID"
  credentials_file: "config/gcreds.json"
```

## 📊 Report Format Kaise Change Karein

```yaml
report:
  formats: ["pdf", "excel"]   # dono chahiye to dono likho, ek chahiye to ek
  title: "My Custom Report Title"
```

## 📧 Email Delivery On Karne Ke Liye

```yaml
delivery:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender_email: "your_email@gmail.com"
    sender_password: "YOUR_GMAIL_APP_PASSWORD"   # normal password nahi chalega
    recipients: ["client@example.com"]
```
Gmail App Password yahan banega: https://myaccount.google.com/apppasswords

## 🧩 Naya Data Source Add Karna Ho (Extend Karna)

1. `connectors/` mein nayi file banao, jaise `mongodb_connector.py`
2. `BaseConnector` se inherit karo aur `fetch()` method likho
3. `connectors/__init__.py` mein `CONNECTOR_MAP` dictionary mein add kar do

Bas — poora pipeline automatically naya source use kar payega, kahi aur
kuch change nahi karna padega. Yahi modular design ka fayda hai.

## 🏭 Real-Life Deployment Options

| Option | Best For |
|---|---|
| Cron job (Linux server/VM) | Simple, reliable, low-cost |
| GitHub Actions (scheduled workflow) | Free tier available, code + automation same jagah |
| AWS Lambda + EventBridge | Serverless, scale automatically |
| Docker container + Kubernetes CronJob | Enterprise scale, multiple pipelines |
| Windows Task Scheduler | Agar office Windows machine pe chalana hai |

## ⚠️ Important Notes

- **API costs**: Har run pe Claude API ek chhota sa call hota hai — data ka
  poora raw data nahi, sirf statistical summary bheja jata hai (fast + cheap).
- **Security**: Passwords/API keys ko kabhi bhi config.yaml mein hardcode
  karke Git mein commit mat karo. Production mein environment variables ya
  secrets manager (AWS Secrets Manager, etc.) use karo.
- **Bade datasets**: Agar data lakhon rows ka hai, to Pandas ki jagah
  PySpark/Dask consider karo — is code mein Pandas use hua hai jo
  small-to-medium data (~lakhs rows tak) ke liye perfectly fine hai.

## 🔮 Future Enhancements (Aap khud add kar sakte ho)

- [ ] Multiple report recipients ke liye alag-alag filtered views
- [ ] Slack/Teams delivery connector add karna
- [ ] Predictive analytics (forecast next month's numbers)
- [ ] Web dashboard (Streamlit) jisme reports history dikhe
- [ ] Multi-agent setup: ek agent sirf anomaly-detection kare, doosra summary banaye
