import random
import fitz  # PyMuPDF
import re

DELETE_PATRONS = ["Proprietary + Confidential\n"]


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
                            answers.append(respuesta_correcta) #Devolvemos el valor en cuanto lo encontramos, no es necesario que siga iterando)

    return answers

def extract_questions_from_pdf(file_path):
    doc = fitz.open(file_path)
    questions = []
    options = []
    answers = []
    question_pattern = re.compile(r'Sample Question \d+')

    for i in range(0, len(doc), 2):  # Iterate over pages, assuming questions and answers are on consecutive pages
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

def interactive_quiz(questions, options, answers):
    question_indices = list(range(len(questions)))
    random.shuffle(question_indices)
    score = 0

    for idx in question_indices:
        print(f"\nQuestion {idx} (diapo {idx*2+1}):\n\t{questions[idx]}\n")
        print(f"NOTA: Hay {len(answers[idx])} respuestas posibles. En el caso de responde más de una separe las soluciones con comas.\n")
        for option in options[idx]:
            print(option)
        user_answer = input("Your answer (A/B/C/D): ").strip().upper().replace(" ","")
        if user_answer == ",".join(answers[idx]):
            print("Correct!")
            score += 1
        else:
            print(f"Wrong! The correct answer was {answers[idx]}")

    print(f"\nYour final score: {score}/{len(questions)}")

if __name__ == "__main__":
    file_path = "data/Sample Questions of PMLE.pdf"
    questions, options, answers = extract_questions_from_pdf(file_path)
    interactive_quiz(questions, options, answers)
