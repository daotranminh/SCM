import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

class PdfGenerator:
    def generate(self, 
                 jinja_template_filepath, 
                 template_vars,
                 output_pdf_filepath):
        absolute_jinja_templates_path = os.path.join(os.getcwd(), 'jinja_templates')
        env = Environment(loader=FileSystemLoader(absolute_jinja_templates_path))
        template = env.get_template(jinja_template_filepath)
        html_out = template.render(template_vars)
        HTML(string=html_out).write_pdf(output_pdf_filepath)