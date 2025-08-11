from jinja2 import Template
from typing import List, Dict, Any

def fix_latex_special_chars(text):
    """
    Replace special LaTeX characters with their escaped versions.

    Args:
        text (str): Input text containing potential LaTeX special characters

    Returns:
        str: Text with LaTeX special characters properly escaped
    """
    # Dictionary of special characters and their LaTeX equivalents
    special_chars = {
        '#': r'\#',
        '$': r'\$',
        '%': r'\%',
        '&': r'\&',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\~',
        '^': r'\^',
    }

    # Convert the input string into a list of characters
    chars = list(text)
    i = 0

    # Process each character only once
    while i < len(chars):
        if chars[i] in special_chars and (i == 0 or chars[i - 1] != '\\'):
            # Get the replacement string
            replacement = special_chars[chars[i]]

            # Remove the original character
            chars.pop(i)

            # Insert each character of the replacement
            for j, rep_char in enumerate(replacement):
                chars.insert(i + j, rep_char)

            # Skip the inserted replacement
            i += len(replacement)
        else:
            i += 1

    return ''.join(chars)


def generate_skills_latex(skills):
    """
    Generate LaTeX code for skills using the `tasks` environment.

    Parameters:
        skills (list): A list of skill names to include.
        num_columns (int): Number of columns in the `tasks` environment.

    Returns:
        str: LaTeX code as a string.
    """
    # Header for the Skills section
    latex_code = "\n"
    # Add each skill as a task
    for skill in skills:
        latex_code += f"\\item {fix_latex_special_chars(skill)}\n"

    return latex_code


def generate_project_list(projects):
    latex_code = ""
    for project in projects:
        latex_code += f"{generate_project_latex(project)}\n"
    return latex_code


def generate_project_latex(project: dict):
    latex_template = r"""
    \datedexperience{{{name}}}{{{period}}}
        \explanation{{{position}}}{{{location}}} 
        \explanationdetail{{
        \smallskip
        
    {bullets}
        \smallskip
        }}
    """
    # Generate LaTeX for the bullet points
    bullet_template = r"     \coloredbullet\ {content}"
    formatted_bullets = "\n    \smallskip\n\n".join(
        [bullet_template.format(content=bullet) for bullet in project['bullet_points']]
    )

    # Populate the LaTeX template
    return latex_template.format(
        name=project['name'],
        position=project['position'],
        period=project['period'],
        location=project['location'],
        bullets=formatted_bullets
    )


def make_certifications(certs):
    certs_template = r"""
        \bigskip
        \section{Certifications}
        \begin{itemize}
          {{items}}
        \end{itemize}
    """

  # \item AWS Certified Solutions Architect Associate \hfill May 2024

    items_text = ""
    for cert in certs:
        items_text += f"    \\item {cert['name']}"
        items_text += f"    \\hfill {cert['date']}\n"
    return Template(certs_template).render(items=items_text)


def make_profile_bullet(bullets):
    return bullets
    # items_text = ""
    # for bullet in bullets:
    #     items_text += (f"\smallskip\n"
    #                    f"\n\coloredbullet\ {bullet}")
    # return items_text


def sanitize_latex(text: str) -> str:
    """
    Escapes special LaTeX characters in a given string.
    This is crucial for handling text from an LLM.
    """
    replacements = {
        '&': r'\\&',
        '%': r'\\%',
        '$': r'\\$',
        '#': r'\\#',
        '_': r'\\_',
        '{': r'\\{',
        '}': r'\\}',
        '~': r'\\textasciitilde{}',
        '^': r'\\textasciicircum{}',
        '\\': r'\\textbackslash{}',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def make_single_experience(original_experience: Dict[str, Any], tailored_experience: Dict[str, Any]) -> str:
    """
    Generates LaTeX for a single job by merging original (YAML) and tailored (LLM) data.

    Args:
        original_experience: A single job dictionary from your YAML file.
        tailored_experience: The corresponding dict with {'bullet_points', 'skills'} from the LLM.

    Returns:
        A formatted LaTeX string for one job entry.
    """
    # Use the reliable, static data directly from the original YAML object
    company = original_experience.get('company', '')
    period = original_experience.get('employment_period', '')
    position = original_experience.get('position', '')
    location = original_experience.get('location', '')

    latex = f"""\\datedexperience{{{company}}}{{{period}}}
       \\explanation{{{position}}}{{{location}}}
       \\explanationdetail{{
       """

    # Use the tailored bullet points from the LLM response
    for point in tailored_experience.get('bullet_points', []):
        latex += f"""
       \\smallskip
        \\coloredbullet\\ %
        {sanitize_latex(point)}
        """

    # Use the tailored skills string from the LLM response
    skills = tailored_experience.get('skills', '')
    if skills:  # Only add the skills line if skills are present
        latex += f"""
       \\smallskip
        \\skillslearned\\ %
        {sanitize_latex(skills)}
        """

    # Close the explanationdetail section
    latex += "\n     }"
    return latex


def make_experience_items(original_experiences: List[Dict[str, Any]],
                          tailored_experiences: List[Dict[str, Any]]) -> str:
    """
    Creates the full LaTeX block for all work experiences by zipping the two lists.

    Args:
        original_experiences: The full list of jobs from your YAML.
        tailored_experiences: The list of tailored data from the LLM.

    Returns:
        The complete LaTeX string for the work experience section.
    """
    items_text = []

    # Zip the lists together. This assumes the LLM returns tailored data
    # in the exact same order as the jobs you sent in the prompt.
    if len(original_experiences) != len(tailored_experiences):
        print("Warning: Mismatch between number of original jobs and tailored results from LLM.")
        # Handle this error gracefully, maybe by using the shorter list length

    for original_exp, tailored_exp in zip(original_experiences, tailored_experiences):
        items_text.append(make_single_experience(original_exp, tailored_exp))

    return "\n".join(items_text)


def create_experience_prompt_text(experience_list: List[Dict[str, Any]]) -> str:
    """
    Formats a list of job experiences into a clear, structured string
    for the LLM prompt.

    Args:
        experience_list: A list of experience dictionaries from the YAML file.

    Returns:
        A formatted string representing all job experiences.
    """
    prompt_parts = []
    for i, job in enumerate(experience_list):
        # Format responsibilities as a clean bulleted list
        responsibilities_str = "\n".join([f"- {resp}" for resp in job.get('key_responsibilities', [])])

        # Build a block of text for a single job
        job_block = f"""
Job Entry {i}:
Position: {job.get('position', 'N/A')}
Company: {job.get('company', 'N/A')}
Period: {job.get('employment_period', 'N/A')}
Location: {job.get('location', 'N/A')}
Key Responsibilities:
{responsibilities_str}
"""
        prompt_parts.append(job_block)

    # Join all job blocks with a clear separator
    return "\n---\n".join(prompt_parts)
