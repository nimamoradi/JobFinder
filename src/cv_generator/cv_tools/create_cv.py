from jinja2 import Template

# --- Corrected Absolute Imports ---
# Assumes the CodeUri in your SAM template is 'src/cv_generator/'
from gen_ai.gemini import AskGemini
from gen_ai.model_names import Flash
from latex.latex_generator import MakeCV

# --- Conditionally Correct Relative Imports ---
# These will only work if the file they are in is part of a package
# (e.g., inside the 'cv_tools' folder)
from .map_to_latex import make_certifications, make_profile_bullet, make_experience_items, create_experience_prompt_text
from .prompt_templates import summary_prompt, job_title_prompt, \
    prompt_profile_summary, prompt_working_experience

def prepare_prompts(gemini, cv, job_description, cv_summary):
    """Prepare all prompts based on the CV data and job description."""
    job_summary = gemini.ask(summary_prompt.format(job_description=job_description))
    job_title = gemini.ask(job_title_prompt.format(job_summary=job_summary, cv_summary=cv_summary))


    profile_prompt = prompt_profile_summary.format(
        job_description=job_description,
        personal=cv.get_value('personal')['description'],
        cv=cv_summary
    )

    work_text_for_prompt = create_experience_prompt_text(cv.get_value('experience_details'))

    work_experience_prompt = Template(prompt_working_experience).render({"experience_details": work_text_for_prompt,
                                                                         "job_description": job_summary}
                                                                        )

    return {
        'job_summary': job_summary,
        'work_experience': work_experience_prompt,
        'job_title': job_title,
        'profile_prompt': profile_prompt
    }


def generate_latex_content(gemini, prompts, cv, include_certs=True):
    """Generate the LaTeX content based on prompts and CV data."""

    # Generate certifications
    cert_text = make_certifications(cv.get_value('certifications')) if include_certs else ''

    # Generate profile bullets
    profile_bullet_list = gemini.ask(prompts['profile_prompt'], False)
    print('Generated profile bullets', profile_bullet_list)
    profile_text = make_profile_bullet(profile_bullet_list)

    # Generate experience bullets
    experience_bullet_list = gemini.ask(prompts['work_experience'], True)
    print('Generated experience bullets', experience_bullet_list[0])
    experience_text = make_experience_items(cv.get_value('experience_details'), experience_bullet_list)
    return cert_text, profile_text, experience_text


def create_cv(cv, job_description, cv_summary, include_certs=True):
    """Main function to generate the CV."""
    gemini = AskGemini(Flash)

    # Step 1: Prepare prompts
    prompts = prepare_prompts(gemini, cv, job_description, cv_summary)


    # ---  Conceptual Example of how to use the prompt with Gemini (assuming you have an 'ask' function for Gemini) ---
    gemini = AskGemini(Flash)

    # Step 2: Generate LaTeX content
    cert_text, profile_text, experience_text = generate_latex_content(gemini, prompts,
                                                                                          cv, include_certs)

    # Step 3: Create LaTeX CV
    maker = MakeCV()
    maker.fill_personal_data(cv.get_value('personal')['name'], cv.get_value('personal')['last_name'],
                             cv.get_value('personal')['location'],
                             cv.get_value('personal')['phone'],
                              cv.get_value('personal')['email'],
                              cv.get_value('personal')['github'],
                              cv.get_value('personal')['linkedin'],
                              prompts['job_title'])
    maker.fill_education(cv.get_value('education'))
    return maker.create(cert_text, profile_text, experience_text)

