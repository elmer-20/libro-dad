#!/usr/bin/env python3
import re
import sys

def analyze_file(filename):
    print(f"\n{'='*90}")
    print(f"ANALIZANDO: {filename}")
    print('='*90)
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track question numbers and alternatives
    questions_by_area = {}
    current_area = None
    current_subject = None
    in_question = False
    question_num = 0
    question_start_line = 0
    alternatives = []
    
    for i, line in enumerate(lines, 1):
        # Track areas and subjects
        if '\section' in line and '*' in line:
            current_area = line.strip()
        elif '\subsection' in line and '*' in line:
            current_subject = re.sub(r'\subsection\*{', '', line).replace('}', '').strip()
            if current_area not in questions_by_area:
                questions_by_area[current_area] = {}
            if current_subject not in questions_by_area[current_area]:
                questions_by_area[current_area][current_subject] = []
        
        # Detect question start (first \item in enumerate)
        if re.match(r'^\s*\item\s+', line) and not re.match(r'^\s*\item\s+[a-e]\)', line):
            # This might be a question if it's followed by alternatives
            # Check next few lines for enumerate with alternatives
            has_enum = False
            for j in range(i, min(i+30, len(lines))):
                if '\begin{enumerate}' in lines[j]:
                    has_enum = True
                    break
                if '\end{enumerate}' in lines[j] and j > i + 5:
                    break
            
            if has_enum:
                question_num += 1
                question_start_line = i
                alternatives = []
                in_question = True
        
        # Count alternatives
        if in_question and re.match(r'^\s*\item\s+[a-e]\)', line):
            alternatives.append(line.strip())
        
        # End of question (end of enumerate)
        if in_question and '\end{enumerate}' in line and alternatives:
            if current_area and current_subject:
                if question_num not in [q[0] for q in questions_by_area[current_area][current_subject]]:
                    questions_by_area[current_area][current_subject].append((
                        question_num, question_start_line, len(alternatives), alternatives
                    ))
            in_question = False
    
    # Report results
    for area, subjects in questions_by_area.items():
        print(f"\n{area}:")
        for subject, questions in subjects.items():
            if questions:
                print(f"\n  {subject}:")
                print(f"    Total preguntas: {len(questions)}")
                
                # Check for missing numbers
                question_nums = sorted([q[0] for q in questions])
                missing = []
                duplicates = []
                
                for num in range(1, max(question_nums) + 1):
                    count = question_nums.count(num)
                    if count == 0:
                        missing.append(num)
                    elif count > 1:
                        duplicates.append(num)
                
                # Check for alternative issues
                alt_issues = []
                for q_num, line_num, alt_count, alts in questions:
                    if alt_count != 5:
                        alt_issues.append((q_num, line_num, alt_count))
                    else:
                        # Check for repeated alternatives
                        alt_texts = [re.sub(r'\item\s+[a-e]\)\s*', '', a) for a in alts]
                        if len(alt_texts) != len(set(alt_texts)):
                            alt_issues.append((q_num, line_num, alt_count, "repetidas"))
                
                if missing:
                    print(f"    ⚠ Números faltantes: {missing}")
                if duplicates:
                    print(f"    ⚠ Números duplicados: {duplicates}")
                if alt_issues:
                    print(f"    ⚠ Preguntas con != 5 alternativas:")
                    for issue in alt_issues:
                        if len(issue) == 3:
                            print(f"       Pregunta {issue[0]} (línea {issue[1]}): {issue[2]} alternativas")
                        else:
                            print(f"       Pregunta {issue[0]} (línea {issue[1]}): alternativas repetidas")
                
                if not missing and not duplicates and not alt_issues:
                    print(f"    ✓ Sin problemas detectados")

for filename in [
    "general-2024-I-primera-etapa.tex",
    "general-2024-I-segunda-etapa.tex",
    "cepreuna-2024-I-primera-etapa.tex",
    "cepreuna-2024-I-segunda-etapa.tex"
]:
    try:
        analyze_file(filename)
    except Exception as e:
        print(f"Error analizando {filename}: {e}")
