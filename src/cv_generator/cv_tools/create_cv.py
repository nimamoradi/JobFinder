from pathlib import Path

from jinja2 import Template

# Support both package layouts:
# - CodeUri: src/cv_generator (imports like 'gen_ai.*', 'latex.*')
# - CodeUri: src (imports like 'cv_generator.gen_ai.*', 'cv_generator.latex.*')
try:
    from gen_ai.gemini import escape_latex_in_json
    from gen_ai.llm_interface import LLM_interface
    from gen_ai.model_names import Pro
    from latex.latex_generator import MakeCV
except ModuleNotFoundError:
    from cv_generator.gen_ai.gemini import escape_latex_in_json
    from cv_generator.gen_ai.llm_interface import LLM_interface
    from cv_generator.gen_ai.model_names import Pro
    from cv_generator.latex.latex_generator import MakeCV

from .highlighter import LatexHighlighter
from .map_to_latex import (
    create_experience_prompt_text,
    make_certifications,
    make_experience_items,
    make_profile_bullet,
)
from .prompt_templates import (
    prompt_profile_summary,
    prompt_skills,
    prompt_working_experience,
    summary_prompt,
)

_CONFIG_DIR = Path(__file__).resolve().parents[1] / 'config'


def _load_profile_summary() -> str:
    return (_CONFIG_DIR / 'cv_summary.txt').read_text(encoding='utf-8')


def _normalize_skills(skills_list):
    if isinstance(skills_list, dict):
        return {
            escape_latex_in_json(str(key)): escape_latex_in_json(value)
            for key, value in skills_list.items()
        }

    if isinstance(skills_list, list):
        normalized = {}
        for item in skills_list:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                category = escape_latex_in_json(str(item[0]))
                values = item[1]
                if isinstance(values, list):
                    normalized[category] = escape_latex_in_json(values)
                elif values is None:
                    normalized[category] = []
                else:
                    normalized[category] = [escape_latex_in_json(str(values))]
        return normalized

    return {}


def prepare_prompts(gemini: LLM_interface, cv, job_description):
    """Prepare all prompts based on the CV data and job description."""
    job_summary = gemini.ask(summary_prompt.format(job_description=job_description), True)
    profile_summary = _load_profile_summary()
    job_title = 'Software Engineer'
    skills_prompt = prompt_skills.format(
        my_profile_summary=profile_summary,
        summarized_job_description=job_summary,
        skills=' '.join(cv.get_value('core_skills')),
    )

    profile_prompt = prompt_profile_summary.format(
        job_description=job_description,
        personal=cv.get_value('personal')['description'],
        cv=profile_summary,
    )

    work_text_for_prompt = create_experience_prompt_text(cv.get_value('experience_details'))
    work_experience_prompt = Template(prompt_working_experience).render(
        {
            'experience_details': work_text_for_prompt,
            'job_description': job_summary,
        }
    )

    return {
        'job_summary': job_summary,
        'profile_summary': profile_summary,
        'work_experience': work_experience_prompt,
        'job_title': job_title,
        'skills_prompt': skills_prompt,
        'profile_prompt': profile_prompt,
    }


def generate_latex_content(gemini: LLM_interface, prompts, cv, include_certs=True):
    """Generate the LaTeX content based on prompts and CV data."""
    cert_text = make_certifications(cv.get_value('certifications')) if include_certs else ''

    skills_list = _normalize_skills(gemini.ask(prompts['skills_prompt'], True))

    profile_bullet_list = gemini.ask(prompts['profile_prompt'], False)
    print('Generated profile bullets', profile_bullet_list)
    profile_text = make_profile_bullet(profile_bullet_list)

    gemini.swap_model(Pro)
    experience_bullet_list = gemini.ask(prompts['work_experience'], True)
    if isinstance(experience_bullet_list, list) and experience_bullet_list:
        print('Generated experience bullets', experience_bullet_list[0])
    experience_text = make_experience_items(cv.get_value('experience_details'), experience_bullet_list)

    highlighter = LatexHighlighter(prompts['job_summary'].get('keywords', []))
    profile_text = highlighter.highlight(profile_text)
    experience_text = highlighter.highlight(experience_text)
    return cert_text, profile_text, experience_text, skills_list


def create_cv(cv, job_description, include_certs=True, gemini: LLM_interface = None,
              company_name=None, coverletter=False):
    """Main function to generate the CV LaTeX."""
    if gemini is None:
        raise ValueError('A language model provider must be passed (LLM_interface implementation)')

    prompts = prepare_prompts(gemini, cv, job_description)
    cert_text, profile_text, experience_text, skills_list = generate_latex_content(
        gemini,
        prompts,
        cv,
        include_certs,
    )

    maker = MakeCV()
    maker.fill_personal_data(
        cv.get_value('personal')['name'],
        cv.get_value('personal')['last_name'],
        cv.get_value('personal')['location'],
        cv.get_value('personal')['phone'],
        cv.get_value('personal')['email'],
        prompts['job_title'],
        cv.get_value('personal').get('github', ''),
        cv.get_value('personal').get('linkedin', ''),
    )
    maker.fill_education(cv.get_value('education'))
    return maker.create(
        certifications=cert_text,
        bullet_list=profile_text,
        experience_text=experience_text,
        categorized_skills=skills_list,
    )
