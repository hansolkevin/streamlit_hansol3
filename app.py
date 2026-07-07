import streamlit as st
from openai import OpenAI
import json
import urllib.parse

st.set_page_config(
    page_title="🎵 노래 추천 서비스",
    page_icon="🎵",
    layout="centered"
)

st.title("🎵 AI 노래 추천 서비스")
st.markdown("몇 가지 질문에 답하면 딱 맞는 노래를 추천해 드려요!")

# OpenAI API Key 입력
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="OpenAI API 키를 입력하세요. 키는 저장되지 않습니다."
    )
    if api_key:
        st.success("API 키가 입력되었습니다.")
    else:
        st.warning("API 키를 입력해야 노래를 추천받을 수 있습니다.")

st.divider()

# 설문 조사
st.subheader("📋 설문 조사")

col1, col2 = st.columns(2)

with col1:
    mood = st.selectbox(
        "1. 지금 기분이 어떤가요?",
        ["선택해주세요", "😊 행복하고 신나는", "😢 슬프고 감성적인", "😤 화나고 에너지 넘치는",
         "😌 차분하고 평온한", "🤔 생각이 많은", "😴 졸리고 나른한"]
    )

    activity = st.selectbox(
        "2. 지금 무엇을 하고 있나요?",
        ["선택해주세요", "🏃 운동 중", "📚 공부/작업 중", "🚗 드라이브 중",
         "🛁 휴식 중", "🍽️ 식사 중", "😴 잠들기 전"]
    )

    genre = st.multiselect(
        "3. 선호하는 장르를 선택하세요 (복수 선택 가능)",
        ["K-Pop", "팝(Pop)", "R&B/Soul", "힙합(Hip-hop)", "발라드",
         "록(Rock)", "재즈(Jazz)", "인디/어쿠스틱", "클래식", "EDM/일렉트로닉"]
    )

with col2:
    era = st.selectbox(
        "4. 어떤 시대의 음악을 원하나요?",
        ["선택해주세요", "2020년대 최신곡", "2010년대", "2000년대", "1990년대", "1980년대 이전", "상관없음"]
    )

    language = st.selectbox(
        "5. 선호하는 언어는?",
        ["선택해주세요", "한국어", "영어", "일본어", "상관없음"]
    )

    tempo = st.select_slider(
        "6. 원하는 템포는?",
        options=["매우 느린", "느린", "보통", "빠른", "매우 빠른"],
        value="보통"
    )

st.divider()

additional = st.text_area(
    "7. 추가로 원하는 분위기나 특별한 요청이 있나요? (선택사항)",
    placeholder="예: 비 오는 날 듣기 좋은 노래, 실연 후 위로가 되는 노래, 드라이브할 때 창문 열고 듣기 좋은 노래...",
    height=80
)

count = st.slider("추천받을 노래 수", min_value=3, max_value=10, value=5)

st.divider()


def youtube_search_url(title, artist):
    query = urllib.parse.quote(f"{title} {artist}")
    return f"https://www.youtube.com/results?search_query={query}"


def build_prompt(mood, activity, genre, era, language, tempo, additional, count):
    genre_str = ", ".join(genre) if genre else "장르 무관"
    return f"""당신은 음악 전문가입니다. 사용자의 설문 응답을 바탕으로 노래를 추천해주세요.

사용자 정보:
- 현재 기분: {mood}
- 현재 활동: {activity}
- 선호 장르: {genre_str}
- 선호 시대: {era}
- 선호 언어: {language}
- 원하는 템포: {tempo}
- 추가 요청: {additional if additional else "없음"}

위 조건에 맞는 노래를 정확히 {count}곡 추천해주세요.

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요:

{{
  "songs": [
    {{
      "title": "곡명",
      "artist": "아티스트명",
      "genre": "장르",
      "mood": "한 줄 분위기 설명",
      "reason": "추천 이유 (2~3문장)"
    }}
  ],
  "summary": "전체 플레이리스트 분위기 한 문장 요약"
}}"""


def render_songs(data):
    st.success("추천 완료! 🎉")
    st.subheader("🎶 맞춤 플레이리스트")

    for i, song in enumerate(data["songs"], 1):
        yt_url = youtube_search_url(song["title"], song["artist"])
        with st.container():
            col_info, col_btn = st.columns([5, 1])
            with col_info:
                st.markdown(f"**{i}. {song['title']}** — {song['artist']}")
                st.caption(f"🎸 {song['genre']}  |  🌈 {song['mood']}")
                st.markdown(f"<small>{song['reason']}</small>", unsafe_allow_html=True)
            with col_btn:
                st.link_button("▶ YouTube", yt_url, use_container_width=True)
        st.divider()

    st.info(f"🎧 {data['summary']}")


if st.button("🎵 노래 추천받기", type="primary", use_container_width=True):
    if not api_key:
        st.error("사이드바에서 OpenAI API 키를 먼저 입력해주세요.")
    elif mood == "선택해주세요" or activity == "선택해주세요" or era == "선택해주세요" or language == "선택해주세요":
        st.warning("모든 필수 항목을 선택해주세요.")
    elif not genre:
        st.warning("선호하는 장르를 하나 이상 선택해주세요.")
    else:
        with st.spinner("AI가 딱 맞는 노래를 찾고 있어요... 🎶"):
            try:
                client = OpenAI(api_key=api_key)
                prompt = build_prompt(mood, activity, genre, era, language, tempo, additional, count)

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 음악 취향을 분석하여 개인 맞춤형 노래를 추천해주는 전문 DJ입니다. 반드시 JSON 형식으로만 응답합니다."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    response_format={"type": "json_object"}
                )

                raw = response.choices[0].message.content
                data = json.loads(raw)
                render_songs(data)

            except json.JSONDecodeError:
                st.error("응답 파싱에 실패했습니다. 다시 시도해주세요.")
            except Exception as e:
                error_msg = str(e)
                if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "invalid" in error_msg.lower():
                    st.error("API 키가 올바르지 않습니다. 다시 확인해주세요.")
                elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                    st.error("API 사용 한도를 초과했습니다. OpenAI 계정을 확인해주세요.")
                else:
                    st.error(f"오류가 발생했습니다: {error_msg}")

st.markdown("---")
st.caption("Powered by OpenAI GPT-4o-mini | 🎵 AI 노래 추천 서비스")
