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

st.title("🎬 യൂട്യൂബ് പ്ലേലിസ്റ്റ് ക്രിയേറ്റർ")
st.caption("പഠന ക്ലാസുകളും പ്രഭാഷണങ്ങളും മികച്ച വീഡിയോകൾ ഫിൽട്ടർ ചെയ്ത് ഒരൊറ്റ പ്ലേലിസ്റ്റാക്കാം.")

# Nano Technology ഡിഫോൾട്ട് ആയി ചേർത്ത ഇൻപുട്ട്
topic = st.text_input(
    "പഠിക്കേണ്ട വിഷയം (Topic):",
    value="Nano Technology"
)

col1, col2 = st.columns(2)

with col1:
    lang_choice = st.selectbox(
        "വീഡിയോ ഭാഷ:",
        options=["Malayalam (മലയാളം)", "English", "Any (ഏതും ആകാം)"],
        index=1
    )

with col2:
    limit = st.selectbox(
        "വീഡിയോകളുടെ എണ്ണം:",
        options=[5, 10, 15, 20, 30],
        index=1
    )

translate_option = st.checkbox(
    "തലക്കെട്ടുകൾ മലയാളത്തിലേക്ക് വിവർത്തനം ചെയ്യുക",
    value=(lang_choice == "English")
)

create_btn = st.button("പ്ലേലിസ്റ്റ് നിർമ്മിക്കുക 🚀", type="primary", use_container_width=True)

def fetch_best_videos(search_text, selected_lang, max_vids):
    query = search_text.strip()
    if "Malayalam" in selected_lang:
        query += " in Malayalam full lecture class"
    elif selected_lang == "English":
        query += " best lecture class in English"
    else:
        query += " full lecture course"

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
    with st.spinner(f"'{topic}' സംബന്ധിച്ച മികച്ച {limit} ക്ലാസുകൾ കണ്ടെത്തുന്നു..."):
        try:
            videos = fetch_best_videos(topic, lang_choice, limit)

            if not videos:
                st.warning("വീഡിയോകൾ ഒന്നും കണ്ടെത്താനായില്ല.")
            else:
                video_ids = [v['id'] for v in videos if v.get('id')]
                playlist_url = f"https://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"

                st.success(f"✅ {len(video_ids)} മികച്ച ക്ലാസുകൾ അടങ്ങിയ പ്ലേലിസ്റ്റ് തയ്യാർ!")

                st.markdown("---")
                st.subheader("🌐 പ്ലേലിസ്റ്റ് തുറക്കാനും ഷെയർ ചെയ്യാനും:")

                # 1. ബ്രൗസറിൽ തുറക്കാനുള്ള ബട്ടൺ
                st.link_button(
                    "▶️ ബ്രൗസറിൽ പ്ലേ ചെയ്യുക (Open Playlist)",
                    url=playlist_url,
                    type="primary",
                    use_container_width=True
                )

                # 2. WhatsApp വഴി അയക്കാനുള്ള ബട്ടൺ
                share_message = f"📌 *{topic.strip()}* പഠന ക്ലാസുകളുടെ മികച്ച {len(video_ids)} വീഡിയോ പ്ലേലിസ്റ്റ് ഇതാ:\n\n🔗 {playlist_url}"
                wa_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_message)}"

                st.link_button(
                    "💬 WhatsApp വഴി അയക്കുക (Share to WhatsApp)",
                    url=wa_url,
                    use_container_width=True
                )

                # 3. കോപ്പി ചെയ്യാനുള്ള ബോക്സ്
                st.text_input("📋 നേരിട്ട് കോപ്പി ചെയ്യാനുള്ള ലിങ്ക്:", value=playlist_url)

                st.markdown("---")
                st.write(f"**തിരഞ്ഞെടുത്ത മികച്ച {len(video_ids)} ക്ലാസുകൾ:**")

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
    st.warning("ദയവായി ഒരു വിഷയം നൽകുക.")
