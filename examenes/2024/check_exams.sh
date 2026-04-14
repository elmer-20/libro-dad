#!/bin/bash

check_file() {
    local file=$1
    echo ""
    echo "============================================"
    echo "ANALIZANDO: $file"
    echo "============================================"
    
    # Count questions by looking for \item that start questions
    # These are \item followed by substantial text (not alternatives a-e)
    grep -n "^[[:space:]]*\\item " "$file" > /tmp/items.txt
    
    echo "Total líneas con \item: $(wc -l < /tmp/items.txt)"
    
    # Look for alternatives lines
    grep -n "\\item [a-e])" "$file" > /tmp/alternatives.txt
    echo "Total alternativas encontradas: $(wc -l < /tmp/alternatives.txt)"
    
    # Count enumerate blocks
    echo "Bloques \begin{enumerate}: $(grep -c '\begin{enumerate}' "$file")"
    echo "Bloques \end{enumerate}: $(grep -c '\end{enumerate}' "$file")"
}

for file in general-2024-I-primera-etapa.tex general-2024-I-segunda-etapa.tex cepreuna-2024-I-primera-etapa.tex cepreuna-2024-I-segunda-etapa.tex; do
    check_file "$file"
done
