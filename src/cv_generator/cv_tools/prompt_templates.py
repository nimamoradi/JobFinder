prompt_skills = """
Act as an expert resume writer and HR specialist with a deep understanding of Applicant Tracking Systems (ATS).

Your task is to analyze my professional profile and a target job description to generate a categorized list of my most relevant technical skills. The goal is to highlight the best-matching skills in a format that is both human-readable and ATS-optimized.

### Core Rules:
1.  **Analyze All Inputs**: Synthesize information from my `profile_summary`, my `skills` list, and the `job_description` to get a complete picture.
2.  **Categorize Logically**: Group the skills into logical, professional categories such as "Languages," "Platforms," "Databases," "Frameworks," "Tools," or "Concepts."
3.  **Strict Category Limit**: You must generate **3 to 4 categories** in total. Do not create more than 4.
4.  **Prioritize and Sort**: The final output should be sorted by importance. The most relevant category to the job should appear first, and the skills within each category should also be sorted by their relevance.
5.  **No Fabrication**: Only list skills that can be inferred from my profile and skills list. Do not invent skills I don't have, even if they are in the job description.
6.  **Keyword Matching**: Where appropriate, adjust the wording of my skills to match the terminology used in the job description for better ATS compatibility (e.g., use "Cloud Computing" if the job lists it, instead of "Cloud Platforms").
7.  **Be Concise and Unique**: Keep skill names brief (e.g., "C++" not "C++ Programming Language"). Do not list redundant skills (e.g., choose one between "Data Analysis" and "Data Processing" if they represent the same core skill in this context).
8.  **Technical Skills Only**: Do not include soft skills like "Communication," "Teamwork," or "Leadership."

---
### Inputs:
-   **My Profile Summary:**
    {my_profile_summary}
-   **My Skills List:**
    {skills}
-   **Job Description:**
    {summarized_job_description}

---
### Output Format:
Your response **must** be a single clean JSON object. Do not include any text, explanations, or markdown formatting before or after the JSON.

**Example of the required JSON structure:**
{{
    "Platforms": ["AWS", "Google Cloud Platform (GCP)", "Android Development"],
    "Languages": ["Python", "C++", "SQL", "NoSQL"],
    "Concepts": ["Backend Engineering", "REST API", "Database Management"]
}}
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
- **`keywords`**: A prioritized list of the most important keywords/phrases for highlighting. Each item must be an object with fields {{"keyword": string, "importance": integer from 1 to 5}}, where 5 is most important. Use exact keywords from the text.

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

1.  **Analyze Inputs:** Thoroughly analyze the `Job Description` to identify the most critical qualifications. Simultaneously, review `My CV` to find the strongest corresponding achievements and skills.
2.  **Craft the Summary:** Write a single, dense paragraph that powerfully introduces the candidate.
    * It should start by stating the candidate's professional title and years of experience.
    * It must seamlessly weave in the top 2-3 skills or achievements that are most relevant to the job description (e.g., "architecting a cloud gaming platform," "AWS serverless architecture," "Android SDK").
    * Mention top-tier, relevant certifications if applicable.
3.  **Apply Strict Constraints:**
    * **Output Format:** A single paragraph only. **Do not use bullet points.**
    * **Length:** The final paragraph **must be between 2-4 sentences and strictly under 60 words.**

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
      ]
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
