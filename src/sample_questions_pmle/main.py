import random
import fitz  # PyMuPDF
import re

DELETE_PATRONS = ["Proprietary + Confidential\n"]


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

            options_list = re.findall(r'([A-D]):\s+(.*)', question_text)
            formatted_options = [f"{opt[0]}: {opt[1]}" for opt in options_list]
            options.append(formatted_options)

            answers = answers + [search_answers(answer_blocks)]

    return questions, options, answers

def interactive_quiz(
        questions: list[str],
        options: list[list[str]],
        answers: list[list[str]]
) -> float:
    """
    Función que genera una encuesta interactiva con las preguntas del formulario cargadas
    previamente e integradas en questions, options y answers.

    Parameters
    ----------
    questions: list[str]
        Lista con las preguntas del formulario
    options: list[list[str]]
        Lista con la lista de opciones de respuesta por pregunta
    answers: list[list[str]]
        Lista con la lista de respuestas correctas por pregunta.

    Returns
    -------

    """
    question_indices = list(range(len(questions)))
    random.shuffle(question_indices)
    score = 0
    count_questions = 0
    for idx in question_indices:
        print(f"\nQuestion {idx} (diapo {idx*2+1}):\n\t{questions[idx]}\n")
        print(f"NOTA: Hay {len(answers[idx])} respuestas posibles. En el caso de "
              f"responde más de una separe las soluciones con comas.\n")
        for option in options[idx]:
            print(option)
        user_answer = input("Your answer (A/B/C/D): ").strip().upper().replace(" ","")
        if user_answer == ",".join(answers[idx]):
            print("Correct!")
            score += 1
        else:
            print(f"Wrong! The correct answer was {answers[idx]}")
        count_questions = count_questions + 1

    print(f"\nYour final score: {score}/{len(count_questions) * 100}")

if __name__ == "__main__":
    file_path = "data/Sample Questions of PMLE.pdf"
    questions, options, answers = extract_questions_from_pdf(file_path)
    interactive_quiz(questions, options, answers)
