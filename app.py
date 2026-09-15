import streamlit as st
import urllib.parse
from yt_dlp import YoutubeDL
from deep_translator import GoogleTranslator

# പേജ് ലേഔട്ട് കോൺഫിഗറേഷൻ
st.set_page_config(
    page_title="Smart YT Playlist Share",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🎬 യൂട്യൂബ് പ്ലേലിസ്റ്റ് ക്രിയേറ്റർ")
st.caption("വിഷയം നൽകുക; മികച്ച വീഡിയോകൾ കണ്ടെത്തി ഒറ്റ ലിങ്കായി ഷെയർ ചെയ്യാം.")

# ഇൻപുട്ട് ഭാഗം
topic = st.text_input(
    "പഠിക്കേണ്ട വിഷയം (Topic):",
    placeholder="ഉദാ: python, mutual funds, trading..."
)

col1, col2 = st.columns(2)

with col1:
    lang_choice = st.selectbox(
        "വീഡിയോ ഭാഷ:",
        options=["Malayalam (മലയാളം)", "English", "Any (ഏതും ആകാം)"]
    )

with col2:
    limit = st.selectbox(
        "വീഡിയോകളുടെ എണ്ണം:",
        options=[5, 10, 15, 20],
        index=1
    )

translate_option = st.checkbox(
    "തലക്കെട്ടുകൾ മലയാളത്തിലേക്ക് വിവർത്തനം ചെയ്യുക",
    value=False
)

create_btn = st.button("പ്ലേലിസ്റ്റ് നിർമ്മിക്കുക 🚀", type="primary", use_container_width=True)

def fetch_videos(search_text, selected_lang, max_vids):
    query = search_text.strip()
    if "Malayalam" in selected_lang:
        query += " in Malayalam"
    elif selected_lang == "English":
        query += " in English"

    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{max_vids}:{query}", download=False)
        return info.get('entries', []) if info else []

def translate_to_malayalam(text):
    try:
        return GoogleTranslator(source='auto', target='ml').translate(text)
    except Exception:
        return text

if create_btn and topic.strip():
    with st.spinner("മികച്ച വീഡിയോകൾ കണ്ടെത്തുന്നു..."):
        try:
            videos = fetch_videos(topic, lang_choice, limit)

            if not videos:
                st.warning("വീഡിയോകൾ ഒന്നും കണ്ടെത്താനായില്ല. മറ്റൊരു വാക്ക് നൽകി നോക്കുക.")
            else:
                video_ids = [v['id'] for v in videos if v.get('id')]
                playlist_url = f"https://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"

                st.success(f"✅ {len(video_ids)} വീഡിയോകൾ റെഡിയാണ്!")

                # 1. യൂട്യൂബിൽ നേരിട്ട് കാണാനുള്ള ബട്ടൺ
                st.link_button(
                    "▶️ യൂട്യൂബിൽ പ്ലേ ചെയ്യുക (Open Playlist)",
                    url=playlist_url,
                    type="primary",
                    use_container_width=True
                )

                # ഷെയറിംഗ് ലിങ്കുകൾ
                share_text = f"📌 *{topic.strip()}* സംബന്ധിച്ച മികച്ച യൂട്യൂബ് വീഡിയോകളുടെ പ്ലേലിസ്റ്റ് ഇതാ:\n\n🔗 {playlist_url}"
                wa_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_text)}"
                tg_url = f"https://t.me/share/url?url={urllib.parse.quote(playlist_url)}&text={urllib.parse.quote(f'📌 {topic.strip()} Playlist')}"

                st.markdown("---")
                st.subheader("📤 ലിങ്ക് ഷെയർ ചെയ്യാം")

                # 2. WhatsApp & Telegram ഇൻബിൽറ്റ് ബട്ടണുകൾ
                col_wa, col_tg = st.columns(2)
                with col_wa:
                    st.link_button("💬 WhatsApp വഴി അയക്കുക", url=wa_url, use_container_width=True)
                with col_tg:
                    st.link_button("✈️ Telegram വഴി അയക്കുക", url=tg_url, use_container_width=True)

                # 3. കോപ്പി ചെയ്യാനുള്ള ടെക്സ്റ്റ് ബോക്സ്
                st.text_input("📋 നേരിട്ട് കോപ്പി ചെയ്യാനുള്ള ലിങ്ക്:", value=playlist_url)

                st.markdown("---")
                st.write("**കണ്ടെത്തിയ വീഡിയോകൾ:**")

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
