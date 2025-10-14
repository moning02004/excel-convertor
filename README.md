### 개요
xlsxwriter 를 이용하여 엑셀을 보다 쉽게 작성할 수 있도록 도와주는 라이브러리입니다.
헤더 및 스타일 등을 간단히 지정할 수 있습니다.

### 설치
```bash
pip install xlsx-creator
```

### 사용법
- header 의 key 를 기준으로 데이터를 가공하여 엑셀로 저장합니다. `save_to` 를 string 으로 지정하면 `./output` 디렉터리 아래 파일이 저장됩니다.
- 셀 너비는 텍스트 길이에 따라 자동으로 늘어나지만, 완벽하게 최적으로 설정되지는 않습니다. 따라서 엑셀의 자동 조정기능을 통해 너비를 조정해야 합니다.

```python
from xlsxcreator.excel_convertor import ExcelConvertor

if __name__ == '__main__':
    convertor = ExcelConvertor(save_to="test")
    convertor.header = {"이름": "이름",
                        "휴대폰": "휴 대 폰",
                        "가입일": "가입일"}
    convertor.cell_styles = {"휴대폰": {"num_format": "@"}}
    convertor.cell_comments = {"휴대폰": "- 를 제거한 후 입력해주세요."}

    excel_body = list()
    for x in range(1, 100):
        excel_body.append({"이름": f"홍길동{x}", "휴대폰": f"0101234567{x:02d}", "가입일": "2025-01-01"})
    convertor.body = excel_body
    convertor.save()
```

- 버퍼에 저장하여 다운로드 기능을 제공하거나 파일 업로드 등 다양하게 활용할 수도 있습니다.
```python
from io import BytesIO

from xlsxcreator.excel_convertor import ExcelConvertor
from django.http import HttpResponse

if __name__ == '__main__':
    buffer = BytesIO()
    convertor = ExcelConvertor(save_to=buffer)
    convertor.header = {"이름": "이름",
                        "휴대폰": "휴 대 폰",
                        "가입일": "가입일"}
    convertor.cell_styles = {"휴대폰": {"num_format": "@"}}
    convertor.cell_comments = {"휴대폰": "- 를 제거한 후 입력해주세요."}

    excel_body = list()
    for x in range(1, 100):
        excel_body.append({"이름": f"홍길동{x}", "휴대폰": f"0101234567{x:02d}", "가입일": "2025-01-01"})
    convertor.body = excel_body
    convertor.save()

    # 다운로드 응답
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
    return response
```