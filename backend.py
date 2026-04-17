# backend.py
from fastapi import HTTPException
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from data_loader import df

app = FastAPI(title="企业画像 API", version="1.0.0")

# Pydantic 模型用于请求和响应体
class Company(BaseModel):
    企业名称: str
    行业: str
    省份: str
    企业年龄: int
    人员规模: int
    资质: str  # ✅ 注意：这里是 '资质'
    注册资金: float
    销售总额: float
    实收资本: float
    资产总额: float
    近两年开票总金额: float
    近两年开票总份数: int
    近两年客户总数: int
    近两年月均开票金额: float
    实际经营月份数: int
    分支机构数量: int
    月度开票活跃天数: int
    近一年开票月份数: int
    连续无交易天数: int
    供应商集中度: float
    大客户依赖度: float
    营业收入: float
    净利润: float
    毛利率: float
    资产负债率: float
    纳税人信用等级: str
    欠税余额: float
    行政处罚次数: int
    司法案件数: int
    专利数量: int
    研发费用: float
    研发人员占比: float
    是否专精特新企业: int

class ModelScore(BaseModel):
    企业名称: str
    企业信用价值评估: float
    企业成长价值评估: float
    企业投资价值分析: float
    企业风险评估: float

@app.get("/")
def read_root():
    return {"message": "欢迎访问企业画像系统 API"}

@app.get("/companies/", response_model=List[Company])
def get_companies(limit: Optional[int] = Query(50, description="返回记录数")):
    """
    获取企业列表
    """
    return df.head(limit).to_dict(orient='records')

@app.get("/company/{company_name}", response_model=Company)
def get_company_detail(company_name: str):
    """
    获取特定企业的详细信息
    """
    result = df[df['企业名称'] == company_name]
    if result.empty:
        raise HTTPException(status_code=404, detail="Company not found")

    return result.iloc[0].to_dict()

@app.get("/analysis/{metric}/top/{n}", response_model=List[dict])
def get_top_n_companies_by_metric(metric: str, n: int):
    """
    获取某项指标排名前N的企业
    """
    if metric not in df.columns:
        raise HTTPException(status_code=400, detail="Invalid metric")
    top_n_df = df.nlargest(n, metric)[['企业名称', metric]].rename(columns={metric: 'value'})
    return top_n_df.to_dict(orient='records')

@app.get("/distribution/{dimension}", response_model=List[dict])
def get_distribution(dimension: str):
    """
    获取某个维度的分布情况 (如行业、省份、信用等级)
    """
    if dimension not in df.columns:
        raise HTTPException(status_code=400, detail="Invalid dimension")
    dist_df = df[dimension].value_counts().reset_index()
    dist_df.columns = [dimension, 'count']
    return dist_df.to_dict(orient='records')

@app.get("/model_scores/", response_model=List[ModelScore])
def get_model_scores(limit: Optional[int] = Query(10, description="返回记录数")):
    """
    获取企业模型评估分数 (模拟)
    """
    import numpy as np
    companies = df.head(limit)['企业名称'].tolist()
    scores = []
    for name in companies:
        scores.append({
            '企业名称': name,
            '企业信用价值评估': np.random.randint(60, 95),
            '企业成长价值评估': np.random.randint(40, 90),
            '企业投资价值分析': np.random.randint(30, 85),
            '企业风险评估': np.random.randint(20, 70)
        })
    return scores

@app.get("/radar_data/{company_name}", response_model=List[dict])
def get_radar_data(company_name: str):
    """
    获取特定企业的雷达图数据
    """
    company_row = df[df['企业名称'] == company_name]
    if company_row.empty:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # 简单的模拟逻辑
    values = [
        min(company_row['销售总额'].iloc[0] / 1e8, 100),
        min(company_row['月度开票活跃天数'].iloc[0], 30),
        min(company_row['净利润'].iloc[0] / 1e7 + 50, 100) if company_row['净利润'].iloc[0] > 0 else 30,
        100 - min(company_row['欠税余额'].iloc[0] / 1e5, 90),
        min(company_row['专利数量'].iloc[0] * 2, 100)
    ]
    values = [max(0, min(v, 100)) for v in values]
    categories = ['经营规模', '经营情况', '财务状况', '信用属性', '创新能力']
    
    return [{'dimension': cat, 'score': val} for cat, val in zip(categories, values)]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)