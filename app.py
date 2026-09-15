import streamlit as st
import urllib.parse
from yt_dlp import YoutubeDL
from deep_translator import GoogleTranslator

st.set_page_config(
    page_title="Smart YT Playlist Studio",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# മൊബൈൽ ബട്ടൺ സ്റ്റൈലുകൾ
st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
    .custom-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 12px;
        margin: 6px 0;
        border-radius: 8px;
        font-weight: bold;
        text-decoration: none;
        font-size: 1rem;
        text-align: center;
    }
    .btn-yt {
        background-color: #ff0000 !important;
        color: white !important;
    }
    .btn-wa {
        background-color: #25D366 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 യൂട്യൂബ് പ്ലേലിസ്റ്റ് ക്രിയേറ്റർ")
st.caption("ഏത് വിഷയത്തിന്റെയും ഏറ്റവും മികച്ച വീഡിയോകൾ തിരഞ്ഞെടുത്ത് പ്ലേലിസ്റ്റാക്കാം.")

topic = st.text_input(
    "പഠിക്കേണ്ട വിഷയം (Topic):",
    placeholder="ഉദാ: python tutorial, intraday trading, electronics..."
)

col1, col2 = st.columns(2)

with col1:
    lang_choice = st.selectbox(
        "വീഡിയോ ഭാഷ:",
        options=["Malayalam (മലയാളം)", "English", "Any (ഏതും ആകാം)"]
    )

with col2:
    # പരമാവധി 50 വീഡിയോകൾ വരെ തിരഞ്ഞെടുക്കാം
    limit = st.select_slider(
        "വീഡിയോകളുടെ എണ്ണം (Max Videos):",
        options=[5, 10, 20, 30, 40, 50],
        value=20
    )

translate_option = st.checkbox(
    "തലക്കെട്ടുകൾ മലയാളത്തിലേക്ക് വിവർത്തനം ചെയ്യുക",
    value=False
)

create_btn = st.button("പ്ലേലിസ്റ്റ് നിർമ്മിക്കുക 🚀", type="primary", use_container_width=True)

def fetch_best_videos(search_text, selected_lang, max_vids):
    """മികച്ച വീഡിയോകൾ ഫിൽട്ടർ ചെയ്ത് കണ്ടെത്തുന്നു"""
    query = search_text.strip()
    if "Malayalam" in selected_lang:
        query += " in Malayalam tutorial"
    elif selected_lang == "English":
        query += " best tutorial in English"

    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        # മികച്ച വീഡിയോകൾക്കായി കൃത്യമായ ക്വറി നൽകുന്നു
        info = ydl.extract_info(f"ytsearch{max_vids}:{query}", download=False)
        return info.get('entries', []) if info else []

def translate_to_malayalam(text):
    try:
        return GoogleTranslator(source='auto', target='ml').translate(text)
    except Exception:
        return text

if create_btn and topic.strip():
    with st.spinner(f"ഏറ്റവും മികച്ച {limit} വീഡിയോകൾ കണ്ടെത്തുന്നു..."):
        try:
            videos = fetch_best_videos(topic, lang_choice, limit)

            if not videos:
                st.warning("വീഡിയോകൾ ഒന്നും കണ്ടെത്താനായില്ല. മറ്റൊരു വാക്ക് നൽകി നോക്കുക.")
            else:
                video_ids = [v['id'] for v in videos if v.get('id')]
                
                # YouTube പ്ലേലിസ്റ്റ് ലിങ്ക്
                playlist_url = f"https://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"

                st.success(f"✅ {len(video_ids)} മികച്ച വീഡിയോകൾ ചേർത്ത പ്ലേലിസ്റ്റ് തയ്യാറായി!")

                st.markdown("---")
                st.subheader("🌐 പ്ലേലിസ്റ്റ് തുറക്കാനും ഷെയർ ചെയ്യാനും:")

                # 1. ഇഷ്ടമുള്ള ബ്രൗസറിൽ തുറക്കാൻ (തനിയെ ആപ്പിലേക്ക് പോകാതെ ബ്രൗസർ ചോദിക്കാൻ target='_blank')
                yt_button_html = f"""
                <a href="{playlist_url}" target="_blank" rel="noopener noreferrer" class="custom-btn btn-yt">
                    ▶️ ബ്രൗസറിൽ പ്ലേ ചെയ്യുക (Open in Browser)
                </a>
                """
                st.markdown(yt_button_html, unsafe_allow_html=True)
                st.caption("💡 *ഫോണിൽ ക്ലിക്ക് ചെയ്യുമ്പോൾ Chrome, Brave, Firefox തുടങ്ങിയ ഇഷ്ടമുള്ള ബ്രൗസർ തിരഞ്ഞെടുക്കാം.*")

                # 2. വാട്സാപ്പിലേക്ക് നേരിട്ട് അയക്കാനുള്ള ബട്ടൺ
                share_message = f"📌 *{topic.strip()}* സംബന്ധിച്ച മികച്ച {len(video_ids)} വീഡിയോകളുടെ പ്ലേലിസ്റ്റ് ഇതാ:\n\n🔗 {playlist_url}"
                wa_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_message)}"

                wa_button_html = f"""
                <a href="{wa_url}" target="_blank" class="custom-btn btn-wa">
                    💬 WhatsApp വഴി സുഹൃത്തുക്കൾക്ക് അയക്കുക
                </a>
                """
                st.markdown(wa_button_html, unsafe_allow_html=True)

                # 3. നേരിട്ട് കോപ്പി ചെയ്യാനുള്ള ലിങ്ക് ബോക്സ്
                st.text_input("📋 നേരിട്ട് കോപ്പി ചെയ്യാനുള്ള പ്ലേലിസ്റ്റ് ലിങ്ക്:", value=playlist_url)

                st.markdown("---")
                st.write(f"**തിരഞ്ഞെടുത്ത മികച്ച {len(video_ids)} വീഡിയോകൾ:**")

                for idx, item in enumerate(videos, start=1):
                    original_title = item.get('title', 'No title')
                    channel = item.get('uploader') or item.get('channel') or 'YouTube'
                    link = f"https://www.youtube.com/watch?v={item.get('id')}"

                    display_title = original_title
                    if translate_option:
                        translated_title = translate_to_malayalam(original_title)
                        display_title = f"{translated_title} *(Original: {original_title})*"

                    with st.container(border=True):
                        st.markdown(f"**{idx}. [{display_title}]({link})**")
                        st.caption(f"ചാനൽ: {channel}")

        except Exception as e:
            st.error(f"പ്രശ്നം സംഭവിച്ചു: {str(e)}")

elif create_btn:
    st.warning("ദയവായി ഒരു വിഷയം ടൈപ്പ് ചെയ്യുക.")