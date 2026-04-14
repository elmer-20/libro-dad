#!/bin/bash

analyze_file() {
    local file=$1
    
    echo ""
    echo "================================================================"
    echo "ANALIZANDO ARCHIVO: $file"
    echo "================================================================"
    
    # Extraer números de línea de todas las subsecciones
    local subsections=$(grep -n "subsection\*" "$file" | cut -d: -f1)
    
    local count=0
    local prev_line=0
    local prev_subsection=""
    
    for line in $subsections; do
        count=$((count + 1))
        
        if [ $count -gt 1 ]; then
            # Analizar la sección anterior
            local end_line=$((line - 1))
            sed -n "${prev_line},${end_line}p" "$file" > /tmp/section.tex
            
            # Contar preguntas en esta sección
            # Una pregunta es un \item que NO es alternativa (no tiene [a-e)]
            local questions=$(grep -E "^[[:space:]]*\\item [^a-e]" /tmp/section.tex 2>/dev/null | wc -l)
            
            # Contar alternativas (líneas con \item seguidas de a), b), c), d), e))
            local alternatives=$(grep -E "\\item [a-e]\)" /tmp/section.tex | wc -l)
            
            local expected_alts=$((questions * 5))
            
            echo ""
            echo "Sección: $prev_subsection"
            echo "  Líneas: ${prev_line}-${end_line}"
            echo "  Preguntas: $questions"
            echo "  Alternativas: $alternatives (esperado: $expected_alts)"
            
            if [ $alternatives -ne $expected_alts ] && [ $questions -gt 0 ]; then
                echo "  ⚠⚠⚠ WARNING - Discrepancia en alternativas"
                # Mostrar preguntas encontradas
                grep -n "^[[:space:]]*\\item" /tmp/section.tex | grep -v "[a-e])" | head -3
            fi
        fi
        
        prev_line=$line
        prev_subsection=$(sed -n "${line}p" "$file" | sed 's/.*\subsection\*{\([^}]*\)}.*/\1/')
    done
}

for file in general-2024-I-primera-etapa.tex general-2024-I-segunda-etapa.tex cepreuna-2024-I-primera-etapa.tex cepreuna-2024-I-segunda-etapa.tex; do
    analyze_file "$file"
done
