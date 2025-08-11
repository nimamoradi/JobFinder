prompt_skills = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes.
Your task is to list additional skills relevant to the job. For each skill, ensure you include:
Do not add any information beyond what is listed in the provided data fields.Use the information provided in the'skills' fields to formulate your responses have them sorted base on importance to role. Avoid extrapolating or incorporating details from the job description or other external sources.

1. **Specific Skills**: List the specific technical skills or technologies from my skills that best match the job do not include soft skills like Communication leadership or etc.
2. **Keyword Matching**: Match the wording of each skill to the job description, ensuring ATS compatibility. If a job description uses different terminology for the same skill (e.g., "Database Administration" instead of "Database Management"), adjust the phrasing to match.
3. **do not make up skills, for example if my skills include Java, do think i know Lua or Rust even if needed for the job.
4. ** keep the skill short, and do not over extend if not needed, for example do not make `C` to `C Programming Language` if you don't have a good reason.
5. ** skills should not be repetative, like no need to include both `Data Processing & Analysis` and `Database Management`
- **Job Description:**  
{summarized_job_description}
- **My skills**:  
  {skills} 
- **Template to Use**
The response should be in json array format without any extra information at most 10 skills sorted with degree of importance
like ["Java", "Kotlin"]
"""

summary_prompt = """
You are a high-precision information extraction engine. Your sole purpose is to parse the following job description and extract specific, actionable information into a structured JSON format. You must adhere to the following rules without exception.

### Core Rules:
1.  **Keyword Integrity:** You MUST use the exact keywords and phrasing from the original text. Do not translate, interpret, or replace terms with synonyms or acronyms. For example, if the text says "database management," you must output "database management," not "DBMS."
2.  **Focus and Exclusion:** Extract ONLY information directly related to the candidate's required skills, day-to-day responsibilities, and qualifications. You MUST ignore all other content, such as company background, mission statements, culture descriptions ('fast-paced environment'), equal opportunity statements, and benefits information.

### Extraction Categories:
- **`technical_skills`**: List all specific technologies, programming languages, frameworks, methodologies (e.g., Agile), and software mentioned.
- **`core_responsibilities`**: List the primary duties and actions the candidate will perform in the role.
- **`qualifications_and_preferences`**: List required or preferred experience, educational background, and other qualifications (e.g., "5+ years of experience," "B.S. in Computer Science," "experience in the financial sector").

### Output Format:
Provide the output as a single, clean JSON object. Do not include any explanatory text before or after the JSON block.

### Job Description to Parse:
{job_description}
"""

is_it_a_match = """
work as a recruiter, and give a mark from 1 to 10 that match my cv Summary knowledge, to job description .higger means better match

for job description: see the skills i have in my cv that are not present in my cv, and tell the skill that are present in both, 

then give a short description of why the match is week or strong
Job Summary:
{job_summary}
cv Summary:
{cv_summary}
"""
prompt_notable_projects = """
Act as an HR expert and resume writer with a specialization in creating ATS-friendly resumes. 
1. Select the most relevant projects from the provided list for the specified job role.
2. Generate concise, impactful bullet points for each selected project that highlight achievements, skills, and responsibilities.
 For each project, we have Project Name, position or rule, period, location and description.
 
 Use the following rules:
- Select at least 2 projects that best match the job description in terms of relevance, required skills, and impact.
- Write 2-3 bullet points for each selected project, focusing on quantifiable achievements and technologies used.
- Do not include extra information beyond the provided project details.
- Use the wording in way that include keywords that match the job description

Ensure that the project descriptions demonstrate your skills and achievements relevant to the job description.

# My Projects: 
  {{projects}}

# Job Summary:
  {{job_description}}

# Output Format:
Provide a JSON array where each object represents a selected project:
[
  {
    "name": "Project Name",
    "position": "Position or Role",
    "location": "Montreal",
    "period": "Dec 2020 - Apr 2021",
    "bullet_points": [
      "Bullet point 1",
      "Bullet point 2",
      ...
    ]
  },
  ...
]
"""

# create profile summary
prompt_profile_summary = """
You are an elite ATS Resume Engineer and professional technical resume writer, known for crafting compelling career narratives that land interviews at top-tier companies. Your primary function is to synthesize a user's career experience and a target job description into a high-impact, persuasive professional summary.

Your process must follow these core principles:

1.  **Grounding:** Adhere strictly to the facts, skills, and experiences provided in the user's CV (`My CV`). Do not invent or embellish information.
2.  **Relevance is Priority:** The summary MUST be laser-focused on the skills and qualifications most critical to the provided `Job Description`.
3.  **Impact Over Tasks:** Do not simply list skills. Instead, showcase skills through their most impressive and quantifiable achievements. The goal is to demonstrate value, not just list keywords.
4.  **Aspirational Alignment:** The summary should conclude with a statement that subtly frames the candidate's ambition in the context of the target role's challenges or mission.

### Generation Process:

1.  **Identify the Core Value Proposition:** Analyze the `Job Description` to identify the top 1-2 most critical needs of the employer (e.g., "scaling infrastructure," "leading cross-functional projects," "improving data pipeline efficiency").
2.  **Extract Quantifiable Achievements:** Scour `My CV` for the most powerful, metrics-driven achievements that directly correspond to the employer's needs identified in Step 1. Look for percentages, dollar amounts, user numbers, or time saved.
3.  **Synthesize the Narrative:** Write a single, dense paragraph that tells a compelling story of the candidate's value.
    * **Sentence 1:** Start with the professional title, years of experience, and a high-level summary of their core expertise, directly mirroring the language in the job description (e.g., "A results-driven Senior Cloud Architect with 8+ years of experience...").
    * **Sentence 2-3:** Seamlessly weave in the top 1-2 *quantifiable achievements* you extracted. Frame them as proof of expertise. For example, instead of saying "experienced in cost optimization," say "proven ability to reduce cloud infrastructure costs, achieving a 25% decrease in annual spending through strategic refactoring."
    * **Sentence 4:** Conclude with a concise, forward-looking statement that connects the candidate's skills to the company's goals. For example: "Eager to apply expertise in scalable systems to build the next generation of [Company's Product/Mission from JD]."

### Strict Constraints:

* **Output Format:** A single paragraph only. **Do not use bullet points.**
* **Tone:** The tone must be confident, professional, and data-driven.
* **Length:** The final paragraph **must be between 3-5 sentences and approximately 60-80 words.**

### Input Data:

- **Job Description**:
{job_description}

- **Years of experience and other info**:
{personal}

- **My CV**:
{cv}

### Output Format:

Provide the paragraph text only, with no additional explanation.
"""

prompt_working_experience = """
You are an expert ATS Resume Engineer and professional technical resume writer. Your primary function is to transform a user's career experience into a high-impact, ATS-optimized list of bullet points, strictly tailored to a specific job description.

Your process must follow these core directives:
1.  **Grounding:** Adhere strictly to the information provided in `My Information`. **Do not invent, embellish, or infer facts.** Your role is to rephrase and strategically present existing information.
2.  **Relevance is Priority:** Your primary goal is to maximize the alignment between the user's experience and the `Job Description`.
3.  **Conciseness and Impact:** All output must be professional, concise, and results-oriented.

### Analysis & Generation Process:

**Step 1: Analyze the Target Job Description**
First, thoroughly analyze the `Job Description`. Identify and prioritize the key skills, technologies, and responsibilities. This analysis will be your guide.

**Step 2: Craft and Order Bullet Points for Each Job**
For **each individual job entry** provided in `My Information`, perform the following:
- **Process Responsibilities:** Process every item from the `key_responsibilities` list and ensure it is a dynamic, results-oriented bullet point.
- **Sort by Relevance:** After processing all points for a job, you **must order the final list of bullet points.** The points that most closely align with the `Job Description` must be at the top, followed by others in descending order of relevance.

**Step 3: Select and Limit for Conciseness**
- After sorting by relevance in Step 2, you **must select only the top 4 most relevant bullet points** for the final output.
- **This is a strict rule** to ensure the final document is concise and fits a single page. Discard all other bullet points for that job entry.

**Step 4: Curate a Focused Skill List**
- From the `skills_acquired` list for the job, create a curated, comma-separated string of the **5-7 most impactful skills** that are most relevant to the `Job Description`.

### Input Data:

- **My Information:**
  {{experience_details}}

- **Job Description:**
  {{job_description}}

### Output Format:

Provide a single JSON array, where each object represents a processed job entry according to the rules above.
[
    {
      "bullet_points": [
        "Most relevant bullet point 1 (aligned with JD)",
        "Most relevant bullet point 2 (aligned with JD)",
        "Less relevant but valuable bullet point 3"
      ],
      "skills": "Key Skill from JD, Another Key Skill, Highly Relevant Skill 1, Highly Relevant Skill 2"
    }
]
"""
whole_cv_summary = """
Summarize the following python data dict file into a concise format that includes:

Work experience, listing position, company, location, time period, and a Summary of key achievements and skills.
Key projects with their name, duration, location, description, and technologies used.
Certifications with names and dates.
A list of core skills.
The output should resemble:

Position at Company, Location, Period, in Area of Work. Summary of key work and skills. 

(Repeat for all experiences.)

Projects include:
- Project Name: Description of project, technologies used.
(Repeat for all projects.)

Certifications: List certifications and their dates.

Core Skills: List of skills.

### Output Format:
should only include the summarized text, no additional explanation.
### Input Dictionary:

{cv_dictionary}

"""
job_title_prompt = """
base on the job description and my profile give a title for my cv, that have the best match if there is no good match 
with my skill give a more general title like `Software Engineer`


Job Summary:
{job_summary}
cv Summary:
{cv_summary}
### Output Format:
should only include the job title and nothing else and extra.
"""
