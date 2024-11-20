import argparse

import fitz
import re

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


def search_answers(blocks: list[dict]) -> list[str]:
    """
    Función que busca la respuesta correcta de la pregunta entre toda la lista de bloques
    de la página del pdf de la respuesta.

    Parameters
    ----------
    blocks: list[dict]
        Lista de bloques de la respuesta.

    Returns
    -------
    answers: list[str]
        Lista con las letras asociadas a la respuesta.

    """
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
                            answers.append(respuesta_correcta) #Devolvemos el valor en cuanto lo encontramos, no es necesario que siga iterando)

    return answers

def find_options(question_text: str) -> list[str]:
    """
    Función que extraer las opciones de las preguntas.

    Parameters
    ----------
    question_text: str
        Texto completo de la pregunta y opciones

    Returns
    -------
    options: list[str]
        Lista de las opciones de la pregunta

    """
    question_pattern = re.compile(r'Sample Question \d+')
    options = []
    option_pattern = re.compile(r"\n\s*([A-D]):")
    condition = True
    options_body = question_text
    max_iter = 10
    iter = 0
    while condition and iter < max_iter:
        opt_match = option_pattern.search(options_body)
        if opt_match:
            opt_next_match =  option_pattern.search(options_body[opt_match.end():])
            if opt_next_match:
                option = options_body[
                         opt_match.start():
                         opt_next_match.start() + opt_match.end()
                         ]
                options_body = options_body[opt_next_match.start() + opt_match.end():]
            else:
                option = options_body[opt_match.start(): ]
                question_match = question_pattern.search(option)
                option = option[:question_match.start()]
                condition = False
            option = option.replace("\n", "").strip()
            options.append(option)
        else:
            condition = False
        iter = iter + 1

    return options

def extract_questions_from_pdf(
        file_path: str
) -> tuple[list[str], list[list[str]], list[list[str]]]:
    """
    Función que lee el pdf con el formulario y separs las preguntas, las opciones y las
    repsuestas en tres listas.

    Parameters
    ----------
    file_path: str
        RUta donde se encuentra el pdf con el formulario..

    Returns
    -------
    questions: list[str]
        Lista con las preguntas del formulario
    options: list[list[str]]
        Lista con la lista de opciones de respuesta por pregunta
    answers: list[list[str]]
        Lista con la lista de respuestas correctas por pregunta.
    """
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
            question_body =question_text.replace("Proprietary + Confidential\n", "")
            end_pattern = re.compile(r"\n\s*A:")
            end_match = end_pattern.search(question_body)

            question_body = question_body[:end_match.start()]
            questions.append(question_body)
            options_list = find_options(question_text)
            options.append(options_list)

            answers = answers + [search_answers(answer_blocks)]

    return questions, options, answers

