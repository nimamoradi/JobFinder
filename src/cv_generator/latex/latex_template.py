cv_in_latex = r"""
\documentclass{muratcan_cv}
\usepackage{tasks}
\setname^^; {{ my_name }} ^^= ^^; {{ my_family }} ^^=
\setposition^^; {{ my_position }} ^^={}
\setaddress^^; {{ my_address }} ^^=
\setmobile^^; {{ my_phone }} ^^=
\setmail^^; {{ my_email }} ^^=

\setlinkedinaccount^^; {{ my_linkedin }} ^^=
\setgithubaccount^^; {{ my_github }} ^^=
\setthemecolor{MidnightBlue}

    
\begin{document}

%Create header
\headerview
\vspace{1ex} % white space
%
\section{Career Summary} 
\explanationdetail{\hspace{2ex}
 {{bullet_list}}
\bigskip
}
   

\section{Experience}
    {{experience_text}} 
%

% 

\section{Education} 
{% for entry in education -%}
  \datedexperience^^;{{ entry.degree }}^^=^^;{{ entry.dates }}^^=
    \explanation^^;{{ entry.institution }}^^=^^;{{ entry.location }}^^=
    \explanationdetail^^;
            {{ entry.details }}
^^=
{%- endfor %}

{{certifications}}
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
\newcommand{\myname}^^; {{ my_name }} ^^=
\newcommand{\mytitle}{Applicant}
\newcommand{\myemail}^^; {{ my_email }} ^^=
\newcommand{\mylinkedin}^^; {{ my_linkedin }} ^^=
\newcommand{\myphone}^^; {{ my_phone }} ^^=
\newcommand{\mylocation}^^; {{ my_address }} ^^=
\newcommand{\recipient}{Hiring Manager}
\newcommand{\greeting}{Dear}
\newcommand{\closer}{Kind Regards}

% Company information
\newcommand{\company}^^; {{ the_company }} ^^=


\begin{document}

% Shaded header banner
\AddToShipoutPictureBG{
    \color{gr}
    \AtPageUpperLeft{\rule[-2in]{\paperwidth}^^;2in^^=}
}

% Header
\begin{center}
{\fontsize{28}{0}\selectfont\scshape \myname}

\href{mailto:\myemail}{\faEnvelope\enspace \myemail}\hfill
\href{https://linkedin.com/in/\mylinkedin}{\faLinkedinSquare linkedin.com/in/\mylinkedin}\newline
\href{tel:\myphone}{\faPhone\enspace \myphone}\hfill
\faMapMarker\enspace \mylocation
\end{center}

\vspace{0.2in}

% Opening block
\today\\

\vspace{-0.1in}\recipient\\
\company\\

\vspace{-0.1in}\greeting\ \recipient,\\

% Body
\vspace{-0.1in}\setlength\parindent{24pt}
{{cover_letter_text}}

% Closer
\vspace{0.1in}
\vfill

\begin{flushright}
\closer,

\vspace{-0.1in}\includegraphics[width=1.5in]{signature.png}\vspace{-0.1in}

\myname\\
\mytitle
\end{flushright}

\end{document}
"""
