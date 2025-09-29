#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar o carregamento de exercícios
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'projects'))

from projects.course_manager import CourseManager
from projects.exercise_manager import ExerciseManager

def diagnose_exercise_loading():
    print("=== DIAGNOSTICO DO CARREGAMENTO DE EXERCICIOS ===\n")
    
    # 1. Testar CourseManager
    print("1. Testando CourseManager...")
    try:
        course_mgr = CourseManager()
        courses = course_mgr.get_courses()
        print(f"   OK {len(courses)} cursos carregados")
        
        for course in courses:
            print(f"   - {course['id']}: {course['name']}")
            print(f"     exercises_file: {course.get('exercises_file', 'NAO DEFINIDO')}")
    except Exception as e:
        print(f"   ERRO no CourseManager: {e}")
        return False
    
    print()
    
    # 2. Testar ExerciseManager
    print("2. Testando ExerciseManager...")
    try:
        exercise_mgr = ExerciseManager()
        
        # Testar carregamento de exercícios básicos
        basic_exercises = exercise_mgr.load_exercises_from_file("basic/exercises.json")
        print(f"   OK {len(basic_exercises)} exercicios basicos carregados")
        
        # Testar carregamento de exercícios intermediários
        intermediate_exercises = exercise_mgr.load_exercises_from_file("intermediate/exercises.json")
        print(f"   OK {len(intermediate_exercises)} exercicios intermediarios carregados")
        
        # Mostrar alguns exercícios
        if basic_exercises:
            print(f"   Primeiro exercicio basico: {basic_exercises[0].get('id')} - {basic_exercises[0].get('title')}")
        
        if intermediate_exercises:
            print(f"   Primeiro exercicio intermediario: {intermediate_exercises[0].get('id')} - {intermediate_exercises[0].get('title')}")
            
    except Exception as e:
        print(f"   ERRO no ExerciseManager: {e}")
        return False
    
    print()
    
    # 3. Testar função get_exercise_by_id
    print("3. Testando get_exercise_by_id...")
    try:
        from projects.exercise_manager import get_exercise_by_id
        
        # Testar exercício básico
        exercise = get_exercise_by_id("ex-introducao-1", "python-basico")
        if exercise:
            print(f"   OK Exercicio encontrado: {exercise['id']} - {exercise['title']}")
        else:
            print("   ERRO Exercicio basico nao encontrado")
            
        # Testar exercício intermediário
        exercise = get_exercise_by_id("ex-poo-1", "python-intermediario")
        if exercise:
            print(f"   OK Exercicio encontrado: {exercise['id']} - {exercise['title']}")
        else:
            print("   ERRO Exercicio intermediario nao encontrado")
            
    except Exception as e:
        print(f"   ERRO na funcao get_exercise_by_id: {e}")
        return False
    
    print()
    
    # 4. Testar integração com Flask
    print("4. Testando integracao Flask...")
    try:
        from projects.app import app
        
        with app.test_client() as client:
            # Testar API de exercícios
            response = client.get('/api/courses/python-basico/exercises')
            if response.status_code == 200:
                exercises = response.get_json()
                print(f"   OK API retornou {len(exercises)} exercicios basicos")
            else:
                print(f"   ERRO API falhou com status {response.status_code}")
                
            # Testar página de exercício
            response = client.get('/courses/python-basico/exercise/ex-introducao-1/editor')
            if response.status_code == 200:
                print("   OK Pagina do editor de exercicio carregou")
            else:
                print(f"   ERRO Pagina do editor falhou com status {response.status_code}")
                
    except Exception as e:
        print(f"   ERRO na integracao Flask: {e}")
        return False
    
    print("\n=== DIAGNOSTICO CONCLUIDO ===")
    return True

if __name__ == "__main__":
    success = diagnose_exercise_loading()
    sys.exit(0 if success else 1)