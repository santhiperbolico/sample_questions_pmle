import logging
import sys
import os

from sample_questions_pmle.utils import extract_questions_from_pdf, get_params


import random


def start_quiz(questions, options, answers):
    # Variables globales
    question_indices = list(range(len(questions)))
    random.shuffle(question_indices)
    current_question_index = 0
    score = 0
    failures = 0

    # Funciones para el cuestionario sin GUI
    condition_end = True
    while current_question_index < len(questions) and condition_end:
        idx = question_indices[current_question_index]
        print(f"\nPregunta {current_question_index + 1} (page {idx*2 + 1}) - Score: {score} / {current_question_index}:")
        print(f"\n{questions[idx]}\n")

        # Mostrar opciones
        for i, opt in enumerate(options[idx]):
            print(f"{chr(65 + i)}: {opt}")

        # Leer la respuesta del usuario
        user_input = input("Tu respuesta (puedes ingresar múltiples opciones, ej. AB). Para finalizar escribe `end`: ").upper()
        if user_input.lower() == "end":
            condition_end = False
            continue

        user_selection = set(user_input)
        correct_answers = set(answers[idx])

        if user_selection == correct_answers:
            score += 1
            print("¡Correcto!\n")
        else:
            failures += 1
            print(f"Incorrecto. Respuesta(s) correcta(s): {', '.join(correct_answers)}\n")

        current_question_index += 1

    # Mostrar resultados
    print(f"\nHas completado el cuestionario.\nAciertos: {score}\nFallos: {failures}\nNota final: {(score / len(questions)) * 10:.2f}")


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] [%(asctime)s] %(message)s")
    params = get_params(sys.argv[1:])
    questions, options, answers = extract_questions_from_pdf(**params)
    start_quiz(questions, options, answers)
