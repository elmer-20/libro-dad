#!/bin/bash

# Función para contar preguntas en una sección
count_questions_in_section() {
    local file=$1
    local start_line=$2
    local end_line=$3
    local section_name=$4
    
    # Extraer la sección
    sed -n "${start_line},${end_line}p" "$file" > /tmp/sect.txt
    
    # Preguntas: líneas que empiezan con \item (puede tener tabs/espacios)
    # y que NO tienen solo números o caracteres simples en la misma línea
    # Las alternativas típicamente tienen \item [a-e])
    
    # Contar líneas con \item
    local total_items=$(grep -c "\\item " /tmp/sect.txt)
    
    # Contar alternativas con patrón a), b), c), d), e)
    local alts=$(grep -c "\\item.*[a-e])" /tmp/sect.txt)
    
    # Las preguntas son el total de items menos las alternativas
    local questions=$((total_items - alts))
    
    if [ $questions -gt 0 ]; then
        local expected_alts=$((questions * 5))
        
        echo "$section_name|$questions|$alts|$expected_alts"
    fi
}

# Analizar cada archivo
analyze_file() {
    local file=$1
    echo ""
    echo "========================================="
    echo "ARCHIVO: $(basename $file)"
    echo "========================================="
    
    # Obtener subsecciones
    declare -a subsections
    declare -a line_numbers
    
    mapfile -t lines < <(grep -n "subsection\*{" "$file" | cut -d: -f1)
    mapfile -t names < <(grep "subsection\*{" "$file" | sed 's/.*subsection\*{\([^}]*\)}.*/\1/')
    
    local num_sections=${#lines[@]}
    
    for i in $(seq 0 $((num_sections - 1))); do
        local start_line=${lines[$i]}
        local section_name="${names[$i]}"
        
        # Determinar end_line
        local end_line
        if [ $i -lt $((num_sections - 1)) ]; then
            end_line=$((${lines[$((i+1))]} - 1))
        else
            end_line=$(wc -l < "$file")
        fi
        
        # Contar preguntas
        result=$(count_questions_in_section "$file" "$start_line" "$end_line" "$section_name")
        if [ ! -z "$result" ]; then
            echo "$result"
        fi
    done
}

# Procesar cada archivo
for f in general-2024-I-primera-etapa.tex general-2024-I-segunda-etapa.tex cepreuna-2024-I-primera-etapa.tex cepreuna-2024-I-segunda-etapa.tex; do
    analyze_file "$f"
done
