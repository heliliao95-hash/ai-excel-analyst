from io import BytesIO
from datetime import datetime

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
	SimpleDocTemplate,
	Paragraph,
	Spacer,
	Table,
	TableStyle,
)


def generate_pdf_report(df):
	buffer = BytesIO()

	pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

	styles = getSampleStyleSheet()

	title_style = ParagraphStyle(
		"ChineseTitle",
		parent=styles["Title"],
		fontName="STSong-Light",
		fontSize=20,
		leading=28,
		alignment=TA_CENTER,
		spaceAfter=20,
	)

	heading_style = ParagraphStyle(
		"ChineseHeading",
		parent=styles["Heading2"],
		fontName="STSong-Light",
		fontSize=13,
		leading=20,
		spaceBefore=12,
		spaceAfter=8,
	)

	normal_style = ParagraphStyle(
		"ChineseNormal",
		parent=styles["Normal"],
		fontName="STSong-Light",
		fontSize=9,
		leading=15,
	)

	doc = SimpleDocTemplate(
		buffer,
		pagesize=A4,
		rightMargin=18 * mm,
		leftMargin=18 * mm,
		topMargin=18 * mm,
		bottomMargin=18 * mm,
	)

	elements = [
		Paragraph("数据分析报告", title_style),
		Paragraph(
			f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
			normal_style,
		),
		Spacer(1, 15),
		Paragraph("一、数据概览", heading_style),
	]

	overview = [
		["指标", "结果"],
		["数据行数", str(len(df))],
		["数据列数", str(len(df.columns))],
		["重复行数", str(int(df.duplicated().sum()))],
		["缺失值数量", str(int(df.isnull().sum().sum()))],
	]

	overview_table = Table(overview, colWidths=[65 * mm, 90 * mm])
	overview_table.setStyle(
		TableStyle(
			[
				("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
				("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
				("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
				("FONTSIZE", (0, 0), (-1, -1), 9),
				("PADDING", (0, 0), (-1, -1), 7),
			]
		)
	)

	elements.extend([overview_table, Spacer(1, 12)])
	elements.append(Paragraph("二、字段信息", heading_style))

	field_data = [["字段名称", "数据类型", "缺失值", "唯一值"]]

	for col in df.columns:
		field_data.append(
			[
				str(col)[:30],
				str(df[col].dtype),
				str(int(df[col].isnull().sum())),
				str(int(df[col].nunique())),
			]
		)

	field_table = Table(field_data, repeatRows=1)
	field_table.setStyle(
		TableStyle(
			[
				("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
				("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
				("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
				("FONTSIZE", (0, 0), (-1, -1), 8),
				("PADDING", (0, 0), (-1, -1), 6),
			]
		)
	)

	elements.extend([field_table, Spacer(1, 12)])
	elements.append(Paragraph("三、描述性统计", heading_style))

	numeric_df = df.select_dtypes(include="number")

	if not numeric_df.empty:
		stats = numeric_df.describe().round(2)

		stats_data = [["统计指标"] + [str(col)[:15] for col in stats.columns]]

		for index, row in stats.iterrows():
			stats_data.append([str(index), *[str(value) for value in row.values]])

		stats_table = Table(stats_data, repeatRows=1)
		stats_table.setStyle(
			TableStyle(
				[
					("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
					("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
					("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
					("FONTSIZE", (0, 0), (-1, -1), 7),
					("PADDING", (0, 0), (-1, -1), 5),
				]
			)
		)

		elements.append(stats_table)
	else:
		elements.append(Paragraph("当前数据没有数值字段。", normal_style))

	elements.append(Spacer(1, 12))
	elements.append(Paragraph("四、数据预览", heading_style))

	preview = df.head(10).fillna("").astype(str)
	preview_data = [[str(col)[:15] for col in preview.columns]]

	for _, row in preview.iterrows():
		preview_data.append([str(value)[:25] for value in row.values])

	preview_table = Table(preview_data, repeatRows=1)
	preview_table.setStyle(
		TableStyle(
			[
				("FONTNAME", (0, 0), (-1, -1), "STSong-Light"),
				("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
				("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
				("FONTSIZE", (0, 0), (-1, -1), 6),
				("PADDING", (0, 0), (-1, -1), 4),
			]
		)
	)

	elements.append(preview_table)

	doc.build(elements)

	buffer.seek(0)
	return buffer.getvalue()
