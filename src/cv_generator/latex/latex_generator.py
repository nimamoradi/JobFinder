from jinja2 import Template

# Support both package layouts:
# - CodeUri: src/cv_generator (imports like 'latex.*')
# - CodeUri: src (imports like 'cv_generator.latex.*')
try:
    from latex.latex_template import cv_in_latex, Coverletter_in_latex
except ModuleNotFoundError:
    from cv_generator.latex.latex_template import cv_in_latex, Coverletter_in_latex


class MakeCV:
    def __init__(self):
        self.template = Template(cv_in_latex)
        self.values_dict = {}

    def fill_personal_data(self, name, last_name, address, phone, email, my_position, github='', linkedin=''):
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

    def create(self, certifications, bullet_list, experience_text, categorized_skills=None, projects=None):
        return self.template.render(
            self.values_dict
            | {
                'certifications': certifications,
                'bullet_list': bullet_list,
                'experience_text': experience_text,
                'categorized_skills': categorized_skills or {},
                'projects': projects or [],
            }
        )


class MakeCoverLetter:
    def __init__(self):
        self.template = Template(Coverletter_in_latex)
        self.values_dict = {}

    def fill_personal_data(self, name, address, phone, email, linkedin=''):
        self.values_dict['my_name'] = name
        self.values_dict['my_address'] = address
        self.values_dict['my_phone'] = phone
        self.values_dict['my_email'] = email
        self.values_dict['my_linkedin'] = linkedin

    def create(self, cover_letter_text, company_name):
        return self.template.render(
            self.values_dict | {'cover_letter_text': cover_letter_text, 'the_company': company_name}
        )
