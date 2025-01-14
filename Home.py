import streamlit as st
import pandas as pd

# ===== CSS 커스텀 =====
# 1) 검색 입력창과 버튼 높이 맞춤
# 2) 사이드바 버튼 폭/높이 고정
#    (예: width: 200px; height: 2rem; 원하는 값으로 조정)
custom_css = """
<style>
/* 1) 검색 영역: text_input과 button 높이 맞추기 */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
    display: flex;
    align-items: end;
}

/* 버튼 높이 맞추기 */
div.stButton > button {
    width: 100%;
}

div[data-testid="stMarkdownContainer"] {
    width: 100%;
}

div[data-testid="stMarkdownContainer"] > div {
    margin: 0 0 0 0;
}

/* 2) 사이드바 버튼 폭/높이 고정(예시) */
.sidebar-button button {
    width: 200px !important;       /* 원하는 폭 */
    height: 2rem !important;       /* 원하는 높이 */
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)


def load_data(csv_path="Lucy.csv"):
    df = pd.read_csv(csv_path)
    return df


def main():

    # 데이터 불러오기
    df = load_data()

    # DataFrame을 list of dict로 변환
    song_data = df.to_dict(orient="records")

    if "selected_song" not in st.session_state:
        st.session_state["selected_song"] = None
    if "search_result" not in st.session_state:
        st.session_state["search_result"] = []

    # ───────────────────────────────────────────────────
    # 1. 왼쪽 사이드바 - 곡 제목 목록
    #    클릭 시 해당 곡 정보가 메인에 표시되도록
    # ───────────────────────────────────────────────────
    st.sidebar.title("곡 목록")

    for idx, song in enumerate(song_data):
        # 곡 제목을 버튼으로 표시
        if st.sidebar.button(song["title"], key=f"sidebar_{idx}"):
            st.session_state["selected_song"] = song
            # 검색 결과는 초기화하거나 말거나 선택할 수 있음.
            st.session_state["search_result"] = []

    # ───────────────────────────────────────────────────
    # 2. 검색 입력 & 버튼을 한 줄에 배치 + 엔터 검색
    # ───────────────────────────────────────────────────
    # 방법 A) on_change 사용
    def do_search():
        query = st.session_state["search_query"]  # text_input에 설정한 key
        search_by = st.session_state["search_by"]
        # 필터링
        filtered = []
        for song in song_data:
            val = str(song[search_by]) if pd.notna(song[search_by]) else ""
            if query.lower() in val.lower():
                filtered.append(song)
        st.session_state["search_result"] = filtered
        st.session_state["selected_song"] = None

    # 검색 기준 options
    if "search_by" not in st.session_state:
        st.session_state["search_by"] = "title"

    # 첫 번째 컬럼: 검색어 입력 (on_change=do_search, key="search_query")
    st.selectbox(
        "검색 기준",
        ["title", "album", "lyric"],
        key="search_by",
        on_change=do_search,
    )

    col_search, col_btn = st.columns([9, 1])
    with col_search:
        st.text_input(
            "검색어",
            key="search_query",
            on_change=do_search,  # 엔터치면 검색
            placeholder="검색어를 입력 후 엔터",
        )
    with col_btn:
        # 검색 버튼
        if st.button("검색"):
            do_search()

    search_result = st.session_state["search_result"]
    if search_result:
        st.subheader(f"검색 결과: {len(search_result)}건")

        for idx, song in enumerate(search_result):
            # 목록을 div로 감싸서 100% 폭으로
            # 제목 클릭 시 해당 곡 선택
            # (버튼 대신 링크 느낌을 주려면 st.markdown + unsafe_allow_html 사용 가능)
            html_content = f"""
                <div class="song-item">
                    <strong>{song['title']}</strong>
                </div>
            """
            if st.button(f"{song['title']}", key=f"result_{idx}"):
                st.session_state["selected_song"] = song

    # ───────────────────────────────────────────────────
    # 선택된 곡 상세 정보 표시
    # ───────────────────────────────────────────────────
    selected = st.session_state["selected_song"]
    if selected is not None:
        st.write("---")
        st.subheader("곡 상세 정보")

        st.write(f"**제목**: {selected['title']}")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**앨범명**: {selected['album']}")

        with col2:
            st.write(f"**좋아요 수**: {selected['like']}")

        # 가사가 여러 줄일 경우를 가정하여 text_area 또는 st.write
        lyric_md = selected["lyric"].replace("\n", "<br>")
        st.markdown(lyric_md, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
