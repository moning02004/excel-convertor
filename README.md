### 개요
xlsxwriter 를 이용하여 엑셀을 보다 쉽게 작성할 수 있도록 도와주는 라이브러리입니다.

### 설치
```bash
pip install xlsx-creator
```

### 사용법
```python
from xlsxcreator.excel_convertor import ExcelConverter, get_excel_row

excel_row = get_excel_row(header={"이름": "이름", "휴대폰": "휴대폰", "가입일": "가입일"},
                          body=[{"이름": "홍길동", "휴대폰": "010-1234-5678", "가입일": "2025-01-01"}, ])
ExcelConverter(list(excel_row), buffer="test.xlsx").save()
```