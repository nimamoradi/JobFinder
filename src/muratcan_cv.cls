% Created by Murat Can Karacabey
% Parsing-friendly variant adjusted by OpenAI
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{muratcan_cv}[2026/03/08 Parsing-friendly CV class]
\author{Original template authors}
\RequirePackage[dvipsnames]{xcolor}
\LoadClass[11pt]{article}
\RequirePackage{iftex}

% Engine-aware text extraction helpers.
% - pdfLaTeX: use ToUnicode maps.
% - XeLaTeX/LuaLaTeX: avoid pdfTeX-only commands and keep Unicode text searchable.
\ifPDFTeX
  \RequirePackage[T1]{fontenc}
  \input glyphtounicode.tex
  \pdfgentounicode=1
  % Normalize punctuation that often breaks ATS/parsers.
  \DeclareUnicodeCharacter{2011}{-}% non-breaking hyphen
  \DeclareUnicodeCharacter{2013}{-}% en dash
  \DeclareUnicodeCharacter{2014}{-}% em dash
  \DeclareUnicodeCharacter{00A0}{\space}% no-break space
  \DeclareUnicodeCharacter{2019}{\textquotesingle}% right single quote
\else
  \RequirePackage{newunicodechar}
  \newunicodechar{‑}{-}% non-breaking hyphen
  \newunicodechar{–}{-}% en dash
  \newunicodechar{—}{-}% em dash
  \newunicodechar{ }{\space}% no-break space
  \newunicodechar{’}{\textquotesingle}% right single quote
  \ifXeTeX
    \ifdefined\XeTeXgenerateactualtext
      \XeTeXgenerateactualtext=1
    \fi
  \fi
  \ifLuaTeX
    \ifdefined\pdfvariable
      \pdfvariable gentounicode 1\relax
    \fi
  \fi
\fi

\RequirePackage[sfdefault]{noto}
\RequirePackage{etoolbox}
\RequirePackage{pgffor}
\RequirePackage{titlesec}
\RequirePackage{tikz}
\RequirePackage{courier}
\RequirePackage[left=0.5in,top=0.4in,right=0.5in,bottom=0.4in]{geometry}
\RequirePackage{hyperref}
\RequirePackage{mfirstuc}
\RequirePackage{ifthen}
\RequirePackage{lipsum}
\RequirePackage{array}
\RequirePackage{enumitem}
\RequirePackage{changepage}
\RequirePackage{comment}
\pagestyle{empty}

\newlength{\gridindent}
\setlength{\gridindent}{0.5em}

% Prevent hyphenated word breaks that confuse text extractors.
\hyphenpenalty=10000
\exhyphenpenalty=10000
\emergencystretch=2em

% On XeLaTeX/LuaLaTeX, force a real sans font even if the document later loads helvet.
\AtBeginDocument{%
  \ifPDFTeX\else
    \ifdefined\setsansfont
      \setsansfont{Noto Sans}
      \renewcommand\familydefault{\sfdefault}
    \fi
  \fi
}

% Setup
\newcommand{\sizeLargest}[1]{{\fontsize{20pt}{23pt}\selectfont\bfseries #1}}
\newcommand{\sizeSecond}[1]{{\fontsize{12pt}{14pt}\selectfont\bfseries #1}}
\newcommand{\sizeThird}[1]{{\fontsize{10pt}{12pt}\selectfont #1}}
\newcommand{\sizeThirdBold}[1]{{\fontsize{10pt}{12pt}\selectfont\bfseries #1}}

\newcommand*{\setname}[2]{\def\@firstname{#1}\def\@lastname{#2}}
\newcommand*{\setaddress}[1]{\def\@address{#1}}
\newcommand*{\setmobile}[1]{\def\@mobile{#1}}
\newcommand*{\setposition}[2]{\def\@position{#1}}
\newcommand*{\setmail}[1]{\def\@mail{#1}}
\newcommand*{\setcitizenship}[1]{\def\@citizenship{#1}}
\newcommand*{\setthemecolor}[1]{\def\@themecolor{#1}}
\newcommand*{\setlinkedinaccount}[1]{\def\@linkedinaccount{#1}}
\newcommand*{\setgithubaccount}[1]{\def\@githubaccount{#1}}

\hypersetup{hidelinks,pdfborder={0 0 0},urlcolor=NavyBlue}
\urlstyle{same}

\newcommand{\linkedinview}{\href{https://www.\@linkedinaccount}{\@linkedinaccount}}
\newcommand{\githubview}{\href{https://www.\@githubaccount}{\@githubaccount}}

\newcommand{\name}{{\color{\@themecolor}\sizeLargest{\@firstname\ \@lastname}}}
\newcommand{\cvTitle}{{\sizeSecond{\MakeUppercase{\@position}}}}

% Header
\newcommand\headerview{%
\begin{center}
    {\name}\par\vspace{1.5ex}
    {\cvTitle}\par\vspace{1ex}
    {\sizeThird{\href{mailto:\@mail}{\@mail} | \linkedinview}}\par\vspace{0.5ex}
    {\sizeThird{\githubview{} | \@address | \@mobile}}
\end{center}
}

\newcommand{\datetext}[1]{{\footnotesize\mdseries\color{black}\sizeThirdBold{#1}}}
\newcommand{\datetextbold}[1]{{\footnotesize\mdseries\color{black}\sizeThirdBold{#1}}}

% Section styles
\newcommand\ruleafter[1]{\sizeThirdBold{\MakeUppercase{#1}}{\color{black!60!\@themecolor}\hrulefill}}
\newcommand\rulemiddle[1]{\sizeThirdBold{\MakeUppercase{#1}}\hspace{0.5em}{\color{black!60!\@themecolor}\hrulefill}}

\titleformat{\section}
  {\sizeSecond\bfseries\raggedright\color{\@themecolor}}
  {}{0pt}
  {\rulemiddle}
\titlespacing*{\section}{0pt}{-2pt}{3pt}

\newcommand{\datedexperience}[2]{%
  \noindent\sizeThirdBold{#1}\,|\,\datetext{#2}\par\vspace{0.01cm}%
}

\newcommand{\explanation}[2]{%
  \noindent\sizeThirdBold{#1}\,|\,\sizeThird{#2}\par\vspace{0.01cm}%
}

\newcommand{\explanationdetail}[1]{%
  \begin{adjustwidth}{\gridindent}{}
    \footnotesize #1
    \vspace{0.1cm}
    \hspace{0.5em}
  \end{adjustwidth}
}

\newenvironment{jobbullets}{%
  \begin{itemize}[
    leftmargin=0.6cm,
    rightmargin=0.6cm,
    labelsep=0.3cm,
    itemsep=0.05cm,
    topsep=0.05cm,
    partopsep=0pt,
    parsep=0pt
  ]
  \renewcommand{\labelitemi}{\color{\@themecolor}\textbullet}
}{%
  \end{itemize}
}

\newenvironment{educationBlock}{%
  \begin{itemize}[
    leftmargin=0.6cm,
    rightmargin=0.6cm,
    label={},
    labelsep=0pt,
    itemindent=0pt,
    topsep=0.1cm,
    parsep=0pt
  ]
  \item
}{%
  \end{itemize}
}

\newcommand{\experience}[2]{\mbox{\hspace{1em}\sizeThirdBold{#1}}}

\newcommand{\skillslearned}[1]{%
  \smallskip
  \noindent
  \textcolor{NavyBlue}{\sizeThirdBold{Skills:}} #1
  \\[0.1cm]
}

\newcommand{\certificationitem}[2]{%
  \noindent\hspace{\gridindent}{\sizeThirdBold{#1}}\,|\,\datetext{#2}\par\vspace{0.15cm}%
}
