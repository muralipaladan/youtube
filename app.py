import streamlit as st
import urllib.parse
from yt_dlp import YoutubeDL
from deep_translator import GoogleTranslator

# മൊബൈൽ ഫ്രണ്ട്‌ലി പേജ് കോൺഫിഗറേഷൻ
st.set_page_config(
    page_title="Smart YT Playlist Share",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎬 യൂട്യൂബ് പ്ലേലിസ്റ്റ് ഷെയറർ")
st.caption("ഏത് വിഷയത്തിന്റെയും മികച്ച വീഡിയോകൾ കണ്ടെത്തി ഒറ്റ ലിങ്കായി ഷെയർ ചെയ്യാം.")

# ഇൻപുട്ടുകൾ
topic = st.text_input(
    "പഠിക്കേണ്ട വിഷയം (Topic):",
    placeholder="ഉദാ: Mutual Fund basics, Web development..."
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
    value=(lang_choice == "English")
)

create_btn = st.button("പ്ലേലിസ്റ്റ് നിർമ്മിക്കുക 🚀", type="primary", use_container_width=True)

def fetch_videos(search_text, selected_lang, max_vids):
    final_query = search_text.strip()
    if "Malayalam" in selected_lang:
        final_query += " in Malayalam"
    elif selected_lang == "English":
        final_query += " in English"

    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{max_vids}:{final_query}", download=False)
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

                st.success(f"✅ {len(video_ids)} മികച്ച വീഡിയോകൾ അടങ്ങിയ പ്ലേലിസ്റ്റ് തയ്യാർ!")

                # നേരിട്ട് തുറക്കാനുള്ള ബട്ടൺ
                st.link_button(
                    "▶️ പ്ലേലിസ്റ്റ് യൂട്യൂബിൽ കാണുക",
                    url=playlist_url,
                    type="primary",
                    use_container_width=True
                )

                # ഷെയർ ചെയ്യാനുള്ള സന്ദേശം തയ്യാറാക്കുന്നു
                share_message = f"📌 *{topic.strip()}* സംബന്ധിച്ച മികച്ച യൂട്യൂബ് വീഡിയോകളുടെ പ്ലേലിസ്റ്റ് ഇതാ:\n\n🔗 {playlist_url}"
                encoded_msg = urllib.parse.quote(share_message)

                whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_msg}"
                telegram_url = f"https://t.me/share/url?url={urllib.parse.quote(playlist_url)}&text={urllib.parse.quote(f'📌 {topic.strip()} Playlist')}"

                # ഷെയറിംഗ് ബട്ടണുകൾ
                st.markdown("### 📤 ഒറ്റ ക്ലിക്കിൽ ഷെയർ ചെയ്യാം:")
                col_wa, col_tg = st.columns(2)
                with col_wa:
                    st.link_button("💬 WhatsApp വഴി അയക്കുക", url=whatsapp_url, use_container_width=True)
                with col_tg:
                    st.link_button("✈️ Telegram വഴി അയക്കുക", url=telegram_url, use_container_width=True)

                # ലിങ്ക് കോപ്പി ചെയ്യാൻ പാകത്തിൽ ഒരു ബോക്സിൽ കാണിക്കുന്നു
                st.text_input("📋 നേരിട്ട് കോപ്പി ചെയ്യാനുള്ള ലിങ്ക്:", value=playlist_url)

                st.markdown("---")
                st.write("**ലിസ്റ്റിലെ വീഡിയോകൾ:**")

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
