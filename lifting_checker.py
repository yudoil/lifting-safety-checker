
# Streamlit 웹앱 버전: 중량물 인양 안전성 검토기 (엑셀 기반 수치 반영)

import streamlit as st
import math

# 인양기구 기준 테이블 (엑셀 기반 수치 반영)
def get_sling_cut_load(width_mm):
    sling_table = {
        25: 1.6, 50: 3.2, 75: 4.8, 100: 6.4, 125: 8.0,
        150: 9.6, 200: 12.8, 250: 16.0, 300: 19.2
    }  # 단위: ton (Basket Type 기준)
    return sling_table.get(width_mm, 0)

def get_wire_cut_load(diameter_mm):
    wire_table = {
        14: 13.2, 16: 17.2, 18: 21.8, 20: 26.9,
        22: 33.8, 24: 38.8, 26: 45.5, 28: 52.8,
        30: 60.6, 32: 69.0, 36: 87.3, 38: 97.3,
        40: 108.0, 44: 130.0, 46: 143.0, 50: 168.0
    }
    return wire_table.get(diameter_mm, 0)

def get_shackle_wll(size_inch):
    shackle_table = {
        0.5: 2.0, 0.625: 3.25, 0.75: 4.75,
        0.875: 6.5, 1.0: 8.5, 1.125: 9.5, 1.25: 12.0
    }
    return shackle_table.get(size_inch, 0)

# 계산 함수들
def calculate_sling_belt_safe_load(width_mm, count, safety_factor, angle_deg):
    cut_load = get_sling_cut_load(width_mm)
    angle_rad = math.radians(angle_deg)
    coefficient = 1 / math.cos(angle_rad)
    safe_load1 = (cut_load * count) / safety_factor
    safe_load2 = (cut_load * count) / (safety_factor * coefficient)
    return round(min(safe_load1, safe_load2), 2)

def calculate_wire_rope_safe_load(diameter_mm, count, safety_factor, efficiency, angle_deg):
    cut_load = get_wire_cut_load(diameter_mm)
    angle_rad = math.radians(angle_deg)
    coefficient = 1 / math.cos(angle_rad)
    safe_load = (cut_load * count * efficiency) / (safety_factor * coefficient)
    return round(safe_load, 2)

def calculate_shackle_safe_load(size_inch, count, safety_factor):
    wll = get_shackle_wll(size_inch)
    safe_load = (wll * count) / safety_factor
    return round(safe_load, 2)

def calculate_crane_safe_load(rated_load, safety_rate=0.9):
    return round(rated_load * safety_rate, 2)

def check_safety(safe_load, actual_load):
    return "✅ 적합" if safe_load >= actual_load else "❌ 부적합"

# Streamlit UI
st.title("🔧 중량물 인양 안전성 검토기")
st.markdown("선택한 항목의 조건을 입력하면 실제 인양 가능 여부를 확인할 수 있습니다.")

actual_load = st.number_input("✅ 인양할 실제 하중 (ton)", min_value=0.1, value=2.0, step=0.1)

options = st.multiselect("검토할 항목을 선택하세요:", ["슬링벨트", "와이어로프", "샤클", "크레인"], default=["슬링벨트"])

if "슬링벨트" in options:
    st.subheader("🟩 슬링벨트 조건")
    sling_width = st.selectbox("슬링벨트 폭 (mm)", [25, 50, 75, 100, 125, 150, 200, 250, 300])
    sling_count = st.number_input("슬링벨트 개수", min_value=1, value=2)
    sling_angle_between = st.slider("슬링 사이 각도 (도)", min_value=0, max_value=180, value=120)
    sling_angle = sling_angle_between / 2
    sling_safe = calculate_sling_belt_safe_load(sling_width, sling_count, 5, sling_angle)
    st.write(f"🔸 슬링벨트 안전하중: **{sling_safe} ton** → {check_safety(sling_safe, actual_load)}")

if "와이어로프" in options:
    st.subheader("🟦 와이어로프 조건")
    wire_diameter = st.selectbox("와이어로프 직경 (mm)", [14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 36, 38, 40, 44, 46, 50])
    wire_count = st.number_input("와이어로프 개수", min_value=1, value=2)
    wire_efficiency = st.slider("단말가공 효율 (%)", min_value=50, max_value=100, value=85) / 100
    wire_angle = st.slider("줄걸이 각도 (도)", min_value=0, max_value=90, value=60)
    wire_safe = calculate_wire_rope_safe_load(wire_diameter, wire_count, 5, wire_efficiency, wire_angle)
    st.write(f"🔸 와이어로프 안전하중: **{wire_safe} ton** → {check_safety(wire_safe, actual_load)}")

if "샤클" in options:
    st.subheader("🟥 샤클 조건")
    shackle_size = st.selectbox("샤클 규격 (inch)", [0.5, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25])
    shackle_count = st.number_input("샤클 개수", min_value=1, value=2)
    shackle_safe = calculate_shackle_safe_load(shackle_size, shackle_count, 3)
    st.write(f"🔸 샤클 안전하중: **{shackle_safe} ton** → {check_safety(shackle_safe, actual_load)}")

if "크레인" in options:
    st.subheader("🟨 크레인 조건")
    crane_rated = st.number_input("정격하중 (ton)", min_value=0.1, value=7.9, step=0.1, help="※ 장비 모델의 Load Chart(정격하중표) 기준 수치를 입력해주세요.")
    crane_safe = calculate_crane_safe_load(crane_rated)
    st.write(f"🔸 크레인 안전하중: **{crane_safe} ton** → {check_safety(crane_safe, actual_load)}")
