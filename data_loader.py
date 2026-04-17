# data_loader.py
import pandas as pd
import numpy as np

def load_simulated_data(n=50):
    """
    加载或生成模拟的企业数据。
    """
    np.random.seed(42)
    data = {
        '企业名称': [f'企业_{i}' for i in range(n)],
        '行业': np.random.choice(['制造业', '信息技术', '批发零售', '科学研究'], n),
        '省份': np.random.choice(['广东', '江苏', '浙江', '江西', '上海'], n),
        '企业年龄': np.random.randint(1, 31, n),
        '人员规模': np.random.randint(10, 5000, n),
        '注册资金': np.random.randint(100, 10000, n) * 10000, # 100万-10亿
        '资质': np.random.choice(
            ['高新技术企业', '专精特新企业', '普通企业'],
            n,
            p=[0.25, 0.15, 0.6]  # 确保无空值
        ),
        
        # 经营规模数据
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
        '月度开票活跃天数': np.random.randint(10, 30, n),
        '近一年开票月份数': np.random.randint(0, 12, n),
        '连续无交易天数': np.random.randint(0, 100, n),
        '供应商集中度': np.random.rand(n),
        '大客户依赖度': np.random.rand(n),

        # 财务数据
        '营业收入': np.random.randint(100, 20000, n) * 10000,
        '净利润': np.random.randint(-1000, 5000, n) * 10000, # 可能亏损
        '毛利率': np.random.rand(n),
        '资产负债率': np.random.rand(n),

        # 信用数据
        '纳税人信用等级': np.random.choice(['A', 'B', 'M', 'C', 'D'], n),
        '欠税余额': np.random.randint(0, 1000000, n),
        '行政处罚次数': np.random.randint(0, 5, n),
        '司法案件数': np.random.randint(0, 10, n),

        # 创新数据
        '专利数量': np.random.randint(0, 100, n),
        '研发费用': np.random.randint(0, 5000, n) * 10000,
        '研发人员占比': np.random.rand(n),
        '是否专精特新企业': np.random.choice([0, 1], n, p=[0.8, 0.2])
    }
    return pd.DataFrame(data)

# 全局加载数据
df = load_simulated_data()