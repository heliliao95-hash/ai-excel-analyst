import pandas as pd

from report_utils import generate_pdf_report


def test_generate_pdf_report():
	df = pd.DataFrame({
		"产品": ["电脑", "手机", "平板"],
		"销售额": [12000, 8000, 5000],
		"销售数量": [3, 5, 2],
	})

	result = generate_pdf_report(df)

	assert isinstance(result, bytes)
	assert result.startswith(b"%PDF")
	assert len(result) > 0


def test_generate_pdf_report_with_missing_values():
	df = pd.DataFrame({
		"产品": ["电脑", None, "平板"],
		"销售额": [12000, None, 5000],
	})

	result = generate_pdf_report(df)

	assert result.startswith(b"%PDF")


def test_generate_pdf_report_without_numeric_columns():
	df = pd.DataFrame({"产品": ["电脑", "手机", "平板"]})

	result = generate_pdf_report(df)

	assert result.startswith(b"%PDF")
