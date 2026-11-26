
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from report_utils import generate_pdf_report

load_dotenv(Path(__file__).resolve().parent / ".env")

st.set_page_config(
    page_title="AI Excel 数据分析助手",
    page_icon="📊",
    layout="wide"
)

st.title("AI Excel 数据分析助手")
st.caption("Excel 数据清洗、统计分析与智能问答")

uploaded_file = st.sidebar.file_uploader(
    "上传 CSV 或 Excel 文件",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is None:
    st.info("请上传 CSV 或 Excel 文件开始分析。")
    st.stop()

try:
    if uploaded_file.name.lower().endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="gbk")
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"文件读取失败：{e}")
    st.stop()

df = df.dropna(axis=1, how="all")

if df.empty or len(df.columns) == 0:
    st.warning("文件中没有有效数据。")
    st.stop()

st.header("一、数据概览")

c1, c2, c3, c4 = st.columns(4)
c1.metric("数据行数", len(df))
c2.metric("数据列数", len(df.columns))
c3.metric("重复行数", int(df.duplicated().sum()))
c4.metric("缺失值", int(df.isnull().sum().sum()))

st.dataframe(df.head(100), use_container_width=True)

st.header("二、数据质量检测")

quality_df = pd.DataFrame({
    "数据类型": df.dtypes.astype(str),
    "缺失值数量": df.isnull().sum(),
    "缺失率(%)": (df.isnull().mean() * 100).round(2),
    "唯一值数量": df.nunique()
})

st.dataframe(quality_df, use_container_width=True)

st.header("三、数据清洗")

missing_method = st.selectbox(
    "缺失值处理方式",
    [
        "保留缺失值",
        "删除含缺失值的行",
        "数值列使用均值填充",
        "数值列使用中位数填充",
        "使用众数填充"
    ]
)

clean_df = df.copy()

if missing_method == "删除含缺失值的行":
    clean_df = clean_df.dropna()

elif missing_method == "数值列使用均值填充":
    for col in clean_df.select_dtypes(include="number").columns:
        if clean_df[col].notna().any():
            clean_df[col] = clean_df[col].fillna(clean_df[col].mean())

elif missing_method == "数值列使用中位数填充":
    for col in clean_df.select_dtypes(include="number").columns:
        if clean_df[col].notna().any():
            clean_df[col] = clean_df[col].fillna(clean_df[col].median())

elif missing_method == "使用众数填充":
    for col in clean_df.columns:
        modes = clean_df[col].mode(dropna=True)
        if not modes.empty:
            clean_df[col] = clean_df[col].fillna(modes.iloc[0])

if st.checkbox("删除重复行", value=True):
    clean_df = clean_df.drop_duplicates()

st.metric("清洗后数据行数", len(clean_df))
st.dataframe(clean_df.head(100), use_container_width=True)

st.download_button(
    "下载清洗后的 CSV",
    data=clean_df.to_csv(index=False, encoding="utf-8-sig"),
    file_name="cleaned_data.csv",
    mime="text/csv"
)

st.header("四、统计分析")

numeric_df = clean_df.select_dtypes(include="number")

if not numeric_df.empty:
    st.dataframe(numeric_df.describe().T, use_container_width=True)
else:
    st.info("当前数据没有数值字段。")

st.header("五、数据可视化")

if not numeric_df.empty:
    numeric_col = st.selectbox(
        "选择数值字段",
        numeric_df.columns.tolist()
    )

    category_cols = clean_df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    if category_cols:
        category_col = st.selectbox(
            "选择分类字段",
            category_cols
        )

        chart_data = clean_df[[category_col, numeric_col]].dropna()

        grouped = (
            chart_data.groupby(category_col)[numeric_col]
            .sum()
            .reset_index()
            .sort_values(numeric_col, ascending=False)
        )

        if not grouped.empty:
            fig = px.bar(
                grouped,
                x=category_col,
                y=numeric_col,
                title=f"{numeric_col} 分类统计"
            )
            st.plotly_chart(fig, use_container_width=True)

            pie_fig = px.pie(
                grouped.head(10),
                names=category_col,
                values=numeric_col,
                title=f"{numeric_col} 分类占比"
            )
            st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("没有可用于分类统计的字段。")

st.header("六、AI 智能问答")

api_key = os.getenv("DASHSCOPE_API_KEY")
base_url = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")

if "ai_call_count" not in st.session_state:
    st.session_state.ai_call_count = 0

st.caption(f"本次会话调用次数：{st.session_state.ai_call_count}/10")

question = st.text_area(
    "请输入数据分析问题",
    max_chars=500,
    placeholder="例如：哪个产品销售额最高？"
)

if st.button("AI 开始分析", type="primary"):
    if not api_key:
        st.error("请检查 .env 中的 API Key。")
    elif not question.strip():
        st.warning("请先输入问题。")
    elif st.session_state.ai_call_count >= 10:
        st.error("本次会话调用次数已达到上限。")
    else:
        summary = [
            f"数据行数：{len(clean_df)}",
            f"字段名称：{', '.join(map(str, clean_df.columns))}",
            f"缺失值：{int(clean_df.isnull().sum().sum())}",
            f"重复行：{int(clean_df.duplicated().sum())}"
        ]

        if not numeric_df.empty:
            summary.append(
                numeric_df.describe().round(2).to_string()
            )

        for col in clean_df.select_dtypes(exclude="number").columns[:8]:
            summary.append(
                f"{col}类别统计：\n"
                f"{clean_df[col].value_counts().head(10).to_string()}"
            )

        try:
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=30,
                max_retries=0
            )

            with st.spinner("正在分析..."):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "你是一名专业的数据分析师。"
                                "请根据数据摘要回答问题，不要编造数据。"
                                "使用中文，给出清晰的分析结论。"
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                "\n".join(summary)[:12000]
                                + "\n用户问题："
                                + question
                            )
                        }
                    ],
                    temperature=0.3,
                    max_tokens=500
                )

            st.session_state.ai_call_count += 1
            st.subheader("AI 分析结果")
            st.markdown(response.choices[0].message.content or "暂无回答")

        except Exception as e:
            st.error(f"AI 调用失败：{e}")

st.header("七、报告导出")

try:
    pdf_data = generate_pdf_report(clean_df)

    st.download_button(
        "下载 PDF 分析报告",
        data=pdf_data,
        file_name="analysis_report.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"PDF 报告生成失败：{e}")

st.divider()
st.caption("AI Excel 数据分析助手")
