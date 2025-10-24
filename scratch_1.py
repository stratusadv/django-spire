from django.core.wsgi import get_wsgi_application
from markitdown.converters import DocxConverter, HtmlConverter
from markitdown.converter_utils.docx.pre_process import pre_process_docx
import mammoth.transforms
from mammoth import documents

get_wsgi_application()

def transform_paragraph(element):
    new_element = None

    if element.children and not element.style_id:
        for child in element.children:
            if isinstance(child, documents.Run) and isinstance(child.font_size, float):
                if child.font_size >= 20:
                    new_element = element.copy(style_id="Heading1")
                elif 16 > child.font_size > 20:
                    new_element = element.copy(style_id="Heading2")

    return new_element or element


transform_document = mammoth.transforms.paragraph(transform_paragraph)

with open("DOCX_TestPage.docx", "rb") as docx_file:
    preprocessed_docx_stream = pre_process_docx(docx_file)

html_content = mammoth.convert_to_html(
    preprocessed_docx_stream,
    transform_document=transform_document
).value

markdown_content = HtmlConverter().convert_string(html_content).markdown

with open("test_output_new.md", "w", encoding='utf-8') as md_file:
    md_file.write(markdown_content)


