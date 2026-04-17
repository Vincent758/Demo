import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

# 页面配置
st.set_page_config(page_title="企业画像系统", layout="wide", initial_sidebar_state="expanded")

# --- 数据加载模块 ---
@st.cache_data
def load_data():
    # 模拟数据生成
    np.random.seed(42)
    n = 50
    data = {
        '企业名称': [f'企业_{i}' for i in range(n)],
        '行业': np.random.choice(['制造业', '信息技术', '批发零售', '科学研究'], n),
        '省份': np.random.choice(['广东', '江苏', '浙江', '江西', '上海'], n),
        '企业年龄': np.random.randint(1, 31, n),
        '人员规模': np.random.randint(10, 5000, n),
        '注册资金': np.random.randint(100, 10000, n) * 10000, # 修复：统一使用此列名
        '资质': np.random.choice(['高新技术', '专精特新', '普通企业'], n, p=[0.2, 0.3, 0.5]),
        
        # 经营规模数据 (修复：修正列名以匹配下拉框)
        '实收资本': np.random.randint(50, 8000, n) * 10000,
        '资产总额': np.random.randint(500, 50000, n) * 10000,
        '销售总额': np.random.randint(100, 20000, n) * 10000,
        '近两年开票总金额': np.random.randint(50, 15000, n) * 10000,
        '近两年开票总份数': np.random.randint(100, 2000, n),
        '近两年客户总数': np.random.randint(10, 500, n),
        '近两年月均开票金额': np.random.randint(10, 800, n) * 10000,
        '实际经营月份数': np.random.randint(12, 360, n),
        '分支机构数量': np.random.randint(0, 50, n),

        # 经营情况数据
        # 1. 交易活跃度
        '月度开票活跃天数': np.random.randint(10, 30, n),
        '近一年开票月份数': np.random.randint(0, 12, n),
        '连续无交易天数': np.random.randint(0, 100, n),
        '近半年无交易月数': np.random.randint(0, 6, n),
        '最近半年销售金额': np.random.randint(30, 8000, n) * 10000,
        '最大开票间隔天数': np.random.randint(1, 60, n),
        # 2. 供应链与采购特征 (基于上游分析)
        '供应商集中度': np.random.rand(n),
        '进项发票合规率': np.random.uniform(0.5, 1.0, n),
        '上游行业多样性': np.random.randint(1, 6, n),
        # 3. 客户结构与依赖度 (基于下游分析)
        '大客户依赖度': np.random.rand(n),
        '客户集中度': np.random.uniform(0.1, 0.9, n),
        '客户分散度': np.random.uniform(0.1, 0.9, n),   # 与集中度概念相反，但独立模拟
        # 4. 客户结构
        '新增客户占比': np.random.uniform(0.1, 0.6, n),
        '流失客户占比': np.random.uniform(0.1, 0.4, n),
        '老客户数量': np.random.randint(1, 200, n),

        # 5. 商品与销售结构
        '销售商品种类数': np.random.randint(5, 200, n),
        '核心商品销售金额占比': np.random.uniform(0.3, 0.9, n),
        '蓝票金额占比': np.random.uniform(0.6, 1.0, n),

        # 财务数据
        '营业收入': np.random.randint(100, 20000, n) * 10000,
        '净利润': np.random.randint(-1000, 5000, n) * 10000,
        '毛利率': np.random.rand(n),
        '资产负债率': np.random.rand(n),
        '净利率': np.random.uniform(-0.2, 0.3, n),
        '营业收入增长率': np.random.uniform(-0.2, 0.5, n),
        '流动比率': np.random.uniform(0.5, 3.0, n),
        '短期借款占比': np.random.uniform(0.0, 0.6, n),
        '实收资本占比': np.random.uniform(0.1, 0.8, n),
        '应收账款周转率': np.random.uniform(1.0, 12.0, n),
        '存货周转率': np.random.uniform(2.0, 15.0, n),
        '财务费用占比': np.random.uniform(0.0, 0.15, n),
        '经营活动现金流净额': np.random.randint(-5000, 15000, n) * 10000,
        '投资活动现金流净额': np.random.randint(-10000, 5000, n) * 10000,
        '筹资活动现金流净额': np.random.randint(-5000, 10000, n) * 10000,

        # 信用数据
        # 1.税务信用
        '纳税人信用等级': np.random.choice(['A', 'B', 'M', 'C', 'D'], n),
        '欠税余额': np.random.randint(0, 1000000, n),
        '增值税纳税人类型': np.random.choice(['一般纳税人', '小规模纳税人'], n, p=[0.7, 0.3]),
        '当期新增欠税金额': np.random.randint(0, 500000, n),
        '实缴金额占比': np.random.uniform(0.7, 1.0, n),
        '税款滞纳天数': np.random.randint(0, 60, n),
        # 2. 法律与合规风险
        '行政处罚次数': np.random.randint(0, 5, n),
        '违法行为数量': np.random.randint(0, 8, n),
        '违法违章状态': np.random.choice(['已处理', '未处理', '无违法'], n, p=[0.2, 0.1, 0.7]),
        '税款状态异常次数': np.random.randint(0, 5, n),
        '是否发生过红冲/作废异常': np.random.choice([0, 1], n, p=[0.8, 0.2]),  # 1 表示发生过
        # 3. 红冲与作废行为
        '近两年红冲金额占比': np.random.uniform(0.0, 0.3, n),
        '近半年作废金额占比': np.random.uniform(0.0, 0.2, n),

        # 创新数据
        # 1. 知识产权
        '是否有创新载体': np.random.choice([0, 1], n, p=[0.6, 0.4]),  # 1=有
        '商标数量': np.random.randint(0, 50, n),
        '专利数量': np.random.randint(0, 100, n),
        # 2. 研发投入
        '研发费用占比': np.random.uniform(0.0, 0.25, n),
        '研发费用增长率': np.random.uniform(-0.2, 0.6, n),
        '研发费用': np.random.randint(0, 5000, n) * 10000,
        '研发人员占比': np.random.rand(n),
        # 3. 技术与产业定位
        '产业链位置': np.random.choice(['上游', '中游', '下游'], n),
        '产业规模等级': np.random.choice(['微型', '小型', '中型', '大型'], n, p=[0.2, 0.4, 0.3, 0.1]),
        '是否专精特新企业': np.random.choice([0, 1], n, p=[0.8, 0.2])
    }
    return pd.DataFrame(data)

df = load_data()

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
                         "第八页：企业画像"])

st.sidebar.markdown("---")
st.sidebar.info("数据更新时间: 2026-04-16")

# --- 页面逻辑分发 ---
if page == "首页：总览":
    st.title("1. 首页：企业总览")
    
    # 1. 行业分布
    st.subheader("1）行业分布")
    industry_cnt = df['行业'].value_counts()
    fig1 = px.pie(values=industry_cnt.values, names=industry_cnt.index, title='企业行业占比')
    st.plotly_chart(fig1, use_container_width=True)

    # 2. 地域分布
    st.subheader("2）地域分布")
    region_cnt = df['省份'].value_counts().reset_index()
    region_cnt.columns = ['省份', '数量']
    fig2 = px.bar(region_cnt, x='省份', y='数量', color='数量', title='企业地域分布')
    st.plotly_chart(fig2, use_container_width=True)

    # 3. 企业年龄分布
    st.subheader("3）企业年龄分布")
    fig3 = px.histogram(df, x='企业年龄', nbins=20, title='企业年龄分布直方图')
    st.plotly_chart(fig3, use_container_width=True)

    # 4. 人员规模
    st.subheader("4）人员规模")
    df['人员规模分级'] = pd.cut(df['人员规模'], bins=[0, 50, 300, 1000, 5000, 10000], labels=['微型企业', '小型企业', '中型企业', '大型企业', '特大型企业'])
    scale_cnt = df['人员规模分级'].value_counts()
    fig4 = px.bar(x=scale_cnt.index, y=scale_cnt.values, title='人员规模分布')
    st.plotly_chart(fig4, use_container_width=True)

    # 5. 注册资金
    st.subheader("5）注册资金")
    fig5 = px.histogram(df, x='注册资金', nbins=20, title='注册资金分布直方图')
    st.plotly_chart(fig5, use_container_width=True)

    # 6. 企业资质
    st.subheader("6）企业资质")
    zizhi_cnt = df['资质'].value_counts()
    fig6 = px.pie(values=zizhi_cnt.values, names=zizhi_cnt.index, title='企业资质分布')
    st.plotly_chart(fig6, use_container_width=True)

elif page == "第二页：经营规模分析":
    st.title("2. 经营规模分析")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 核心指标排名")
    with col2:
        top_n = st.slider("选择数量", 5, 20, 10, key="scale_top")

    metrics = [
        "注册资金", "实收资本", "资产总额", "销售总额", 
        "近两年开票总金额", "近两年开票总份数", "近两年客户总数",
        "近两年月均开票金额", "实际经营月份数", "分支机构数量", "人员规模"
    ]
    
    # 下拉选择框仅用于选择具体指标绘图
    selected_metric = st.selectbox("请选择要查看的指标", metrics)
    
    # --- 绘制所选指标的 Top N 条形图 ---
    metric = selected_metric
    top_data = df.nlargest(top_n, metric)[['企业名称', metric]].copy()
    if metric in ["注册资金", "实收资本", "资产总额", "销售总额", 
                  "近两年开票总金额", "近两年月均开票金额"]:
        top_data['显示值'] = top_data[metric] / 10000
        hover_text = "数值: %{x:.2f} 万元"
    else:
        top_data['显示值'] = top_data[metric]
        hover_text = "数值: %{x}"
    
    fig = px.bar(
        top_data,
        x='显示值',
        y='企业名称',
        orientation='h',
        title=f"{metric} Top {top_n}",
        text='显示值',
        hover_data={metric: True}
    )
    fig.update_traces(
        texttemplate='%{text:.2s}',
        textposition='outside',
        hovertemplate=hover_text
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=500,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # --- 固定显示所有指标得分表（位于图表下方）---
    st.markdown("---")
    st.subheader("📋 企业各经营规模指标得分表（百分位数排名，0-100分）")
    
    # 计算每个指标的得分
    score_df = df[['企业名称']].copy()
    for m in metrics:
        score_df[f'{m}_得分'] = (df[m].rank(pct=True) * 100).round(0).astype(int)
    
    # 原始总分
    score_cols = [f'{m}_得分' for m in metrics]
    raw_total = score_df[score_cols].sum(axis=1)
    
    # 将原始总分归一化到1-100
    min_total = raw_total.min()
    max_total = raw_total.max()
    if max_total > min_total:
        score_df['经营规模综合得分'] = ((raw_total - min_total) / (max_total - min_total) * 99 + 1).round(1)
    else:
        score_df['经营规模综合得分'] = 50.0  # 若所有企业总分相同，设为中间值
    
    # 按综合得分降序排列
    score_df_sorted = score_df.sort_values('经营规模综合得分', ascending=False)
    
    st.dataframe(
        score_df_sorted,
        use_container_width=True,
        height=600,
        hide_index=True
    )
    st.caption("各指标得分基于该指标在所有企业中的百分位数计算（0-100分）；综合得分为各指标得分之和经归一化处理后映射到1-100区间。")

elif page == "第三页：经营情况分析":
    st.title("3. 经营情况分析")
    
    # --- 定义五个分组的指标及其显示名称（用于图表标题）---
    groups = {
        "1. 交易活跃度": [
            "月度开票活跃天数", "近一年开票月份数", "连续无交易天数",
            "近半年无交易月数", "最近半年销售金额", "最大开票间隔天数"
        ],
        "2. 供应链与采购特征": [
            "供应商集中度", "进项发票合规率", "上游行业多样性"
        ],
        "3. 客户结构与依赖度": [
            "大客户依赖度", "客户集中度", "客户分散度"
        ],
        "4. 客户结构": [
            "新增客户占比", "流失客户占比", "老客户数量"
        ],
        "5. 商品与销售结构": [
            "销售商品种类数", "核心商品销售金额占比", "蓝票金额占比"
        ]
    }
    
    # 顶部控件：全局 Top N 选择
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 经营活跃与结构分析")
    with col2:
        top_n = st.slider("选择展示的 Top N 数量", 5, 20, 10, key="operation_top")
    
    # 使用选项卡分组展示
    tabs = st.tabs(list(groups.keys()))
    
    for tab, (group_name, metrics) in zip(tabs, groups.items()):
        with tab:
            st.markdown(f"#### {group_name}")
            # 每行最多展示两个图表
            cols = st.columns(2)
            for i, metric in enumerate(metrics):
                with cols[i % 2]:
                    top_data = df.nlargest(top_n, metric)[['企业名称', metric]].copy()
                    # 判断是否为百分比类型，调整格式
                    is_percent = "占比" in metric or "率" in metric or "集中度" in metric or "依赖度" in metric
                    if is_percent:
                        top_data['显示值'] = top_data[metric] * 100
                        title_suffix = " (%)"
                        hover_format = ".1f"
                        text_format = ".1f"
                    else:
                        top_data['显示值'] = top_data[metric]
                        title_suffix = ""
                        hover_format = ".2s"
                        text_format = ".2s"
                    
                    fig = px.bar(
                        top_data,
                        x='显示值',
                        y='企业名称',
                        orientation='h',
                        title=f"{metric} Top {top_n}{title_suffix}",
                        text='显示值',
                        hover_data={metric: True}
                    )
                    fig.update_traces(
                        texttemplate=f'%{{text:{text_format}}}',
                        textposition='outside',
                        hovertemplate=f"{metric}: %{{x:{hover_format}}}<extra></extra>"
                    )
                    fig.update_layout(
                        yaxis=dict(autorange="reversed"),
                        height=400,
                        margin=dict(l=50, r=50, t=50, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # --- 底部：所有指标得分表（综合得分限制在 1-100）---
    with st.expander("📊 查看全部企业 - 经营情况指标得分表 (百分位数排名，0-100分)"):
        # 收集所有需要计算得分的指标（共20个）
        all_metrics = []
        for m_list in groups.values():
            all_metrics.extend(m_list)
        
        score_df = df[['企业名称']].copy()
        for metric in all_metrics:
            # 百分位数排名（值越大越好，除了连续无交易天数、近半年无交易月数、最大开票间隔天数、流失客户占比是负向指标）
            # 负向指标：反转得分（1 - 百分位数）
            if metric in ["连续无交易天数", "近半年无交易月数", "最大开票间隔天数", "流失客户占比"]:
                score_df[f'{metric}_得分'] = (
                    (1 - df[metric].rank(pct=True)) * 100
                ).round(0).astype(int)
            else:
                score_df[f'{metric}_得分'] = (
                    df[metric].rank(pct=True) * 100
                ).round(0).astype(int)
        
        # 计算综合得分：所有指标得分之和
        score_cols = [f'{m}_得分' for m in all_metrics]
        raw_sum = score_df[score_cols].sum(axis=1)
        # 将综合得分映射到 1-100 区间 (线性缩放)
        min_sum = raw_sum.min()
        max_sum = raw_sum.max()
        if max_sum > min_sum:
            score_df['经营情况综合得分'] = (1 + 99 * (raw_sum - min_sum) / (max_sum - min_sum)).round(0).astype(int)
        else:
            score_df['经营情况综合得分'] = 50  # 全相等时给中间值
        
        # 按综合得分降序排列
        score_df_sorted = score_df.sort_values('经营情况综合得分', ascending=False)
        
        st.dataframe(
            score_df_sorted,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        st.caption("各指标得分基于百分位数计算（0-100分），负向指标已反转。经营情况综合得分 = 所有指标得分之和线性缩放至1-100区间。")

elif page == "第四页：财务状况分析":
    st.title("4. 财务状况分析")
    
    # 指标分组定义
    groups = {
        "1. 盈利能力": ["营业收入", "净利润", "毛利率", "净利率", "营业收入增长率"],
        "2. 偿债能力": ["资产负债率", "流动比率", "短期借款占比", "实收资本占比"],
        "3. 营运能力": ["应收账款周转率", "存货周转率", "财务费用占比"],
        "4. 现金流": ["经营活动现金流净额", "投资活动现金流净额", "筹资活动现金流净额"]
    }
    
    # 顶部控件
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 盈利、偿债、营运与现金流分析")
    with col2:
        top_n = st.slider("选择展示的 Top N 数量", 5, 20, 10, key="finance_top")
    
    # 选项卡分组展示
    tabs = st.tabs(list(groups.keys()))
    
    for tab, (group_name, metrics) in zip(tabs, groups.items()):
        with tab:
            st.markdown(f"#### {group_name}")
            cols = st.columns(2)
            for i, metric in enumerate(metrics):
                with cols[i % 2]:
                    # 排序获取 Top N
                    top_data = df.nlargest(top_n, metric)[['企业名称', metric]].copy()
                    
                    # 数值格式化处理
                    if metric in ["营业收入", "净利润", "经营活动现金流净额", 
                                  "投资活动现金流净额", "筹资活动现金流净额"]:
                        # 金额类除以 10000 显示为万元
                        top_data['显示值'] = top_data[metric] / 10000
                        unit = " (万元)"
                        hover_format = ".2f"
                        text_format = ".2s"
                    elif metric in ["毛利率", "净利率", "营业收入增长率", "资产负债率", 
                                    "短期借款占比", "实收资本占比", "财务费用占比"]:
                        # 比率类转为百分比显示
                        top_data['显示值'] = top_data[metric] * 100
                        unit = " (%)"
                        hover_format = ".1f"
                        text_format = ".1f"
                    else:
                        top_data['显示值'] = top_data[metric]
                        unit = ""
                        hover_format = ".2f"
                        text_format = ".2s"
                    
                    # 净利润和现金流可能为负，使用颜色区分
                    if metric in ["净利润", "经营活动现金流净额", "投资活动现金流净额", "筹资活动现金流净额"]:
                        colors = ['red' if v < 0 else 'green' for v in top_data[metric]]
                        fig = px.bar(
                            top_data,
                            x='显示值',
                            y='企业名称',
                            orientation='h',
                            title=f"{metric} Top {top_n}{unit}",
                            text='显示值',
                            hover_data={metric: True}
                        )
                        fig.update_traces(
                            texttemplate=f'%{{text:{text_format}}}',
                            textposition='outside',
                            marker_color=colors,
                            hovertemplate=f"{metric}: %{{x:{hover_format}}}{unit}<extra></extra>"
                        )
                    else:
                        fig = px.bar(
                            top_data,
                            x='显示值',
                            y='企业名称',
                            orientation='h',
                            title=f"{metric} Top {top_n}{unit}",
                            text='显示值',
                            hover_data={metric: True},
                            color='显示值',
                            color_continuous_scale='Blues'
                        )
                        fig.update_traces(
                            texttemplate=f'%{{text:{text_format}}}',
                            textposition='outside',
                            hovertemplate=f"{metric}: %{{x:{hover_format}}}{unit}<extra></extra>"
                        )
                    
                    fig.update_layout(
                        yaxis=dict(autorange="reversed"),
                        height=400,
                        margin=dict(l=50, r=50, t=50, b=50),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # --- 综合得分表（财务健康状况综合得分 1-100）---
    with st.expander("📊 查看全部企业 - 财务指标得分表 (百分位数排名，0-100分)"):
        all_metrics = []
        for m_list in groups.values():
            all_metrics.extend(m_list)
        
        score_df = df[['企业名称']].copy()
        for metric in all_metrics:
            # 负向指标：资产负债率、短期借款占比、财务费用占比 数值越低越好
            reverse_metrics = ["资产负债率", "短期借款占比", "财务费用占比"]
            if metric in reverse_metrics:
                score_df[f'{metric}_得分'] = (
                    (1 - df[metric].rank(pct=True)) * 100
                ).round(0).astype(int)
            else:
                score_df[f'{metric}_得分'] = (
                    df[metric].rank(pct=True) * 100
                ).round(0).astype(int)
        
        score_cols = [f'{m}_得分' for m in all_metrics]
        raw_sum = score_df[score_cols].sum(axis=1)
        min_sum = raw_sum.min()
        max_sum = raw_sum.max()
        if max_sum > min_sum:
            score_df['财务状况综合得分'] = (1 + 99 * (raw_sum - min_sum) / (max_sum - min_sum)).round(0).astype(int)
        else:
            score_df['财务状况综合得分'] = 50
        
        score_df_sorted = score_df.sort_values('财务状况综合得分', ascending=False)
        
        st.dataframe(
            score_df_sorted,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        st.caption("各指标得分基于百分位数计算（0-100分），负向指标已反转。财务状况综合得分 = 所有指标得分之和线性缩放至1-100区间。")

elif page == "第五页：信用属性分析":
    st.title("5. 信用属性分析")
    
    # --- 指标分组定义 ---
    groups = {
        "1. 税务信用": [
            "欠税余额", "当期新增欠税金额", "实缴金额占比", "税款滞纳天数"
        ],
        "2. 法律与合规风险": [
            "违法行为数量", "税款状态异常次数", "行政处罚次数"
        ],
        "3. 红冲与作废行为": [
            "近两年红冲金额占比", "近半年作废金额占比"
        ]
    }
    
    # 顶部控件
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 税务合规与法律风险分析")
    with col2:
        top_n = st.slider("选择展示的 Top N 数量", 5, 20, 10, key="credit_top")
    
    # 使用选项卡分组展示
    tabs = st.tabs(list(groups.keys()))
    
    # ---- 税务信用 Tab（特殊处理：包含等级分布图） ----
    with tabs[0]:
        st.markdown("#### 1. 税务信用")
        
        # 纳税人信用等级分布饼图
        st.markdown("##### 纳税人信用等级分布")
        tax_credit = df['纳税人信用等级'].value_counts().reset_index()
        tax_credit.columns = ['等级', '数量']
        fig_pie = px.pie(tax_credit, values='数量', names='等级', 
                         title='纳税人信用等级占比',
                         color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # 增值税纳税人类型分布
        st.markdown("##### 增值税纳税人类型分布")
        vat_type = df['增值税纳税人类型'].value_counts().reset_index()
        vat_type.columns = ['类型', '数量']
        fig_vat = px.bar(vat_type, x='类型', y='数量', text='数量',
                         title='增值税纳税人类型统计', color='类型')
        fig_vat.update_traces(textposition='outside')
        st.plotly_chart(fig_vat, use_container_width=True)
        
        # 其余税务信用指标（条形图）
        st.markdown("##### 税务信用关键指标 Top N")
        tax_metrics = groups["1. 税务信用"]
        cols = st.columns(2)
        for i, metric in enumerate(tax_metrics):
            with cols[i % 2]:
                top_data = df.nlargest(top_n, metric)[['企业名称', metric]].copy()
                
                # 格式化处理
                if metric in ["欠税余额", "当期新增欠税金额"]:
                    top_data['显示值'] = top_data[metric] / 10000
                    unit = " (万元)"
                    hover_format = ".2f"
                    text_format = ".2s"
                elif metric == "实缴金额占比":
                    top_data['显示值'] = top_data[metric] * 100
                    unit = " (%)"
                    hover_format = ".1f"
                    text_format = ".1f"
                else:
                    top_data['显示值'] = top_data[metric]
                    unit = ""
                    hover_format = ".1f"
                    text_format = ".2s"
                
                # 对于风险类指标（欠税、滞纳天数），用红色警示
                if metric in ["欠税余额", "当期新增欠税金额", "税款滞纳天数"]:
                    color_scale = "Reds"
                else:
                    color_scale = "Blues"
                
                fig = px.bar(
                    top_data, x='显示值', y='企业名称', orientation='h',
                    title=f"{metric} Top {top_n}{unit}",
                    text='显示值', color='显示值',
                    color_continuous_scale=color_scale
                )
                fig.update_traces(
                    texttemplate=f'%{{text:{text_format}}}',
                    textposition='outside',
                    hovertemplate=f"{metric}: %{{x:{hover_format}}}{unit}<extra></extra>"
                )
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    height=350,
                    margin=dict(l=50, r=30, t=40, b=30),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ---- 法律与合规风险 Tab ----
    with tabs[1]:
        st.markdown("#### 2. 法律与合规风险")
        
        # 违法违章状态分布
        st.markdown("##### 违法违章状态统计")
        illegal_status = df['违法违章状态'].value_counts().reset_index()
        illegal_status.columns = ['状态', '数量']
        fig_status = px.pie(illegal_status, values='数量', names='状态',
                            title='企业违法违章状态分布',
                            color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_status, use_container_width=True)
        
        # 是否发生过红冲/作废异常
        st.markdown("##### 红冲/作废异常发生情况")
        abnormal_count = df['是否发生过红冲/作废异常'].value_counts().reset_index()
        abnormal_count['是否发生过红冲/作废异常'] = abnormal_count['是否发生过红冲/作废异常'].map({0: '否', 1: '是'})
        abnormal_count.columns = ['是否异常', '企业数']
        fig_abnormal = px.bar(abnormal_count, x='是否异常', y='企业数', text='企业数',
                              title='发生过红冲/作废异常的企业数量',
                              color='是否异常')
        fig_abnormal.update_traces(textposition='outside')
        st.plotly_chart(fig_abnormal, use_container_width=True)
        
        # 风险指标条形图
        st.markdown("##### 法律合规风险指标 Top N")
        legal_metrics = groups["2. 法律与合规风险"]
        cols = st.columns(2)
        for i, metric in enumerate(legal_metrics):
            with cols[i % 2]:
                top_data = df.nlargest(top_n, metric)[['企业名称', metric]].copy()
                top_data['显示值'] = top_data[metric]
                
                fig = px.bar(
                    top_data, x='显示值', y='企业名称', orientation='h',
                    title=f"{metric} Top {top_n}",
                    text='显示值', color='显示值',
                    color_continuous_scale="Reds"
                )
                fig.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    hovertemplate=f"{metric}: %{{x}}<extra></extra>"
                )
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    height=350,
                    margin=dict(l=50, r=30, t=40, b=30),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ---- 红冲与作废行为 Tab ----
    with tabs[2]:
        st.markdown("#### 3. 红冲与作废行为")
        red_metrics = groups["3. 红冲与作废行为"]
        cols = st.columns(2)
        for i, metric in enumerate(red_metrics):
            with cols[i % 2]:
                top_data = df.nlargest(top_n, metric)[['企业名称', metric]].copy()
                # 百分比显示
                top_data['显示值'] = top_data[metric] * 100
                fig = px.bar(
                    top_data, x='显示值', y='企业名称', orientation='h',
                    title=f"{metric} Top {top_n} (%)",
                    text='显示值', color='显示值',
                    color_continuous_scale="OrRd"
                )
                fig.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside',
                    hovertemplate=f"{metric}: %{{x:.2f}}%<extra></extra>"
                )
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    height=400,
                    margin=dict(l=50, r=30, t=40, b=30),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # --- 信用综合得分表 (1-100) ---
    with st.expander("📊 查看全部企业 - 信用指标得分表 (百分位数排名，0-100分)"):
        # 定义所有参与评分的指标（不包含分类变量）
        all_metrics = [
            "欠税余额", "当期新增欠税金额", "实缴金额占比", "税款滞纳天数",
            "违法行为数量", "税款状态异常次数", "行政处罚次数",
            "近两年红冲金额占比", "近半年作废金额占比"
        ]
        
        score_df = df[['企业名称']].copy()
        for metric in all_metrics:
            # 负向指标：欠税余额、当期新增欠税、滞纳天数、违法数量、异常次数、案件数、处罚次数、红冲/作废占比
            reverse_metrics = [
                "欠税余额", "当期新增欠税金额", "税款滞纳天数",
                "违法行为数量", "税款状态异常次数", "行政处罚次数",
                "近两年红冲金额占比", "近半年作废金额占比"
            ]
            if metric in reverse_metrics:
                score_df[f'{metric}_得分'] = (
                    (1 - df[metric].rank(pct=True)) * 100
                ).round(0).astype(int)
            else:
                score_df[f'{metric}_得分'] = (
                    df[metric].rank(pct=True) * 100
                ).round(0).astype(int)
        
        # 纳税人信用等级映射为得分
        tax_grade_score = {'A': 100, 'B': 80, 'M': 60, 'C': 40, 'D': 20}
        score_df['纳税人信用等级_得分'] = df['纳税人信用等级'].map(tax_grade_score).fillna(50).astype(int)
        
        # 是否发生过红冲/作废异常（0分表示发生过，100分表示未发生）
        score_df['红冲作废异常_得分'] = df['是否发生过红冲/作废异常'].apply(lambda x: 0 if x == 1 else 100)
        
        # 综合得分：所有得分相加后映射至1-100
        score_cols = [f'{m}_得分' for m in all_metrics] + ['纳税人信用等级_得分', '红冲作废异常_得分']
        raw_sum = score_df[score_cols].sum(axis=1)
        min_sum = raw_sum.min()
        max_sum = raw_sum.max()
        if max_sum > min_sum:
            score_df['信用属性综合得分'] = (1 + 99 * (raw_sum - min_sum) / (max_sum - min_sum)).round(0).astype(int)
        else:
            score_df['信用属性综合得分'] = 50
        
        score_df_sorted = score_df.sort_values('信用属性综合得分', ascending=False)
        
        st.dataframe(
            score_df_sorted,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        st.caption("各指标得分基于百分位数计算（0-100分），负向指标已反转。纳税人信用等级按 A:100、B:80、M:60、C:40、D:20 赋值，红冲/作废异常：发生0分，未发生100分。信用属性综合得分 = 所有指标得分之和线性缩放至1-100区间。")

elif page == "第六页：创新能力分析":
    st.title("6. 创新能力分析")
    
    # --- 指标分组定义 ---
    groups = {
        "1. 知识产权": ["专利数量", "商标数量"],
        "2. 研发投入": ["研发费用", "研发费用占比", "研发费用增长率", "研发人员占比"],
        "3. 技术与产业定位": []  # 分类变量单独处理
    }
    
    # 顶部控件
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 研发投入与知识产权分析")
    with col2:
        top_n = st.slider("选择展示的 Top N 数量", 5, 20, 10, key="innovation_top")
    
    # 选项卡分组展示
    tabs = st.tabs(list(groups.keys()))
    
    # ---- Tab 1: 知识产权 ----
    with tabs[0]:
        st.markdown("#### 1. 知识产权")
        
        # 是否有创新载体分布
        st.markdown("##### 创新载体拥有情况")
        carrier_count = df['是否有创新载体'].value_counts().reset_index()
        carrier_count['是否有创新载体'] = carrier_count['是否有创新载体'].map({0: '无', 1: '有'})
        carrier_count.columns = ['是否有创新载体', '企业数量']
        fig_carrier = px.pie(carrier_count, values='企业数量', names='是否有创新载体',
                             title='拥有创新载体的企业占比',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_carrier, use_container_width=True)
        
        # 专利数量与商标数量 Top N 条形图
        st.markdown("##### 知识产权数量 Top N")
        ip_metrics = groups["1. 知识产权"]
        cols = st.columns(2)
        for i, metric in enumerate(ip_metrics):
            with cols[i % 2]:
                top_data = df.nlargest(top_n, metric)[['企业名称', metric]].copy()
                top_data['显示值'] = top_data[metric]
                
                fig = px.bar(
                    top_data, x='显示值', y='企业名称', orientation='h',
                    title=f"{metric} Top {top_n}",
                    text='显示值', color='显示值',
                    color_continuous_scale="Blues"
                )
                fig.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    hovertemplate=f"{metric}: %{{x}}<extra></extra>"
                )
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    height=350,
                    margin=dict(l=50, r=30, t=40, b=30),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ---- Tab 2: 研发投入 ----
    with tabs[1]:
        st.markdown("#### 2. 研发投入")
        rd_metrics = groups["2. 研发投入"]
        
        cols = st.columns(2)
        for i, metric in enumerate(rd_metrics):
            with cols[i % 2]:
                top_data = df.nlargest(top_n, metric)[['企业名称', metric]].copy()
                
                # 格式化处理
                if metric == "研发费用":
                    top_data['显示值'] = top_data[metric] / 10000
                    unit = " (万元)"
                    hover_format = ".2f"
                    text_format = ".2s"
                elif metric in ["研发费用占比", "研发人员占比", "研发费用增长率"]:
                    top_data['显示值'] = top_data[metric] * 100
                    unit = " (%)"
                    hover_format = ".1f"
                    text_format = ".1f"
                else:
                    top_data['显示值'] = top_data[metric]
                    unit = ""
                    hover_format = ".1f"
                    text_format = ".2s"
                
                # 研发费用增长率可能有负值，用颜色区分
                if metric == "研发费用增长率":
                    colors = ['red' if v < 0 else 'green' for v in top_data[metric]]
                    fig = px.bar(
                        top_data, x='显示值', y='企业名称', orientation='h',
                        title=f"{metric} Top {top_n}{unit}",
                        text='显示值'
                    )
                    fig.update_traces(
                        texttemplate=f'%{{text:{text_format}}}',
                        textposition='outside',
                        marker_color=colors,
                        hovertemplate=f"{metric}: %{{x:{hover_format}}}{unit}<extra></extra>"
                    )
                else:
                    fig = px.bar(
                        top_data, x='显示值', y='企业名称', orientation='h',
                        title=f"{metric} Top {top_n}{unit}",
                        text='显示值', color='显示值',
                        color_continuous_scale="Greens"
                    )
                    fig.update_traces(
                        texttemplate=f'%{{text:{text_format}}}',
                        textposition='outside',
                        hovertemplate=f"{metric}: %{{x:{hover_format}}}{unit}<extra></extra>"
                    )
                
                fig.update_layout(
                    yaxis=dict(autorange="reversed"),
                    height=350,
                    margin=dict(l=50, r=30, t=40, b=30),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ---- Tab 3: 技术与产业定位 ----
    with tabs[2]:
        st.markdown("#### 3. 技术与产业定位")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            # 是否专精特新企业分布
            st.markdown("##### 专精特新企业占比")
            special_count = df['是否专精特新企业'].value_counts().reset_index()
            special_count['是否专精特新企业'] = special_count['是否专精特新企业'].map({0: '否', 1: '是'})
            special_count.columns = ['是否专精特新', '企业数量']
            fig_special = px.pie(special_count, values='企业数量', names='是否专精特新',
                                 title='专精特新企业分布',
                                 color_discrete_sequence=['lightgray', 'gold'])
            st.plotly_chart(fig_special, use_container_width=True)
            
            # 产业链位置分布
            st.markdown("##### 产业链位置分布")
            chain_count = df['产业链位置'].value_counts().reset_index()
            chain_count.columns = ['产业链位置', '企业数量']
            fig_chain = px.bar(chain_count, x='产业链位置', y='企业数量', text='企业数量',
                               title='企业在产业链中的位置', color='产业链位置')
            fig_chain.update_traces(textposition='outside')
            st.plotly_chart(fig_chain, use_container_width=True)
        
        with col_right:
            # 产业规模等级分布
            st.markdown("##### 产业规模等级分布")
            scale_count = df['产业规模等级'].value_counts().reset_index()
            # 按规模顺序排序
            order = ['微型', '小型', '中型', '大型']
            scale_count['产业规模等级'] = pd.Categorical(scale_count['产业规模等级'], categories=order, ordered=True)
            scale_count = scale_count.sort_values('产业规模等级')
            scale_count.columns = ['产业规模等级', '企业数量']
            fig_scale = px.bar(scale_count, x='产业规模等级', y='企业数量', text='企业数量',
                               title='产业规模等级统计', color='产业规模等级')
            fig_scale.update_traces(textposition='outside')
            st.plotly_chart(fig_scale, use_container_width=True)
            
            # 专精特新企业行业分布（旭日图）
            st.markdown("##### 专精特新企业行业分布")
            specialized_df = df[df['是否专精特新企业'] == 1]
            if not specialized_df.empty:
                fig_sunburst = px.sunburst(
                    specialized_df,
                    path=['行业', '产业链位置'],
                    values='专利数量',
                    title='专精特新企业行业与产业链分布',
                    color='专利数量',
                    color_continuous_scale='YlOrRd'
                )
                fig_sunburst.update_layout(height=400)
                st.plotly_chart(fig_sunburst, use_container_width=True)
            else:
                st.info("暂无专精特新企业数据")
    
    # --- 创新能力综合得分表 (1-100) ---
    with st.expander("📊 查看全部企业 - 创新能力指标得分表 (百分位数排名，0-100分)"):
        # 定义所有参与评分的定量指标
        quantitative_metrics = [
            "专利数量", "商标数量",
            "研发费用", "研发费用占比", "研发费用增长率", "研发人员占比"
        ]
        
        score_df = df[['企业名称']].copy()
        for metric in quantitative_metrics:
            # 研发费用增长率可能有负值，但排名法仍然适用（数值越高排名越前）
            score_df[f'{metric}_得分'] = (
                df[metric].rank(pct=True) * 100
            ).round(0).astype(int)
        
        # 分类变量映射得分
        # 是否有创新载体：有=100，无=0
        score_df['创新载体_得分'] = df['是否有创新载体'].apply(lambda x: 100 if x == 1 else 0)
        
        # 是否专精特新企业：是=100，否=0
        score_df['专精特新_得分'] = df['是否专精特新企业'].apply(lambda x: 100 if x == 1 else 0)
        
        # 产业链位置映射（上游=100，中游=70，下游=50）
        chain_score = {'上游': 100, '中游': 70, '下游': 50}
        score_df['产业链位置_得分'] = df['产业链位置'].map(chain_score).fillna(50).astype(int)
        
        # 产业规模等级映射（大型=100，中型=75，小型=50，微型=25）
        scale_score = {'大型': 100, '中型': 75, '小型': 50, '微型': 25}
        score_df['产业规模等级_得分'] = df['产业规模等级'].map(scale_score).fillna(50).astype(int)
        
        # 综合得分
        all_score_cols = [f'{m}_得分' for m in quantitative_metrics] + [
            '创新载体_得分', '专精特新_得分', '产业链位置_得分', '产业规模等级_得分'
        ]
        raw_sum = score_df[all_score_cols].sum(axis=1)
        min_sum = raw_sum.min()
        max_sum = raw_sum.max()
        if max_sum > min_sum:
            score_df['创新能力综合得分'] = (1 + 99 * (raw_sum - min_sum) / (max_sum - min_sum)).round(0).astype(int)
        else:
            score_df['创新能力综合得分'] = 50
        
        score_df_sorted = score_df.sort_values('创新能力综合得分', ascending=False)
        
        st.dataframe(
            score_df_sorted,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        st.caption("定量指标得分基于百分位数计算（0-100分）。分类指标得分规则：创新载体/专精特新：有/是=100，无/否=0；产业链位置：上游=100，中游=70，下游=50；产业规模：大型=100，中型=75，小型=50，微型=25。创新能力综合得分 = 所有指标得分之和线性缩放至1-100区间。")

elif page == "第七页：企业评价模型":
    st.title("7. 企业评价模型")
    
    # 模拟模型得分
    np.random.seed(42)
    model_data = []
    for name in df['企业名称'].head(10): # 取前10个演示
        model_data.append({
            '企业名称': name,
            '企业信用价值评估': np.random.randint(60, 95),
            '企业成长价值评估': np.random.randint(40, 90),
            '企业投资价值分析': np.random.randint(30, 85),
            '企业风险评估': np.random.randint(20, 70) # 风险越低越好
        })
    model_df = pd.DataFrame(model_data)

    # 使用 Tabs 分页展示不同模型
    tab1, tab2, tab3, tab4 = st.tabs(["企业信用价值评估", "企业成长价值评估", "企业投资价值分析", "企业风险评估"])
    
    with tab1:
        st.dataframe(model_df[['企业名称', '企业信用价值评估']].sort_values('企业信用价值评估', ascending=False), use_container_width=True)
    with tab2:
        st.dataframe(model_df[['企业名称', '企业成长价值评估']].sort_values('企业成长价值评估', ascending=False), use_container_width=True)
    with tab3:
        st.dataframe(model_df[['企业名称', '企业投资价值分析']].sort_values('企业投资价值分析', ascending=False), use_container_width=True)
    with tab4:
        st.dataframe(model_df[['企业名称', '企业风险评估']].sort_values('企业风险评估', ascending=True), use_container_width=True) # 风险低在前

elif page == "第八页：企业画像":
    st.title("8. 企业画像")
    
    # 选择企业
    selected_company = st.selectbox("选择企业", df['企业名称'])
    
    # 模拟雷达图数据 (需要归一化处理)
    categories = ['经营规模', '经营情况', '财务状况', '信用属性', '创新能力']
    # 这里基于企业的真实数据做一个简单的加权模拟
    company_row = df[df['企业名称'] == selected_company]
    if not company_row.empty:
        # 简单的模拟逻辑：取几个关键指标的平均分
        values = [
            min(company_row['销售总额'].values[0] / 1e8, 100), # 标准化
            min(company_row['月度开票活跃天数'].values[0], 30),
            min(company_row['净利润'].values[0] / 1e7 + 50, 100) if company_row['净利润'].values[0] > 0 else 30,
            100 - min(company_row['欠税余额'].values[0] / 1e5, 90), # 欠税越少分越高
            min(company_row['专利数量'].values[0] * 2, 100)
        ]
        # 限制在 0-100 之间
        values = [max(0, min(v, 100)) for v in values]
        
        # 创建雷达图
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=selected_company
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title=f"{selected_company} - 企业画像"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示详细数据
        st.subheader("企业详细数据")
        st.dataframe(company_row.T, use_container_width=True)
    else:
        st.warning("未找到企业数据")

# 页脚
st.markdown("---")
st.markdown("© 2026 企业画像系统 | 技术支持：数据分析团队")