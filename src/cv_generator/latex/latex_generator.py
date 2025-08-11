import os
import subprocess

from jinja2 import Template

from latex.latex_template import cv_in_latex, Coverletter_in_latex


def cleanup_aux_files(latex_file):
    base_filename = os.path.splitext(latex_file)[0]
    extensions = ['.aux', '.log', '.toc', '.out', '.nav', '.snm', '.bbl', '.blg', 'tex']
    for ext in extensions:
        try:
            os.remove(base_filename + ext)
        except FileNotFoundError:
            pass


class MakeCV:
    def __init__(self):
        # Create a Template instance
        self.template = Template(cv_in_latex)
        self.values_dict = {}

    def fill_personal_data(self, name, last_name,  address, phone, email, my_position, github, linkedin):
        self.values_dict['my_name'] = name
        self.values_dict['my_family'] = last_name
        self.values_dict['my_address'] = address
        self.values_dict['my_phone'] = phone
        self.values_dict['my_email'] = email
        self.values_dict['my_position'] = my_position
        self.values_dict['my_github'] = github
        self.values_dict['my_linkedin'] = linkedin

    def fill_education(self, education):
        self.values_dict['education'] = education

    def create(self, certifications, bullet_list, experience_text):
        # Render the template with the context
        return self.template.render(
            self.values_dict | {'certifications': certifications,
                                'bullet_list': bullet_list, 'experience_text': experience_text})

