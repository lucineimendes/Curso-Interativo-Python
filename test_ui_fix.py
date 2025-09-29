#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para verificar se os exercícios estão sendo carregados na interface
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'projects'))

from projects.app import app

def test_lesson_exercises_ui():
    print("=== TESTE DE EXERCICIOS NA INTERFACE ===\n")
    
    with app.test_client() as client:
        # Testar página de lição que deve mostrar exercícios
        response = client.get('/courses/python-basico/lessons/ola-mundo-python')
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # Verificar se a seção de exercícios está presente
            if 'Exercícios:' in html_content:
                print("OK - Seção de exercícios encontrada no HTML")
                
                # Verificar se há links para exercícios
                if 'ex-introducao-1' in html_content:
                    print("OK - Exercício ex-introducao-1 encontrado no HTML")
                else:
                    print("ERRO - Exercício ex-introducao-1 NÃO encontrado no HTML")
                    
                # Verificar se há links para o editor
                if '/editor' in html_content:
                    print("OK - Links para editor encontrados")
                else:
                    print("ERRO - Links para editor NÃO encontrados")
                    
            else:
                print("ERRO - Seção de exercícios NÃO encontrada no HTML")
                
            # Mostrar parte do HTML para debug
            print("\n--- TRECHO DO HTML (primeiros 2000 chars) ---")
            print(html_content[:2000])
            print("--- FIM DO TRECHO ---\n")
                
        else:
            print(f"ERRO - Página retornou status {response.status_code}")
            
    print("=== TESTE CONCLUIDO ===")

if __name__ == "__main__":
    test_lesson_exercises_ui()