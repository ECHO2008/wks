# pdf_to_word_unoconv.py
import subprocess

def pdf_to_word_unoconv(pdf_path, word_path):
    subprocess.run(['unoconv', '-f', 'docx', '-o', word_path, pdf_path])

# 使用示例
pdfFile = '/Users/echo/Downloads/2015—2016筠连中学期末模拟物理试卷_word.pdf'
pdf_to_word_unoconv(pdfFile, 'output.docx')