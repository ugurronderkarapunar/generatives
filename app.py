import streamlit as st
import anthropic
import json
import re
import os

# API key: Streamlit Cloud secrets veya env variable
api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))

st.set_page_config(
    page_title="🎬 Video Prompt Generator",
    page_icon="🎬",
    layout="centered"
)

# --- CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    color: #e0e0f0;
}

.main-title {
    text-align: center;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #ff6b6b, #f9ca24, #6bcb77, #4d96ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.subtitle {
    text-align: center;
    color: #888;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}

.scene-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}

.scene-header {
    font-size: 0.8rem;
    color: #4d96ff;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}

.scene-prompt {
    font-size: 0.9rem;
    color: #c8c8e8;
    margin-bottom: 0.5rem;
}

.overlay-badge {
    display: inline-block;
    background: linear-gradient(90deg, #ff6b6b44, #f9ca2444);
    border: 1px solid #f9ca2488;
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.82rem;
    color: #f9ca24;
    font-weight: 600;
}

.meta-pill {
    display: inline-block;
    background: rgba(77,150,255,0.15);
    border: 1px solid rgba(77,150,255,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    color: #4d96ff;
    margin-right: 0.4rem;
}

.cta-box {
    background: linear-gradient(135deg, rgba(255,107,107,0.15), rgba(249,202,36,0.15));
    border: 1px solid rgba(249,202,36,0.3);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f9ca24;
    margin-top: 0.8rem;
}

.music-box {
    background: rgba(107,203,119,0.1);
    border: 1px solid rgba(107,203,119,0.3);
    border-radius: 12px;
    padding: 0.8rem 1.2rem;
    color: #6bcb77;
    font-size: 0.9rem;
    margin-top: 0.8rem;
}

.stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    color: #e0e0f0 !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

.stButton > button {
    background: linear-gradient(90deg, #ff6b6b, #f9ca24) !important;
    color: #0f0f1a !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

div[data-testid="stCodeBlock"] {
    background: rgba(0,0,0,0.4) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="main-title">🎬 Video Prompt Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ürün fikrini yaz → Luma / Runway / Pika için sahne komutları üretelim</div>', unsafe_allow_html=True)

# --- Input ---
idea = st.text_area(
    "💡 Ürün / Reklam Fikri",
    placeholder="Örnek: Spor salonunda kullanılan protein bar, 18-25 yaş Gen Z hedef kitle...",
    height=120
)

col1, col2, col3 = st.columns(3)
with col1:
    platform = st.selectbox("📱 Platform", ["TikTok", "Reels", "YouTube Shorts"])
with col2:
    vibe = st.selectbox("🎭 Vibe", ["Enerjik", "Lüks", "Hızlı", "Sakin", "Duygusal"])
with col3:
    scene_count = st.selectbox("🎞️ Sahne Sayısı", [3, 4, 5, 6])

generate = st.button("⚡ Sahne Komutları Üret")

# --- Generation ---
if generate:
    if not idea.strip():
        st.warning("Lütfen bir ürün veya reklam fikri gir.")
    else:
        with st.spinner("Sahneler üretiliyor..."):
            if not api_key:
                st.error("⚠️ ANTHROPIC_API_KEY bulunamadı. Streamlit Secrets veya environment variable olarak tanımla.")
                st.stop()
            client = anthropic.Anthropic(api_key=api_key)

            system_prompt = """Sen uzman bir Video Prodüksiyon Yapay Zekasısın. Kullanıcının verdiği ürün/konu fikrini, video üretim modelleri (Luma/Runway/Pika) için teknik sahne komutlarına dönüştürürsün.

OUTPUT FORMAT (Sadece geçerli JSON dön, başka hiçbir şey yazma):
{
  "video_metadata": {
    "vibe": "string",
    "target_platform": "string"
  },
  "scenes": [
    {
      "scene_number": 1,
      "visual_prompt": "Technical English cinematic prompt for video AI model",
      "duration": "3s",
      "overlay_text": "Vurucu Türkçe metin"
    }
  ],
  "music_instruction": "Müzik tarzı açıklaması",
  "cta": "Harekete geçirici Türkçe mesaj"
}

RULES:
1. visual_prompt MUTLAKA İngilizce, sinematik, teknik olmalı (camera movement, lighting, lens type, mood).
2. overlay_text MUTLAKA Türkçe ve dikkat çekici olmalı.
3. Sadece JSON dön. Hiçbir açıklama, markdown, kod bloğu ekleme."""

            user_msg = f"""Ürün/Fikir: {idea}
Platform: {platform}
Vibe: {vibe}
Sahne sayısı: {scene_count}

Bu bilgilere göre {scene_count} sahneli video prompt JSON üret."""

            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1500,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_msg}]
                )

                raw = response.content[0].text.strip()
                # Strip markdown fences if present
                raw = re.sub(r"^```[a-z]*\n?", "", raw)
                raw = re.sub(r"\n?```$", "", raw)

                data = json.loads(raw)

                # --- Display Results ---
                st.markdown("---")
                st.markdown("### 🎬 Üretilen Sahne Planı")

                # Metadata pills
                meta = data.get("video_metadata", {})
                pills_html = ""
                if meta.get("vibe"):
                    pills_html += f'<span class="meta-pill">🎭 {meta["vibe"]}</span>'
                if meta.get("target_platform"):
                    pills_html += f'<span class="meta-pill">📱 {meta["target_platform"]}</span>'
                if pills_html:
                    st.markdown(pills_html, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                # Scenes
                for scene in data.get("scenes", []):
                    num = scene.get("scene_number", "?")
                    duration = scene.get("duration", "")
                    prompt = scene.get("visual_prompt", "")
                    overlay = scene.get("overlay_text", "")

                    st.markdown(f"""
                    <div class="scene-card">
                        <div class="scene-header">🎥 Sahne {num} &nbsp;·&nbsp; {duration}</div>
                        <div class="scene-prompt">{prompt}</div>
                        <span class="overlay-badge">💬 {overlay}</span>
                    </div>
                    """, unsafe_allow_html=True)

                # Music
                music = data.get("music_instruction", "")
                if music:
                    st.markdown(f'<div class="music-box">🎵 <strong>Müzik:</strong> {music}</div>', unsafe_allow_html=True)

                # CTA
                cta = data.get("cta", "")
                if cta:
                    st.markdown(f'<div class="cta-box">🚀 {cta}</div>', unsafe_allow_html=True)

                # Raw JSON toggle
                with st.expander("📋 Ham JSON (kopyala / kaydet)"):
                    st.code(json.dumps(data, ensure_ascii=False, indent=2), language="json")

            except json.JSONDecodeError:
                st.error("JSON parse hatası. Ham yanıt:")
                st.code(raw)
            except Exception as e:
                st.error(f"Hata: {e}")

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;color:#444;font-size:0.75rem;">Powered by Claude · Luma / Runway / Pika uyumlu promptlar</p>',
    unsafe_allow_html=True
)
