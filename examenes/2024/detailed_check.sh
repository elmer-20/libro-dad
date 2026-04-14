#!/bin/bash

analyze_section() {
    local file=$1
    local start_line=$2
    local end_line=$3
    local section_name=$4
    
    # Extract the section
    sed -n "${start_line},${end_line}p" "$file" > /tmp/section.tex
    
    # Count questions (lines starting with \item that don't have [a-e])
    local question_count=$(grep -c "^[[:space:]]*\\item [^a-e]" /tmp/section.tex 2>/dev/null || echo "0")
    
    # Count lines with alternatives a-e)
    local alt_lines=$(grep "\item [a-e])" /tmp/section.tex | wc -l)
    
    if [ $question_count -gt 0 ]; then
        local expected_alts=$((question_count * 5))
        
        echo ""
        echo "Sección: $section_name"
        echo "  Preguntas detectadas: $question_count"
        echo "  Alternativas encontradas: $alt_lines"
        echo "  Alternativas esperadas: $expected_alts"
        
        if [ $alt_lines -ne $expected_alts ]; then
            echo "  ⚠ WARNING: discrepancia en alternativas"
        fi
    fi
}

echo "======================================"
echo "ANALIZANDO: general-2024-I-primera-etapa.tex"
echo "======================================"

file="general-2024-I-primera-etapa.tex"

# Extraer subsecciones y sus líneas iniciales
grep -n "subsection\*" "$file" | head -20
