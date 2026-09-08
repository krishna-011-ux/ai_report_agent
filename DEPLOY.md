# Deploy Guide — Web App Jisse "Sab Log" Use Kar Sakein

Ye guide batata hai kaise apna AI Report Agent ko ek **public web link** bana
kar deploy karein — jise koi bhi browser se khol ke, bina Python/code jaane,
istemal kar sake.

---

## Option A: Streamlit Community Cloud (FREE, Sabse Aasan) — Recommended

Isse ek link milega jaisa: `https://your-app-name.streamlit.app`
Koi bhi is link ko khol ke file upload karke report bana sakta hai.

### Steps:

**1. GitHub par code push karo**
```bash
# Zip extract karne ke baad us folder mein:
git init
git add .
git commit -m "AI Report Agent - initial commit"
```
GitHub.com pe ek naya (public ya private) repository banao, phir:
```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-report-agent.git
git branch -M main
git push -u origin main
```

> ⚠️ **IMPORTANT**: `config/config.yaml` mein agar koi real password/API key
> daali hai to usko hatao pehle, ya `.gitignore` mein daal do. API keys
> Streamlit ke "Secrets" mein daalenge (neeche step 4), GitHub mein nahi.

**2. Streamlit Community Cloud pe account banao**
- Jao: https://streamlit.io/cloud
- "Sign up" karo apne GitHub account se (free hai)

**3. New app deploy karo**
- "New app" button click karo
- Apna GitHub repo select karo
- Main file path: `streamlit_app.py`
- "Deploy" click karo

**4. Secrets (API keys) add karo — SECURE tarika**
- App settings mein "Secrets" section mein jao
- Ye add karo:
```toml
ANTHROPIC_API_KEY = "your-actual-key-here"
```
- Ab code mein `os.environ.get("ANTHROPIC_API_KEY")` automatically ye utha lega

**5. Done!**
2-3 minute mein app live ho jayegi apne link ke saath, jo aap kisi ko bhi
bhej sakte ho — WhatsApp, email, kahi bhi. Wo bina kuch install kiye seedha
browser mein use kar sakega.

---

## Option B: Hugging Face Spaces (FREE, Alternative)

Agar Streamlit Cloud kaam na kare, ye bhi free hai:
1. https://huggingface.co/spaces pe jao, "Create new Space"
2. SDK: "Streamlit" select karo
3. Files upload karo (ya GitHub se link karo)
4. Settings mein "Repository secrets" mein API key daalo
5. Automatically deploy ho jayega, link mil jayega

---

## Option C: Apni Company/Team Ke Andar (Private Network)

Agar public internet pe nahi, sirf office/team ke andar chahiye:

```bash
# Kisi bhi office server/VM pe:
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```
Phir team `http://<server-ka-IP>:8501` se access kar sakti hai (same
network/VPN pe).

24/7 chalte rehne ke liye background process banao:
```bash
nohup streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
```

---

## Option D: Docker Container (Enterprise-Grade)

Agar AWS/GCP/Azure jaise cloud pe scalable deployment chahiye:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build aur run:
```bash
docker build -t ai-report-agent .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY="your-key" ai-report-agent
```
Isko phir AWS ECS, Google Cloud Run, ya Azure Container Apps pe deploy kar
sakte ho — auto-scaling ke saath.

---

## Kaunsa Option Chuno?

| Zaroorat | Best Option |
|---|---|
| Free, public link, jaldi | **A - Streamlit Cloud** |
| Free, alternative | **B - Hugging Face Spaces** |
| Sirf company/team ke andar | **C - Private server** |
| Bade scale pe, enterprise | **D - Docker + Cloud** |

**99% cases mein Option A (Streamlit Community Cloud) hi sabse sahi hai** —
free hai, public link deta hai, aur setup 10 minute mein ho jata hai.

---

## Security Checklist Before Public Deploy

- [ ] Config file mein koi hardcoded password/key nahi honi chahiye
- [ ] `.gitignore` mein `config/gcreds.json`, `*.db`, `outputs/*` add karo
- [ ] Streamlit Secrets mein hi API keys rakho, code mein nahi
- [ ] Agar sensitive company data hai, to Option A/B ki jagah Option C (private) use karo
- [ ] File upload size limit set karo (Streamlit default 200MB hai, config.toml se change ho sakta hai)
