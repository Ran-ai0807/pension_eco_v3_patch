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
    return {"基础养老金": round(base_pension, 2), "个人账户养老金": round(account_pension, 2), "合计月养老金": round(total, 2)}

def calc_pp(base_salary, pp_contribute, pp_years, eq_ratio):
    total_contribute = pp_contribute * pp_years
    expected_return = (eq_ratio / 100) * 0.07 + (1 - eq_ratio / 100) * 0.03
    future_value = 0
    for _ in range(pp_years):
        future_value = (future_value + pp_contribute) * (1 + expected_return)
    tax_saved = total_contribute * 0.1
    tax_on_withdraw = future_value * 0.03
    net_value = future_value - tax_on_withdraw + tax_saved
    return {"累计本金": total_contribute, "预计账户价值": round(future_value, 2), "净收益": round(net_value, 2), "预期年化": round(expected_return*100, 1)}

def mock_health_audit(age, health):
    score = {"较差": 30, "一般": 60, "良好": 85}[health] - max(0, (age - 65)) * 1.0
    score = max(0, min(100, score))
    level = "高" if score < 40 else ("中" if score < 70 else "低")
    advice = "建议接入智能监护设备（防跌倒），并在合同中明确AI决策不能作为拒赔唯一依据。" if level == "高" else "维持现有健康管理节奏。"
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
    col1, col2, col3 = st.columns(3)
    col1.metric("基础养老金（月）", f"¥{pension_result['基础养老金']:,}")
    col2.metric("个人账户养老金（月）", f"¥{pension_result['个人账户养老金']:,}")
    col3.metric("合计月养老金", f"¥{pension_result['合计月养老金']:,}", delta=f"替代率 {replacement_rate:.1f}%")

    st.divider()

    st.subheader("模块二：个人养老金税优与自定义配置方案")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("累计本金", f"¥{pp_result['累计本金']:,}")
    p2.metric("预计账户价值", f"¥{pp_result['预计账户价值']:,}", delta=f"年化 {pp_result['预期年化']}%")
    p3.metric("预计节税", f"¥{pp_result['累计本金']*0.1:,}")
    p4.metric("净收益（含税优）", f"¥{pp_result['净收益']:,}")
    
    df_pie = pd.DataFrame({"资产类型": ["固收类", "权益类"], "比例": [100-custom_eq, custom_eq]})
    fig_pie = px.pie(df_pie, names="资产类型", values="比例", hole=0.5, title=f"当前方案：{risk_pref} ({custom_eq}% 权益)")
    fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0), height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    st.subheader("模块三：多方案横向对比")
    scenarios = []
    for idx in [0.6, 1.0, 1.5, 2.0, 3.0]:
        res = calc_pension(base_salary, pay_years, avg_wage, idx, retire_age)
        scenarios.append({"缴费指数": idx, "月养老金": res["合计月养老金"]})
    df_sc = pd.DataFrame(scenarios)
    fig_sc = px.bar(df_sc, x="缴费指数", y="月养老金", text="月养老金", title="不同缴费指数下的月养老金对比")
    fig_sc.update_traces(texttemplate='¥%{text:,.0f}', textposition='outside')
    st.plotly_chart(fig_sc, use_container_width=True)

    st.divider()

    st.subheader("模块四：健康与情感联动评估")
    hc1, hc2, hc3 = st.columns(3)
    with hc1:
        st.metric("建议权益比例", f"{custom_eq}%")
        st.metric("建议固收比例", f"{100-custom_eq}%")
        if mode == "年轻预备役（积累期）":
            st.error("【算法审计预警】参考NBER研究：AI倾向于给女性更低的权益配置。")
        else:
            st.error("【算法审计预警】参考Earnest案：AI可能基于历史数据产生歧视，警惕隐藏条款。")
    with hc2:
        st.metric("健康风险分", hea["健康风险分"])
        st.metric("综合风险等级", hea["风险等级"])
        st.info(hea["健康建议"])
    with hc3:
        st.metric("陪伴需求强度", emo_level)
        st.warning(emo_advice)

    st.subheader("模块五：生态健康度雷达图")
    fin_score = 70
    hea_score = int(hea["健康风险分"].split("/")[0])
    emo_score = {"强": 30, "中": 65, "弱": 90}[emo_level]
    radar = go.Figure(data=go.Scatterpolar(
        r=[fin_score, hea_score, emo_score, fin_score],
        theta=["金融稳健度", "健康安全度", "情感满足度", "金融稳健度"],
        fill="toself", fillcolor="rgba(0, 122, 255, 0.2)", line_color="#007AFF" 
    ))
    radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350)
    st.plotly_chart(radar, use_container_width=True)

    st.subheader("模块六：长寿风险与资金耗尽模拟")
    net_withdraw = max(0, (monthly_spend - monthly_income - pension_result["合计月养老金"]) * 12)
    np.random.seed(42)
    n_sim = 500
    returns = np.random.normal(0.04, 0.08, (n_sim, 40))
    balances = np.zeros((n_sim, 41))
    balances[:, 0] = savings * 10000
    for t in range(1, 41):
        withdraw = net_withdraw * (1.03 ** (t - 1))
        balances[:, t] = balances[:, t-1] * (1 + returns[:, t-1]) - withdraw
        balances[:, t] = np.maximum(balances[:, t], 0)
    depletion = []
    for i in range(n_sim):
        zero = np.where(balances[i] <= 0)[0]
        depletion.append(retire_age + (zero[0] if len(zero) > 0 else 40))
    fig = px.histogram(x=depletion, nbins=20, labels={"x": "资金耗尽年龄", "y": "频次"}, title="养老金耗尽年龄模拟")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', colorway=["#007AFF"])
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"每月资金缺口：¥{net_withdraw/12:,.0f} | 500次模拟中位耗尽年龄：{int(np.median(depletion))} 岁")

    st.divider()
    
    st.subheader("模块七：退休后综合现金流推演")
    pp_monthly_income = pp_result["预计账户价值"] / (pp_withdraw_years * 12)
    savings_monthly_income = 2000 
    cash_flow_data = pd.DataFrame({
        "收入来源": ["国家社保", "个人养老金", "自有资产增值"],
        "金额": [pension_result["合计月养老金"], pp_monthly_income, savings_monthly_income]
    })
    fig_cf = px.bar(cash_flow_data, x="金额", y="收入来源", orientation='h', text="金额", title="退休后每月收入来源拆解（元）")
    fig_cf.update_traces(texttemplate='¥%{text:,.0f}', textposition='outside', marker_color=['#34C759', '#007AFF', '#FF9500'])
    fig_cf.update_layout(height=300)
    st.plotly_chart(fig_cf, use_container_width=True)
    
    total_monthly_retire_income = pension_result["合计月养老金"] + pp_monthly_income + savings_monthly_income
    st.success(f"综合推演结果：退休后您预计每月可支配总收入为 **¥{total_monthly_retire_income:,.0f}**。")

else:
    st.info("请在左侧填写参数后，点击「生成全链条评估报告」。")