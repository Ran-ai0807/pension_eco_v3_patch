import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="养老生态全链条评估沙盘 V3", layout="wide")

st.title("养老生态全链条评估沙盘 (V3 双端完全体)")
st.caption("政策端精算 × 个人端税优 × 健康情感联动 | 仅用于学术演示")

with st.sidebar:
    st.header("1. 评估模式")
    mode = st.radio("面向人群", ["年轻预备役（积累期）", "银发一族（消耗期）"])
    gender = st.selectbox("性别", ["男", "女"])
    
    st.header("2. 政策端精算参数")
    base_salary = st.number_input("当前/预期月薪（元）", 3000, 50000, 10000)
    pay_years = st.slider("累计缴费年限（年）", 15, 40, 25)
    retire_age = st.slider("计划退休年龄", 55, 65, 60)
    avg_wage = st.number_input("当地社平工资（元/月）", 5000, 20000, 8000)
    pay_index = st.slider("平均缴费工资指数", 0.6, 3.0, 1.0, 0.1)
    
    if mode == "年轻预备役（积累期）":
        st.header("3. 青年未来养老预估")
        savings = st.number_input("目前存款（万元）", 0, 500, 20)
        monthly_income = st.number_input("预计退休后总收入（元）", 2000, 30000, 8000)
        monthly_spend = st.number_input("预计退休后月支出（元）", 2000, 30000, 6000)
    else:
        st.header("3. 老年人当前档案")
        savings = st.number_input("当前养老储备（万元）", 0, 500, 80)
        monthly_income = st.number_input("当前月总收入（元）", 2000, 30000, 5000)
        monthly_spend = st.number_input("当前每月支出（元）", 2000, 30000, 4500)
        
    st.header("4. 个人养老金规划")
    pp_contribute = st.number_input("每年顶格缴存（元）", 0, 12000, 12000, step=1000)
    pp_years = st.slider("预计缴存年限（年）", 1, 30, 15)
    pp_withdraw_years = st.slider("预计领取年限（年）", 10, 30, 15)
    
    st.header("5. 个人养老金投资偏好")
    risk_pref = st.selectbox("风险偏好推荐方案", ["保守型（固收为主）", "稳健型（股债平衡）", "激进型（权益为主）", "自定义"])
    
    if risk_pref == "保守型（固收为主）":
        default_eq = 20
    elif risk_pref == "稳健型（股债平衡）":
        default_eq = 50
    elif risk_pref == "激进型（权益为主）":
        default_eq = 80
    else:
        default_eq = 50
        
    custom_eq = st.slider("自定义权益类（基金）比例 %", 0, 100, default_eq)

    st.header("6. 健康与情感")
    health = st.select_slider("健康自评", ["较差", "一般", "良好"], value="一般")
    lonely = st.selectbox("陪伴情况", ["独居，很少与人交流", "偶尔有人探望", "家人日常陪伴"])
    
    run = st.button("生成全链条评估报告", type="primary", use_container_width=True)

def calc_pension(base_salary, pay_years, avg_wage, pay_index, retire_age):
    months_map = {55: 170, 60: 139, 65: 101}
    months = months_map.get(retire_age, 139)
    base_pension = avg_wage * (1 + pay_index) / 2 * pay_years * 0.01
    personal_account = base_salary * 0.08 * 12 * pay_years
    account_pension = personal_account / months
    total = base_pension + account_pension
    return {
        "基础养老金": round(base_pension, 2), 
        "个人账户养老金": round(account_pension, 2), 
        "合计月养老金": round(total, 2)
    }

def calc_pp(base_salary, pp_contribute, pp_years, eq_ratio):
    total_contribute = pp_contribute * pp_years
    expected_return = (eq_ratio / 100) * 0.07 + (1 - eq_ratio / 100) * 0.03
    future_value = 0
    for _ in range(pp_years):
        future_value = (future_value + pp_contribute) * (1 + expected_return)
        
    tax_saved = total_contribute * 0.1
    tax_on_withdraw = future_value * 0.03
    net_value = future_value - tax_on_withdraw + tax_saved
    return {
        "累计本金": total_contribute, 
        "预计账户价值": round(future_value, 2), 
        "净收益": round(net_value, 2), 
        "预期年化": round(expected_return*100, 1)
    }

def mock_health_audit(age, health):
    score = {"较差": 30, "一般": 60, "良好": 85}[health] - max(0, (age - 65)) * 1.0
    score = max(0, min(100, score))
    level = "高" if score < 40 else ("中" if score < 70 else "低")
    if level == "高":
        advice = "建议接入智能监护设备（防跌倒），并在合同中明确AI决策不能作为拒赔唯一依据。"
    else:
        advice = "维持现有健康管理节奏。"
    return {"健康风险分": f"{score:.0f}/100", "风险等级": level, "健康建议": advice}

def mock_emotion_audit(lonely):
    if "独居" in lonely:
        return "强", "【防幻觉预警】AI陪伴虽好，但警惕近期‘AI乱给打赏码’事件，涉及资金支付必须人工介入。"
    elif "偶尔" in lonely:
        return "中", "可使用AI语音助手辅助用药提醒。"
    else:
        return "弱", "重点关注防诈骗风险。"

if run:
    pension_result = calc_pension(base_salary, pay_years, avg_wage, pay_index, retire_age)
    pp_result = calc_pp(base_salary, pp_contribute, pp_years, custom_eq)
    hea = mock_health_audit(retire_age, health)
    emo_level, emo_advice = mock_emotion_audit(lonely)
    replacement_rate = pension_result["合计月养老金"] / base_salary * 100

    st.subheader("模块一：政策端宏观评估")
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("基础养老金（月）", f"¥{pension_result['基础养老金']:,}")
        with col2:
            st.metric("个人账户养老金（月）", f"¥{pension_result['个人账户养老金']:,}")
        with col3:
            st.metric("合计月养老金", f"¥{pension_result['合计月养老金']:,}", delta=f"替代率 {replacement_rate:.1f}%")

    st.divider()

    st.subheader("模块二：个人养老金税优与自定义配置方案")
    with st.container():
        p1, p2, p3, p4 = st.columns(4)
        with p1:
            st.metric("累计本金", f"¥{pp_result['累计本金']:,}")
        with p2:
            st.metric("预计账户价值", f"¥{pp_result['预计账户价值']:,}", delta=f"年化 {pp_result['预期年化']}%")
  