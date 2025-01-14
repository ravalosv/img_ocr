from PyPDF2 import PdfReader

def scrapped_data(pdf_path):
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    text = page.extract_text()
    print(text)

if __name__ == '__main__':
    print('Starting PDF Scrapping')
    pdf_path = 'F:\\Mis Proyectos\\git\\python_pdf\\ocr_python\\test.pdf'
    scrapped_data(pdf_path)