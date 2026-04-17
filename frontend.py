# frontend.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# 配置页面
st.set_page_config(page_title="企业画像系统", layout="wide", initial_sidebar_state="expanded")

# FastAPI 后端地址
BACKEND_URL = "http://localhost:8000"

# --- 辅助函数：从后端获取数据 ---
@st.cache_data
def fetch_companies(limit=50):
    response = requests.get(f"{BACKEND_URL}/companies/?limit={limit}")
    return pd.DataFrame(response.json())

@st.cache_data
def fetch_company_detail(name):
    response = requests.get(f"{BACKEND_URL}/company/{name}")
    return response.json()

@st.cache_data
def fetch_top_n(metric, n):
    response = requests.get(f"{BACKEND_URL}/analysis/{metric}/top/{n}")
    return pd.DataFrame(response.json())

@st.cache_data
def fetch_distribution(dim):
    response = requests.get(f"{BACKEND_URL}/distribution/{dim}")
    return pd.DataFrame(response.json())

@st.cache_data
def fetch_model_scores(limit=10):
    response = requests.get(f"{BACKEND_URL}/model_scores/?limit={limit}")
    return pd.DataFrame(response.json())

@st.cache_data
def fetch_radar_data(name):
    response = requests.get(f"{BACKEND_URL}/radar_data/{name}")
    return pd.DataFrame(response.json())


# --- 侧边栏导航 ---
st.sidebar.title("企业画像系统")
page = st.sidebar.radio("导航", 
                        ["首页：总览", 
                         "第二页：经营规模分析", 
                         "第三页：经营情况分析",
                         "第四页：财务状况分析",
                         "第五页：信用属性分析",
                         "第六页：创新能力分析",
                         "第七页：企业评价模型",
                         "第八页：企业画像(雷达图)"])

st.sidebar.markdown("---")
st.sidebar.info("数据更新时间: 2026-04-16")

# --- 页面逻辑分发 ---
if page == "首页：总览":
    st.title("1. 首页：企业总览")
    
    all_companies = fetch_companies()
    
    # 1. 行业分布
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1）行业分布")
        industry_dist = fetch_distribution('行业')
        if not industry_dist.empty:
            fig1 = px.pie(industry_dist, values='count', names='行业', title='企业行业占比')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("未获取到行业分布数据。")
    
    # 2. 地域分布
    with col2:
        st.subheader("2）地域分布")
        region_dist = fetch_distribution('省份')
        if not region_dist.empty:
            fig2 = px.bar(region_dist, x='省份', y='count', color='count', title='企业地域分布')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("未获取到地域分布数据。")

    # 3. 企业年龄分布
    st.subheader("3）企业年龄分布")
    if '企业年龄' in all_companies.columns:
        fig3 = px.histogram(all_companies, x='企业年龄', nbins=20, title='企业年龄分布直方图')
        st.plotly_chart(fig3, use_container_width=True)

    # 4. 人员规模分布
    st.subheader("4）人员规模")
    if '人员规模' in all_companies.columns:
        # 创建一个分级列
        all_companies['人员规模分级'] = pd.cut(all_companies['人员规模'], 
                                               bins=[0, 50, 300, 1000, 5000, float('inf')], 
                                               labels=['微型企业 (≤50人)', '小型企业 (51-300人)', '中型企业 (301-1000人)', '大型企业 (1001-5000人)', '超大型企业 (>5000人)'])
        scale_dist = all_companies['人员规模分级'].value_counts().reset_index()
        scale_dist.columns = ['规模等级', '数量']
        fig4 = px.bar(scale_dist, x='规模等级', y='数量', title='人员规模分布')
        st.plotly_chart(fig4, use_container_width=True)

    # 5. 注册资金分布
    st.subheader("5）注册资金")
    if '注册资金' in all_companies.columns:
        # 由于注册资金范围很大，使用对数刻度或直方图
        fig5 = px.histogram(all_companies, x='注册资金', nbins=20, title='注册资金分布直方图')
        # 格式化x轴标签
        fig5.update_xaxes(tickprefix="¥ ", tickformat=".0f")
        st.plotly_chart(fig5, use_container_width=True)

    # 6. 企业资质分布
    st.subheader("6）企业资质")
    if '资质' in all_companies.columns:
        # 直接统计所有值，包括可能的空值（但根据新数据，应无空值）
        zizhi_dist = all_companies['资质'].value_counts().reset_index()
        zizhi_dist.columns = ['资质', '数量']
        
        # 检查是否有有效数据
        if zizhi_dist.empty or zizhi_dist['数量'].sum() == 0:
            st.warning("⚠️ 未获取到有效的企业资质数据。请检查后端数据源。")
        else:
            # 创建一个更清晰的标签映射（可选，用于美化）
            label_map = {
                '高新技术企业': '高新技术企业',
                '专精特新企业': '专精特新企业',
                '普通企业': '普通企业'
            }
            zizhi_dist['资质_显示'] = zizhi_dist['资质'].map(label_map).fillna(zizhi_dist['资质'])
            
            fig6 = px.pie(
                zizhi_dist,
                values='数量',
                names='资质_显示',
                title='企业资质分布',
                hole=0.3,  # 添加环形图效果，更现代
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            # 添加百分比标签
            fig6.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig6, use_container_width=True)
            
            # # 同时展示一个简洁的表格，方便查看具体数值
            # st.caption("资质统计表:")
            # st.dataframe(zizhi_dist[['资质_显示', '数量']].rename(columns={'资质_显示': '资质'}), use_container_width=True)
    else:
        st.error("❌ 数据中不存在 '资质' 列。")

elif page == "第二页：经营规模分析":
    st.title("2. 经营规模分析")
    
    # 修复：使用 df 中实际存在的列名
    scale_metrics = ["注册资金", "实收资本", "资产总额", "销售总额", "人员规模", "分支机构数量"]
    
    top_n = st.slider("选择显示前 N 个企业", 5, 20, 10, key="scale_top")
    
    cols = st.columns(2)
    for i, metric in enumerate(scale_metrics):
        with cols[i % 2]:
            try:
                top_data = fetch_top_n(metric, top_n)
                if not top_data.empty:
                    # 格式化大数字
                    if metric in ['注册资金', '实收资本', '资产总额', '销售总额']:
                        top_data['显示值'] = top_data['value'] / 10000
                    else:
                        top_data['显示值'] = top_data['value']
                        
                    fig = px.bar(top_data, x='显示值', y='企业名称', orientation='h', title=f"{metric} Top {top_n}")
                    fig.update_layout(yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"指标 '{metric}' 的数据为空。")
            except Exception as e:
                st.error(f"获取指标 '{metric}' 数据时出错: {e}")

elif page == "第三页：经营情况分析":
    st.title("3. 经营情况分析")
    
    st.markdown("#### 1. 交易活跃度")
    active_metrics = ["月度开票活跃天数", "近一年开票月份数", "连续无交易天数"]
    top_trade = st.slider("交易活跃度 Top N", 5, 20, 10, key="trade_top")
    cols = st.columns(3)
    for idx, metric in enumerate(active_metrics):
        with cols[idx]:
            try:
                top_data = fetch_top_n(metric, top_trade)
                if not top_data.empty:
                    fig = px.bar(top_data, x='value', y='企业名称', orientation='h', title=f"{metric} Top {top_trade}")
                    fig.update_layout(yaxis=dict(autorange="reversed"), height=300)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"指标 '{metric}' 的数据为空。")
            except Exception as e:
                st.error(f"获取指标 '{metric}' 数据时出错: {e}")

    st.markdown("#### 2. 供应链与采购特征")
    supply_metrics = ["供应商集中度", "大客户依赖度"]
    cols = st.columns(2)
    for idx, metric in enumerate(supply_metrics):
        with cols[idx]:
            try:
                # 获取所有公司的该指标数据用于分布图
                all_data_response = requests.get(f"{BACKEND_URL}/companies/")
                all_data_df = pd.DataFrame(all_data_response.json())
                
                if metric in all_data_df.columns:
                    fig = px.scatter(all_data_df, x=metric, y='行业', title=f"{metric}行业分布", size=metric)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"数据中不存在列 '{metric}'。")
            except Exception as e:
                st.error(f"获取指标 '{metric}' 数据时出错: {e}")

elif page == "第四页：财务状况分析":
    st.title("4. 财务状况分析")
    
    st.markdown("#### 1. 盈利能力分析")
    profit_metrics = ["营业收入", "净利润", "毛利率"]
    cols = st.columns(3)
    for idx, metric in enumerate(profit_metrics):
        with cols[idx]:
            try:
                top_data = fetch_top_n(metric, 10)
                if not top_data.empty:
                    fig = px.bar(top_data, x='value', y='企业名称', orientation='h', title=f"{metric} Top 10")
                    fig.update_layout(yaxis=dict(autorange="reversed"), height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"指标 '{metric}' 的数据为空。")
            except Exception as e:
                st.error(f"获取指标 '{metric}' 数据时出错: {e}")

    st.markdown("#### 2. 偿债能力分析")
    try:
        all_data_response = requests.get(f"{BACKEND_URL}/companies/")
        all_data_df = pd.DataFrame(all_data_response.json())
        
        if '资产负债率' in all_data_df.columns:
            fig = px.histogram(all_data_df, x='资产负债率', nbins=20, title="资产负债率分布")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中不存在列 '资产负债率'。")
    except Exception as e:
        st.error(f"获取资产负债率数据时出错: {e}")

elif page == "第五页：信用属性分析":
    st.title("5. 信用属性分析")
    
    st.markdown("#### 1. 税务信用等级")
    try:
        credit_dist = fetch_distribution('纳税人信用等级')
        if not credit_dist.empty:
            fig = px.pie(credit_dist, values='count', names='纳税人信用等级', title='纳税人信用等级分布')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("未获取到纳税人信用等级数据。")
    except Exception as e:
        st.error(f"获取纳税人信用等级数据时出错: {e}")

    st.markdown("#### 2. 违规与欠税情况")
    cols = st.columns(2)
    with cols[0]:
        try:
            top_arrears = fetch_top_n("欠税余额", 10)
            if not top_arrears.empty:
                fig = px.bar(top_arrears, x='value', y='企业名称', orientation='h', title="欠税余额 Top 10")
                fig.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("欠税余额数据为空。")
        except Exception as e:
            st.error(f"获取欠税余额数据时出错: {e}")
    
    with cols[1]:
        try:
            top_cases = fetch_top_n("司法案件数", 10)
            if not top_cases.empty:
                fig = px.bar(top_cases, x='value', y='企业名称', orientation='h', title="司法案件数 Top 10")
                fig.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("司法案件数数据为空。")
        except Exception as e:
            st.error(f"获取司法案件数数据时出错: {e}")

elif page == "第六页：创新能力分析":
    st.title("6. 创新能力分析")
    
    st.markdown("#### 1. 研发投入")
    r_d_metrics = ["研发费用", "研发人员占比"]
    cols = st.columns(2)
    for idx, metric in enumerate(r_d_metrics):
        with cols[idx]:
            try:
                top_data = fetch_top_n(metric, 10)
                if not top_data.empty:
                    fig = px.bar(top_data, x='value', y='企业名称', orientation='h', title=f"{metric} Top 10")
                    fig.update_layout(yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"指标 '{metric}' 的数据为空。")
            except Exception as e:
                st.error(f"获取指标 '{metric}' 数据时出错: {e}")

    st.markdown("#### 2. 知识产权产出")
    cols = st.columns(2)
    with cols[0]:
        try:
            top_patents = fetch_top_n("专利数量", 10)
            if not top_patents.empty:
                fig = px.scatter(top_patents, x='value', y='企业名称', size='value', color='value', title="专利数量分布")
                fig.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("专利数量数据为空。")
        except Exception as e:
            st.error(f"获取专利数量数据时出错: {e}")
    
    with cols[1]:
        try:
            all_data_response = requests.get(f"{BACKEND_URL}/companies/")
            all_data_df = pd.DataFrame(all_data_response.json())
            
            specialized_df = all_data_df[all_data_df['是否专精特新企业'] == 1]
            if not specialized_df.empty:
                fig = px.sunburst(specialized_df, path=['行业', '企业名称'], values='专利数量', title="专精特新企业行业分布")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无专精特新企业数据")
        except Exception as e:
            st.error(f"获取专精特新企业数据时出错: {e}")

elif page == "第七页：企业评价模型":
    st.title("7. 企业评价模型")
    
    try:
        model_scores_df = fetch_model_scores()
        if not model_scores_df.empty:
            st.markdown("#### 模型一：企业信用价值评估")
            st.table(model_scores_df[['企业名称', '企业信用价值评估']].sort_values('企业信用价值评估', ascending=False))

            st.markdown("#### 模型二：企业成长价值评估")
            st.table(model_scores_df[['企业名称', '企业成长价值评估']].sort_values('企业成长价值评估', ascending=False))

            st.markdown("#### 模型三：企业投资价值分析")
            st.table(model_scores_df[['企业名称', '企业投资价值分析']].sort_values('企业投资价值分析', ascending=False))

            st.markdown("#### 模型四：企业风险评估 (风险越低越好)")
            st.table(model_scores_df[['企业名称', '企业风险评估']].sort_values('企业风险评估', ascending=True))
        else:
            st.warning("未获取到模型评分数据。")
    except Exception as e:
        st.error(f"获取模型评分数据时出错: {e}")

elif page == "第八页：企业画像(雷达图)":
    st.title("8. 企业画像 (雷达图)")
    
    all_companies_names = fetch_companies()['企业名称'].tolist()
    selected_company = st.selectbox("选择企业", all_companies_names)
    
    try:
        radar_data_df = fetch_radar_data(selected_company)
        if not radar_data_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=radar_data_df['score'].tolist() + [radar_data_df['score'].iloc[0]], # 闭合图形
                theta=radar_data_df['dimension'].tolist() + [radar_data_df['dimension'].iloc[0]], # 闭合图形
                fill='toself',
                name='企业得分'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=False,
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(radar_data_df, use_container_width=True)
            
            # 显示详细信息
            st.subheader("企业详细数据")
            company_details = fetch_company_detail(selected_company)
            st.json(company_details)
        else:
            st.warning(f"未获取到企业 '{selected_company}' 的雷达图数据。")
    except Exception as e:
        st.error(f"获取企业 '{selected_company}' 的雷达图数据时出错: {e}")