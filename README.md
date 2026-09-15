# 🎬 Smart YT Playlist Studio

Vishayam (topic) കൊടുത്താൽ, views/rating അടിസ്ഥാനമാക്കിയോ Gemini AI സ്മാർട്ട് സെലക്ഷൻ ഉപയോഗിച്ചോ മികച്ച YouTube ക്ലാസുകൾ ഫിൽട്ടർ ചെയ്ത് ഒരൊറ്റ playlist ആക്കുന്ന Streamlit app.

## 📁 Files

```
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── .gitignore                      # secrets.toml GitHub-ilekk povathirikkan
└── .streamlit/
    └── secrets.toml.example        # API key setup-inte example (real key idaruth)
```

## 🚀 GitHub-il Publish Cheyyunna Vidham

```bash
# 1. Local folder-il ithu ellam vekkuka: app.py, requirements.txt, .gitignore, .streamlit/secrets.toml.example
git init
git add .
git commit -m "Smart YT Playlist Studio"

# 2. GitHub-il puthiya repo undakkuka (github.com/new), enn oru name kodukkuka
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

⚠️ **`.streamlit/secrets.toml`** (yatharthamaya API key ulla file) **ORU KAALATHUM commit cheyyaruthu.** `.gitignore` athu automatic ayi ozhivakkum. `secrets.toml.example` mathram GitHub-il pokum — athil real key illa.

## ☁️ Streamlit Cloud-il Deploy Cheyyunna Vidham (Free Hosting)

1. **share.streamlit.io** il pokuka, GitHub account vech sign in cheyyuka
2. **"New app"** click cheyyuka
3. Nammal push cheytha repo select cheyyuka, `app.py` main file ayi kodukkuka
4. Deploy cheyyunnathinu munpu (allenkil deploy cheythu kazhinjum) — **"Advanced settings" → "Secrets"** il ithu paste cheyyuka:

   ```toml
   GEMINI_API_KEY = "your-actual-gemini-api-key-here"
   ```

5. **"Deploy"** click cheyyuka — few minutes-il app live aavum, oru public link kittum

Ithu cheythal kazhinjal, app open cheyyumbo Gemini AI toggle automatic ayi "API Key Secrets-il ninnu load cheythu" ennu kaanikkum — user vere onnum type cheyyendathilla.

### Secrets update/change cheyyenamenkil
App dashboard → **⋮ (three dots)** → **Settings** → **Secrets** → edit cheythu **Save**. App restart aavum automatic ayi.

## 🔑 Gemini API Key Free-aayi Engane Kittum

1. **aistudio.google.com/apikey** il pokuka
2. Google account vech sign in cheyyuka
3. **"Create API Key"** click cheyyuka — instant aayi free key kittum

## 💻 Local-il Test Cheyyan

```bash
pip install -r requirements.txt

# Local test cheyyan (optional) - secrets.toml.example copy cheythu real key idaam:
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# .streamlit/secrets.toml thurannu real API key idaam

streamlit run app.py
```

secrets.toml illathe direct sidebar-il API key type cheythum test cheyyaam.
