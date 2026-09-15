import streamlit as st
import urllib.parse
import json
from yt_dlp import YoutubeDL
from deep_translator import GoogleTranslator

st.set_page_config(
    page_title="Smart YT Playlist Studio",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🎬 യൂട്യൂബ് പ്ലേലിസ്റ്റ് ക്രിയേറ്റർ")
st.caption("പഠന ക്ലാസുകളും പ്രഭാഷണങ്ങളും മികച്ച വീഡിയോകൾ ഫിൽട്ടർ ചെയ്ത് ഒരൊറ്റ പ്ലേലിസ്റ്റാക്കാം — Gemini AI സഹായത്തോടെ.")


def get_secret_api_key():
    """Streamlit Cloud-ൽ Settings → Secrets വഴി വച്ച GEMINI_API_KEY ഉണ്ടെങ്കിൽ അതെടുക്കും.
    ഇല്ലെങ്കിൽ (local dev) വെറും ശൂന്യമായ string തിരികെ കൊടുക്കും — user-inu sidebar-ൽ നേരിട്ട് നൽകാം."""
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


_secret_key = get_secret_api_key()

# ---------------- Sidebar: Gemini AI Smart Selection ----------------
with st.sidebar:
    st.header("✨ Gemini AI Smart Selection")
    st.caption("Views/Rating മാത്രമല്ല, ഉള്ളടക്ക ഗുണനിലവാരം കൂടി നോക്കി Gemini 2.5 Flash മികച്ച വീഡിയോകൾ തിരഞ്ഞെടുക്കും.")
    use_gemini = st.toggle("Gemini AI സ്മാർട്ട് സെലക്ഷൻ ഓൺ ചെയ്യുക", value=bool(_secret_key))
    gemini_api_key = _secret_key
    gemini_model = "gemini-2.5-flash"
    if use_gemini:
        if _secret_key:
            st.success("🔒 API Key Streamlit Secrets-ൽ നിന്ന് ലോഡ് ചെയ്തു.")
        else:
            gemini_api_key = st.text_input(
                "Gemini API Key",
                type="password",
                help="aistudio.google.com/apikey ൽ നിന്നും സൗജന്യമായി API key എടുക്കാം. Streamlit Cloud-ൽ deploy ചെയ്യുമ്പോൾ ഇത് Secrets-ൽ വച്ചാൽ ഇനി ഇവിടെ കൊടുക്കേണ്ടി വരില്ല."
            )
        gemini_model = st.selectbox(
            "Gemini Model:",
            options=["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"],
            index=0
        )
        st.caption("⚠️ API key code-ലോ GitHub-ലോ സേവ് ചെയ്യപ്പെടില്ല — Secrets/session-ൽ മാത്രം.")

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
        options=[10, 15, 20, 25, 30],
        index=0
    )

col3, col4 = st.columns(2)

with col3:
    sort_by_views = st.checkbox(
        "കൂടുതൽ Views/Rating ഉള്ള വീഡിയോകൾ മുൻഗണന നൽകുക",
        value=True
    )

with col4:
    translate_option = st.checkbox(
        "തലക്കെട്ടുകൾ മലയാളത്തിലേക്ക് വിവർത്തനം ചെയ്യുക",
        value=(lang_choice == "English")
    )

create_btn = st.button("പ്ലേലിസ്റ്റ് നിർമ്മിക്കുക 🚀", type="primary", use_container_width=True)


def fetch_candidate_videos(search_text, selected_lang, max_vids):
    """ആവശ്യമുള്ളതിനേക്കാൾ കൂടുതൽ candidates എടുക്കുന്നു, എന്നിട്ട് അതിൽ നിന്ന് മികച്ചത് select ചെയ്യും."""
    query = search_text.strip()
    if "Malayalam" in selected_lang:
        query += " in Malayalam full lecture class"
    elif selected_lang == "English":
        query += " best lecture class in English"
    else:
        query += " full lecture course"

    # Views/rating വച്ച് ranking വേണമെങ്കിൽ, candidates കൂടുതൽ വേണം (max 60 എണ്ണം വരെ)
    fetch_count = min(max_vids * 3, 60) if sort_by_views or use_gemini else max_vids

    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'playlistend': fetch_count,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{fetch_count}:{query}", download=False)
        return info.get('entries', []) if info else []


def rank_by_views(videos, max_vids):
    """view_count (ലഭ്യമെങ്കിൽ) വച്ച് sort ചെയ്ത് top N എടുക്കുന്നു."""
    def score(v):
        return v.get('view_count') or 0

    sorted_videos = sorted(videos, key=score, reverse=True)
    return sorted_videos[:max_vids]


def smart_select_with_gemini(videos, search_topic, max_vids, api_key, model):
    """Gemini AI ഉപയോഗിച്ച് ഏറ്റവും relevant & high-quality വീഡിയോകൾ തിരഞ്ഞെടുക്കുന്നു."""
    from google import genai

    client = genai.Client(api_key=api_key)

    candidate_list = []
    for v in videos:
        candidate_list.append({
            "id": v.get("id"),
            "title": v.get("title", ""),
            "channel": v.get("uploader") or v.get("channel") or "Unknown",
            "views": v.get("view_count") or 0,
            "duration_sec": v.get("duration") or 0,
        })

    prompt = f"""You are curating a YouTube learning playlist for the topic: "{search_topic}".

Below is a JSON list of candidate videos (id, title, channel, views, duration in seconds).
Select the {max_vids} BEST videos for someone seriously trying to learn this topic — prioritize:
1. Relevance of the title to the topic
2. Higher view counts (signals popularity/trust) when relevance is similar
3. Avoid obvious duplicates, unrelated clips, shorts/clickbait, or very low-effort content
4. Prefer a mix that covers the topic well (not 10 videos on the exact same sub-point)

Candidates:
{json.dumps(candidate_list, ensure_ascii=False)}

Respond with ONLY a JSON array of the selected video "id" strings, ordered from best to good, with no other text, no markdown fences, no explanation. Return exactly {max_vids} ids if possible (fewer only if there truly aren't enough relevant videos)."""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    raw_text = (response.text or "").strip()
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    selected_ids = json.loads(raw_text)

    videos_by_id = {v.get("id"): v for v in videos}
    ordered = [videos_by_id[vid] for vid in selected_ids if vid in videos_by_id]
    return ordered[:max_vids] if ordered else rank_by_views(videos, max_vids)


def translate_to_malayalam(text):
    try:
        return GoogleTranslator(source='auto', target='ml').translate(text)
    except Exception:
        return text


if create_btn and topic.strip():
    spinner_msg = f"'{topic}' സംബന്ധിച്ച മികച്ച {limit} ക്ലാസുകൾ കണ്ടെത്തുന്നു..."
    with st.spinner(spinner_msg):
        try:
            candidates = fetch_candidate_videos(topic, lang_choice, limit)

            if not candidates:
                st.warning("വീഡിയോകൾ ഒന്നും കണ്ടെത്താനായില്ല.")
            else:
                videos = candidates
                used_gemini = False

                if use_gemini and gemini_api_key.strip():
                    try:
                        with st.spinner("✨ Gemini AI മികച്ച വീഡിയോകൾ വിശകലനം ചെയ്യുന്നു..."):
                            videos = smart_select_with_gemini(candidates, topic, limit, gemini_api_key.strip(), gemini_model)
                            used_gemini = True
                    except Exception as ge:
                        st.warning(f"Gemini AI selection പരാജയപ്പെട്ടു ({str(ge)}), views അടിസ്ഥാനമാക്കി തിരഞ്ഞെടുക്കുന്നു.")
                        videos = rank_by_views(candidates, limit)
                elif sort_by_views:
                    videos = rank_by_views(candidates, limit)
                else:
                    videos = candidates[:limit]

                video_ids = [v['id'] for v in videos if v.get('id')]
                playlist_url = f"https://www.youtube.com/watch_videos?video_ids={','.join(video_ids)}"

                badge = "✨ Gemini AI സ്മാർട്ട് സെലക്ഷൻ" if used_gemini else ("📈 Views അടിസ്ഥാനമാക്കിയ സെലക്ഷൻ" if sort_by_views else "🔎 സാധാരണ സെർച്ച്")
                st.success(f"✅ {len(video_ids)} മികച്ച ക്ലാസുകൾ അടങ്ങിയ പ്ലേലിസ്റ്റ് തയ്യാർ! ({badge})")

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
                    views = item.get('view_count')
                    link = f"https://www.youtube.com/watch?v={item.get('id')}"

                    display_title = original_title
                    if translate_option:
                        translated_title = translate_to_malayalam(original_title)
                        display_title = f"{translated_title} *(Original: {original_title})*"

                    with st.container(border=True):
                        st.markdown(f"**{idx}. [{display_title}]({link})**")
                        views_text = f" • 👁️ {views:,} views" if views else ""
                        st.caption(f"ചാനൽ: {channel}{views_text}")

        except Exception as e:
            st.error(f"പ്രശ്നം സംഭവിച്ചു: {str(e)}")

elif create_btn:
    st.warning("ദയവായി ഒരു വിഷയം നൽകുക.")
