import json
import sys
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

def pdf_to_text(path):
    resource_manager = PDFResourceManager()
    text_output = StringIO()
    laparams = LAParams()
    device = TextConverter(resource_manager, text_output, laparams=laparams)

    with open(path, 'rb') as file:
        interpreter = PDFPageInterpreter(resource_manager, device)
        for page in PDFPage.get_pages(file):
            interpreter.process_page(page)

    text = text_output.getvalue()
    text_output.close()
    return text

def parse_questions(data):
    questions = []
    lines = data.split('\n')
    question_data = {}
    is_question = False
    is_explain = False
    for line in lines:
        line = line.strip()
        if line.startswith('Q'):
            if question_data:
                questions.append(question_data)
                question_data = {}
                is_explain = False
            question_data['No'] = line.split('.')[0].strip()
            is_question = True
            question_data['Question'] = line.split('.')[1].strip()
        elif is_question and not line.startswith('A.'):
            if 'Question' in question_data:
                question_data['Question'] += ' ' + line.strip()
            else:
                question_data['Question'] = line.strip()
        elif line.startswith('A.'):
            is_question = False
            question_data['OptionA'] = line[2:].strip()
        elif line.startswith('B.'):
            question_data['OptionB'] = line[2:].strip()
        elif line.startswith('C.'):
            question_data['OptionC'] = line[2:].strip()
        elif line.startswith('D.'):
            question_data['OptionD'] = line[2:].strip()
        elif line.startswith('答案:'):
            question_data['Answer'] = line[3:].strip()
        elif line.startswith('解析:'):
            is_explain = True
            if len(line) > 3:
                question_data['Explain'] = line[3:].strip()
        elif is_explain:
            if 'Explain' in question_data:
                question_data['Explain'] += ' ' + line.strip()
            else:
                question_data['Explain'] = line.strip()
    if question_data:
        questions.append(question_data)
    return questions

def save_as_json(questions, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(questions, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python script.py <input_pdf_path> <output_json_path>')
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    output_json_path = sys.argv[2]

    text_data = pdf_to_text(input_pdf_path)
    parsed_questions = parse_questions(text_data)
    save_as_json(parsed_questions, output_json_path)
