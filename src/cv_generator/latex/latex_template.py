\
cv_in_latex = r"""
\documentclass{muratcan_cv}
\usepackage{tasks}
\usepackage[scaled]{helvet}
\renewcommand{\familydefault}{\sfdefault}

% Basic information
\setname{ {{ my_name }} }{ {{ my_family }} }
\setposition{ {{ my_position }} }{}
\setaddress{ {{ my_address }} }
\setmobile{ {{ my_phone }} }
\setmail{ {{ my_email }} }

\setlinkedinaccount{ {{ my_linkedin }} }
\setgithubaccount{ {{ my_github }} }
\setthemecolor{MidnightBlue}

\begin{document}

\headerview

\section{Professional Summary}
\explanationdetail{
{{ bullet_list }}
}

\section{Experience}
{{ experience_text }}

{% if categorized_skills %}
\section{Skills}
\explanationdetail{
{% for category, skills_list in categorized_skills.items() %}
\textbf{ {{ category }}:} {{ skills_list | join(', ') }}{% if not loop.last %} \\
{% endif %}
{% endfor %}
}
{% endif %}

\section{Education}
{% for entry in education -%}
\datedexperience{ {{ entry.degree }} }{ {{ entry.dates }} }
\explanation{ {{ entry.institution }} }{ {{ entry.location }} }
\explanationdetail{
    {{ entry.details }}
}
{%- endfor %}

{{ certifications }}

\end{document}
"""

Coverletter_in_latex = r"""

\documentclass[12pt]{letter}
\usepackage[utf8]{inputenc}
\usepackage[empty]{fullpage}
\usepackage[hidelinks]{hyperref}
\usepackage{graphicx}
\usepackage{fontawesome}
\usepackage{eso-pic}
\usepackage{charter}

\addtolength{\topmargin}{-0.5in}
\addtolength{\textheight}{1.0in}
\definecolor{gr}{RGB}{236,236,236}

% Personal information
\newcommand{\myname}{ {{ my_name }} }
\newcommand{\mytitle}{Applicant}
\newcommand{\myemail}{ {{ my_email }} }
\newcommand{\mylinkedin}{ {{ my_linkedin }} }
\newcommand{\myphone}{ {{ my_phone }} }
\newcommand{\mylocation}{ {{ my_address }} }
\newcommand{\recipient}{Hiring Manager}
\newcommand{\greeting}{Dear}
\newcommand{\closer}{Kind Regards}

% Company information
\newcommand{\company}{ {{ the_company }} }

\begin{document}

\AddToShipoutPictureBG{
    \color{gr}
    \AtPageUpperLeft{\rule[-2in]{\paperwidth}{2in}}
}

\begin{center}
{\fontsize{28}{0}\selectfont\scshape \myname}

\href{mailto:\myemail}{\faEnvelope\enspace \myemail}\hfill
\href{https://www.\mylinkedin}{\faLinkedinSquare \mylinkedin}\newline
\href{tel:\myphone}{\faPhone\enspace \myphone}\hfill
\faMapMarker\enspace \mylocation
\end{center}

\vspace{0.2in}

\today\\

\vspace{-0.1in}\recipient\\
\company\\

\vspace{-0.1in}\greeting\ \recipient,\\

\vspace{-0.1in}\setlength\parindent{24pt}
{{ cover_letter_text }}

\vspace{0.1in}
\vfill

\begin{flushright}
\closer,

\vspace{0.4in}

\myname\\
\mytitle
\end{flushright}

\end{document}
"""
