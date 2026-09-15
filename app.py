import streamlit as st
from yt_dlp import YoutubeDL
from deep_translator import GoogleTranslator

# മൊബൈൽ ബ്രൗസറുകൾക്കായി ഒപ്റ്റിമൈസ് ചെയ്ത പേജ്
st.set_page_config(
    page_title="Smart YT Playlist Maker",
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

st.title("🎬 യൂട്യൂബ് പ്ലേലിസ്റ്റ് ക്രിയേറ്റർ")
st.caption("വിഷയം നൽകുക; മലയാളത്തിലോ ഇംഗ്ലീഷിലോ ഉള്ള മികച്ച പ്ലേലിസ്റ്റ് സ്വന്തമാക്കുക.")

# ഇൻപുട്ട് ഘടകങ്ങൾ
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

# വിവർത്തന ഓപ്ഷൻ
translate_option = st.checkbox(
    "തലക്കെട്ടുകൾ മലയാളത്തിലേക്ക് വിവർത്തനം ചെയ്യുക (Translate titles to Malayalam)",
    value=(lang_choice == "English")
)

create_btn = st.button("പ്ലേലിസ്റ്റ് നിർമ്മിക്കുക 🚀", type="primary", use_container_width=True)

def fetch_videos(search_text, selected_lang, max_vids):
    """തിരഞ്ഞെടുത്ത ഭാഷയ്ക്കനുസരിച്ച് യൂട്യൂബ് സെർച്ച് ചെയ്യുന്നു"""
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
    """തലക്കെട്ട് മലയാളത്തിലേക്ക് വിവർത്തനം ചെയ്യുന്നു"""
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

                st.success(f"{len(video_ids)} വീഡിയോകൾ റെഡിയാണ്!")

                # നേരിട്ട് യൂട്യൂബ് ആപ്പിലോ ബ്രൗസറിലോ തുറക്കാനുള്ള ബട്ടൺ
                st.link_button(
                    "യൂട്യൂബിൽ പ്ലേ ചെയ്യുക ▶️ (Open Playlist)",
                    url=playlist_url,
                    type="primary",
                    use_container_width=True
                )

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
