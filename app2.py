import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

MEMBER_FILE = "members.csv"

# 체크 열 업데이트 함수
def mark_attendance(person_index, car_usage, start, end, car):
    df = pd.read_csv(MEMBER_FILE)
    kst_now = datetime.utcnow() + timedelta(hours=9)
    now = kst_now.strftime("%Y-%m-%d %H:%M")
    df.at[person_index, "체크"] = now
    df.at[person_index, "자차여부"] = car_usage
    df.at[person_index, "출발지"] = start
    df.at[person_index, "도착지"] = end
    df.at[person_index, "차량번호"] = car
    df.to_csv(MEMBER_FILE, index=False)
    return df.at[person_index, "조"]  # 조 정보 반환

# Streamlit 설정
st.set_page_config(page_title="2025 비상 Cell 리더 워크숍 체크인")
st.title("2025 비상 Cell 리더 워크숍 체크인")

members_df = pd.read_csv(MEMBER_FILE)

# 이동 관련 열이 없으면 생성
for col in ["체크", "자차여부", "출발지", "도착지", "차량번호"]:
    if col not in members_df.columns:
        members_df[col] = ""

# 탭 구성
tab1, tab2 = st.tabs(["✅ 출석 체크", "🔐 관리자 현황 보기"])

with tab1:
    st.markdown("---")
    # 이름 검색
    name_input = st.text_input("🔍 이름을 입력하세요:")
    filtered = members_df[members_df["사원이름"].str.contains(name_input)] if name_input else pd.DataFrame()

    selected_person = None
    selected_index = None
    if not filtered.empty:
        options = [
            f"{row['컴퍼니']} - {row['상위부서명']} - {row['부서명']} - {row['사원이름']}"
            for _, row in filtered.iterrows()
        ]
        selected_option = st.radio("본인을 선택하세요:", options)
        if selected_option:
            selected_index = options.index(selected_option)
            selected_person = filtered.iloc[selected_index]
            selected_global_index = filtered.index[selected_index]  # 실제 원본 df에서의 인덱스

    # 선택된 사람 있을 경우 추가 입력
    if selected_person is not None:
        pw = st.text_input("오늘의 코드를 입력하세요:", type="password")

        car_usage = st.radio("자차를 이용하셨나요?", ["Y", "N"])
        start_location = end_location = car_number = ""

        if car_usage == "Y":
            start_location = st.text_input("출발지:(ex. 경기도 과천시)")
            end_location = st.text_input("도착지:(ex. 경기도 용인시)")
            car_number = st.text_input("차량번호 (Full):")

        if st.button("CHECK-IN"):
            if pw != "250513":
                st.error("오늘의 코드가 틀렸습니다.")
            elif not pd.isna(members_df.at[selected_global_index, "체크"]):
                st.warning("이미 출석이 완료된 사용자입니다.")
            else:
                group_number = mark_attendance(selected_global_index, car_usage, start_location, end_location, car_number)
                st.success("출석이 완료되었습니다. 감사합니다. : )")
                st.info(f"🎉 {selected_person['사원이름']} CP님은 {group_number}조입니다. 강의장 메인 화면을 확인하시고, 자리에 앉아주세요. 명찰을 과정 중 꼭 패용해 주시기 바랍니다. 즐겁고 유익한 시간 되시기 바랍니다. : )")

with tab2:
    st.markdown("---")
    admin_pw = st.text_input("관리자 비밀번호를 입력하세요:", type="password", key="admin_view")
    if admin_pw == "visang.ggs":
        st.subheader("✅ 출석 완료자")
        st.dataframe(members_df[members_df["체크"].notna()])

        st.subheader("❌ 미출석자")
        st.dataframe(members_df[members_df["체크"].isna()])

        # 다운로드 옵션 유지
        st.markdown("---")
        csv_download = members_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 출석현황.csv 다운로드",
            data=csv_download,
            file_name="출석현황.csv",
            mime="text/csv"
        )
    elif admin_pw:
        st.warning("비밀번호가 틀렸습니다.")
