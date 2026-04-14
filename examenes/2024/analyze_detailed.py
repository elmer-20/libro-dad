#!/usr/bin/env python3
import re
import sys

def analyze_file(filename):
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    results = {
        'filename': filename,
        'sections': {},
        'total_questions': 0
    }
    
    current_section = 'General'
    current_subsection = 'Unknown'
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Track sections and subsections
        if '\section*' in line:
            current_section = line.strip()
            if current_section not in results['sections']:
                results['sections'][current_section] = {}
        elif '\subsection*' in line:
            current_subsection = line.strip()
            if current_section not in results['sections']:
                results['sections'][current_section] = {}
            if current_subsection not in results['sections'][current_section]:
                results['sections'][current_section][current_subsection] = {
                    'questions': [],
                    'issues': []
                }
        
        # Detect question: \item followed by question text (not alternatives)
        if re.match(r'^\s*\item\s+', line):
            # Check if this is a question (not an alternative)
            # Alternatives typically have: \item followed by a), b), c), d), e) or \item $...$ etc
            stripped = line.strip()
            
            # Skip if it's an alternative (has label a-e) or Roman numeral or just a number/dollar sign in next part
            if not re.match(r'^\s*\item\s+[a-e]\)', stripped) and \
               not re.match(r'^\s*\item\s+[IVX]+\)', stripped):
                
                # This might be a question - look ahead for alternatives
                j = i + 1
                alternatives = []
                found_enum_with_alts = False
                
                # Look ahead to find the enumerate with alternatives
                while j < len(lines) and j < i + 100:
                    if '\begin{enumerate}' in lines[j]:
                        # Look for alternatives in this enumerate
                        k = j + 1
                        alt_count = 0
                        alt_items = []
                        while k < len(lines) and k < j + 50:
                            if re.match(r'^\s*\item\s+[a-e]\)', lines[k].strip()):
                                alt_items.append((k+1, lines[k].strip()))
                                alt_count += 1
                            elif '\end{enumerate}' in lines[k]:
                                break
                            k += 1
                        
                        if alt_count > 0:
                            found_enum_with_alts = True
                            alternatives = alt_items
                            break
                    
                    if '\subsection' in lines[j] or '\section' in lines[j]:
                        break
                    j += 1
                
                if found_enum_with_alts:
                    # This is a question
                    if current_section not in results['sections']:
                        results['sections'][current_section] = {}
                    if current_subsection not in results['sections'][current_section]:
                        results['sections'][current_section][current_subsection] = {
                            'questions': [],
                            'issues': []
                        }
                    
                    q_data = {
                        'line': i + 1,
                        'text': line.strip()[:80],
                        'alt_count': len(alternatives),
                        'alternatives': alternatives
                    }
                    results['sections'][current_section][current_subsection]['questions'].append(q_data)
                    results['total_questions'] += 1
        
        i += 1
    
    return results

def analyze_alternatives(alt_items):
    """Check if alternatives are unique"""
    alt_texts = []
    for line_num, line_text in alt_items:
        # Extract alternative text
        text = re.sub(r'^\s*\item\s+[a-e]\)\s*', '', line_text)
        # Clean LaTeX commands for comparison
        text = re.sub(r'\[a-zA-Z]+\{[^}]*\}', '', text)
        text = text.strip()
        alt_texts.append((line_num, text))
    
    duplicates = []
    for i, (line1, text1) in enumerate(alt_texts):
        for j, (line2, text2) in enumerate(alt_texts):
            if i < j and text1 and text2 and text1.lower() == text2.lower():
                duplicates.append((line1, line2, text1[:50]))
    
    return duplicates

# Analyze all files
files = [
    "general-2024-I-primera-etapa.tex",
    "general-2024-I-segunda-etapa.tex", 
    "cepreuna-2024-I-primera-etapa.tex",
    "cepreuna-2024-I-segunda-etapa.tex"
]

for filename in files:
    results = analyze_file(filename)
    
    print(f"\n{'='*100}")
    print(f"ARCHIVO: {filename}")
    print('='*100)
    print(f"Total preguntas encontradas: {results['total_questions']}")
    
    for section, subsections in results['sections'].items():
        print(f"\n{section}:")
        for subsection, data in subsections.items():
            if data['questions']:
                print(f"\n  {subsection}:")
                print(f"    Preguntas: {len(data['questions'])}")
                
                # Check for issues
                issues = []
                
                for q in data['questions']:
                    if q['alt_count'] != 5:
                        issues.append(f"      Pregunta en línea {q['line']}: {q['alt_count']} alternativas (esperado 5)")
                    
                    # Check for repeated alternatives
                    dups = analyze_alternatives(q['alternatives'])
                    for dup in dups:
                        issues.append(f"      Pregunta en línea {q['line']}: alternativas repetidas (líneas {dup[0]}, {dup[1]}: '{dup[2]}')")
                
                if issues:
                    print("    ⚠ PROBLEMAS:")
                    for issue in issues:
                        print(issue)
                else:
                    print("    ✓ Sin problemas")

