import argparse
import logging
import sys
import os

import fitz  # PyMuPDF
import re
import random

def get_argument_parser() -> argparse.ArgumentParser:
    """
    Función que genera los argumentos .

    Returns
    -------
    parser: argparse.ArgumentParser
        Parser con los argumentos del job.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path")
    return parser


def get_params(argv: list[str]) -> dict[str, int]:
    """
    Función de preprocesado de los argumentos.

    Parameters
    ----------
    argv: list[str]
        Lista de argumentos del job.

    Returns
    -------
    params: dict[str, int]
        Parámetros con los identificadores del proecto y de la ETL.
    """
    args = get_argument_parser().parse_args(argv)
    params = args.__dict__
    return params

def start_quiz(questions, options, answers):
    # Variables globales
    question_indices = list(range(len(questions)))
    random.shuffle(question_indices)
    current_question_index = 0
    score = 0
    failures = 0

    # Funciones para el cuestionario sin GUI
    while current_question_index < len(questions):
        idx = question_indices[current_question_index]
        print(f"\nPregunta {current_question_index + 1}:\n{questions[idx]}\n")

        # Mostrar opciones
        for i, opt in enumerate(options[idx]):
            print(f"{chr(65 + i)}: {opt}")

        # Leer la respuesta del usuario
        user_input = input("Tu respuesta (puedes ingresar múltiples opciones, ej. AB): ").upper()
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

def search_answers(blocks: list[dict]) -> list[str]:
    answers = []

    for bloque in blocks:
        if bloque['type'] == 0:  # Bloque de texto
            for linea in bloque['lines']:
                for span in linea['spans']:
                    # Comprueba si el texto está en azul y negrita
                    if span['font'].endswith('-Bold') and span['color'] == 4359668:  # Azul
                        texto = span['text'].strip()
                        if texto.startswith(('A:', 'B:', 'C:', 'D:')):
                            respuesta_correcta = texto[0]  # Extraer la letra
                            answers.append(respuesta_correcta)

    return answers

def find_options(question_text: str) -> list[str]:
    options = re.findall(r"[A-D]:\s+(.*)", question_text)
    return options

def extract_questions_from_pdf(file_path: str) -> tuple[list[str], list[list[str]], list[list[str]]]:
    doc = fitz.open(file_path)
    questions = []
    options = []
    answers = []
    question_pattern = re.compile(r'Sample Question \d+')

    for i in range(0, len(doc), 2):
        question_page = doc.load_page(i)
        answer_page = doc.load_page(i + 1)

        question_text = question_page.get_text()
        answer_blocks = answer_page.get_text("dict", flags=fitz.TEXT_PRESERVE_LIGATURES)['blocks']

        question_match = question_pattern.search(question_text)
        if question_match:
            question_body = question_text.replace("Proprietary + Confidential\n", "")
            end_pattern = re.compile(r"\n\s*A:")
            end_match = end_pattern.search(question_body)

            question_body = question_body[:end_match.start()]
            questions.append(question_body)
            options_list = find_options(question_text)
            options.append(options_list)

            answers = answers + [search_answers(answer_blocks)]

    return questions, options, answers

if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] [%(asctime)s] %(message)s")
    params = get_params(sys.argv[1:])
    questions, options, answers = extract_questions_from_pdf(**params)
    start_quiz(questions, options, answers)
