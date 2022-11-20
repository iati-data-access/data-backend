from pyexcelerate import Workbook
from io import BytesIO

def generate_xlsx(data):
    output = BytesIO()
    wb = Workbook()
    data_list = [list(data[0].keys())]+[row.values() for row in data]
    wb.new_sheet("Data", data=data_list)
    wb.save(output)
    output.seek(0)
    return output