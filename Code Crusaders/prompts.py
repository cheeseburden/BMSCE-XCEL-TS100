"""
Prompt templates for the AI Code Review Assistant.
Uses structured prompts to get consistent, high-quality reviews from LLMs.
"""

SYSTEM_PROMPT = """You are an elite senior software engineer and code reviewer with 15+ years of experience \
across multiple programming languages and frameworks. You perform thorough, industry-standard code reviews \
that help developers write better, safer, and more performant code.

Your reviews are:
- Precise and actionable
- Educational — you teach best practices, not just flag issues
- Security-conscious — you catch vulnerabilities before they ship
- Performance-aware — you identify bottlenecks and inefficiencies

You MUST respond ONLY with valid JSON. No markdown, no explanation outside JSON."""


CODE_REVIEW_PROMPT = """Analyze the following {language} code and provide a comprehensive code review.

```{language}
{code}
```

Return your review as a JSON object with EXACTLY this structure:
{{
    "overall_score": <integer 0-100>,
    "summary": "<2-3 sentence executive summary of code quality>",
    "issues": [
        {{
            "id": <integer starting from 1>,
            "category": "<one of: Bug, Security, Performance, Style, Best Practice>",
            "severity": "<one of: Critical, High, Medium, Low>",
            "title": "<short descriptive title>",
            "description": "<detailed explanation of the issue>",
            "line_reference": "<line number or range, e.g. 'Line 5' or 'Lines 10-15', or 'General' if not line-specific>",
            "problematic_code": "<the exact problematic code snippet>",
            "suggested_fix": "<corrected code snippet showing the best practice solution>",
            "explanation": "<educational explanation of WHY the fix is better, what principle it follows (e.g., SOLID, DRY, OWASP), and how it prevents future issues>",
            "learning_reference": "<URL or reference to official documentation, e.g. 'https://docs.python.org/3/library/...' or 'OWASP Top 10: A03 Injection'>"
        }}
    ],
    "strengths": [
        "<positive aspect of the code>"
    ],
    "metrics": {{
        "readability": <integer 0-10>,
        "maintainability": <integer 0-10>,
        "security": <integer 0-10>,
        "performance": <integer 0-10>,
        "best_practices": <integer 0-10>
    }}
}}

IMPORTANT RULES:
1. Find ALL issues — do not skip any bugs, vulnerabilities, or anti-patterns.
2. For EVERY issue, provide a complete corrected code snippet in "suggested_fix" — not just a description.
3. The "explanation" must TEACH the developer — explain the underlying principle.
4. Be specific with line references.
5. Include at least 1-2 strengths even for bad code — find something positive.
6. Score honestly — don't inflate scores.
7. Return ONLY valid JSON — no markdown fences, no extra text.
8. VALUE SIMPLICITY: Simple, clean code that works correctly IS good code. Do NOT penalize code for being simple. \
Only flag issues that are genuinely problematic (real bugs, actual security risks, clear performance issues, poor readability). \
Do NOT flag code just because it could theoretically be wrapped in more abstractions or design patterns.
9. PROPORTIONATE SCORING: A short, correct, readable script with no bugs and no security issues should score 80-95. \
Only deduct points for REAL problems — not for stylistic preferences or missing optional features like logging frameworks.
10. Do NOT suggest adding complexity (extra classes, abstract patterns, factory methods) unless the code genuinely needs it. \
Simple, correct code is better than over-engineered code."""



OPTIMIZE_CODE_PROMPT = """You are given the following {language} code. Rewrite it to fix all genuine issues \
while keeping the code PRACTICAL, CLEAN, and INDUSTRY-READY.

Original code:
```{language}
{code}
```

CRITICAL RULES — READ CAREFULLY:
1. **MATCH THE COMPLEXITY LEVEL OF THE INPUT.** This is the most important rule.
   - If the input is a simple script or small function → keep your output simple and clean. \
Do NOT wrap it in classes, abstract patterns, or unnecessary layers of abstraction.
   - If the input is already complex (classes, modules, architecture) → then apply proper design patterns \
and structural improvements.
2. Fix all REAL bugs, security vulnerabilities, and anti-patterns.
3. Use proper error handling where errors can actually occur.
4. Use clear, descriptive variable and function names.
5. Add type hints to function signatures. Add brief docstrings to functions that are not self-explanatory.
6. Use modern {language} idioms, but keep it readable.
7. Preserve the EXACT same functionality and intent. Do not add features that weren't there.
8. Add short inline comments ONLY for non-obvious improvements (e.g., "# Parameterized query prevents SQL injection").
9. Do NOT over-engineer. Simple, correct, readable code is BETTER than complex, abstract code.
10. The optimized code should score 85+ if reviewed by a code reviewer who values: \
correctness, security, readability, proper error handling, and appropriate use of language features. \
Make sure you address all of these criteria.

Return ONLY the optimized source code. No JSON. No markdown fences. No explanations. Just raw code."""
