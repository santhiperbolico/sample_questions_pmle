import fitz  # PyMuPDF
import re
import tkinter as tk
from tkinter import messagebox
import random


def start_quiz(questions, options, answers):
    # Variables globales
    question_indices = list(range(len(questions)))
    random.shuffle(question_indices)
    current_question_index = [0]  # Usamos una lista para permitir la modificación por referencia
    score = [0]
    failures = [0]
    questions_answered = [0]  # Contador de preguntas respondidas

    # Funciones
    def show_question():
        idx = question_indices[current_question_index[0]]
        question_label.config(text=f"Pregunta {current_question_index[0] + 1}:\n{questions[idx]}")

        # Mostrar opciones
        for i, opt in enumerate(options[idx]):
            option_vars[i].set(0)  # Restablecer las casillas
            option_buttons[i].config(text=opt, state="normal")

    def submit_answer():
        idx = question_indices[current_question_index[0]]
        user_selection = {options[idx][i][0] for i, var in enumerate(option_vars) if var.get() == 1}
        correct_answers = set(answers[idx])

        if user_selection == correct_answers:
            score[0] += 1
            result_label.config(text="¡Correcto!", fg="green")
        else:
            failures[0] += 1
            result_label.config(text=f"Incorrecto. Respuesta(s) correcta(s): {', '.join(correct_answers)}", fg="red")

        questions_answered[0] += 1
        update_stats()
        next_question()

    def next_question():
        if current_question_index[0] + 1 < len(questions):
            current_question_index[0] += 1
            show_question()
        else:
            messagebox.showinfo("Fin del cuestionario", f"Has completado el cuestionario.\n"
                                                        f"Aciertos: {score[0]}\n"
                                                        f"Fallos: {failures[0]}\n"
                                                        f"Nota final: {calculate_grade()}")
            root.destroy()

    def calculate_grade():
        if questions_answered[0] == 0:
            return "0.00"
        return f"{(score[0] / questions_answered[0]) * 10:.2f}"

    def update_stats():
        score_label.config(text=f"Aciertos: {score[0]}")
        failure_label.config(text=f"Fallos: {failures[0]}")
        grade_label.config(text=f"Nota actual: {calculate_grade()}")

    # Interfaz gráfica
    root = tk.Tk()
    root.title("Cuestionario Interactivo")

    # Pregunta
    question_label = tk.Label(root, text="", wraplength=500, justify="left", font=("Arial", 14))
    question_label.pack(pady=15)

    # Opciones
    option_vars = [tk.IntVar() for _ in range(4)]  # Variable para cada opción (0 = no marcada, 1 = marcada)
    option_buttons = []
    for var in option_vars:
        btn = tk.Checkbutton(root, text="", variable=var, font=("Arial", 12), anchor="w", wraplength=500,
                             justify="left")
        btn.pack(fill="x", padx=30, pady=5)
        option_buttons.append(btn)

    # Botón de envío
    submit_button = tk.Button(root, text="Enviar respuesta", command=submit_answer, font=("Arial", 12))
    submit_button.pack(pady=20)

    # Resultado
    result_label = tk.Label(root, text="", font=("Arial", 12))
    result_label.pack(pady=10)

    # Estadísticas
    stats_frame = tk.Frame(root)
    stats_frame.pack(pady=20)

    score_label = tk.Label(stats_frame, text="Aciertos: 0", font=("Arial", 12))
    score_label.grid(row=0, column=0, padx=20)
    failure_label = tk.Label(stats_frame, text="Fallos: 0", font=("Arial", 12))
    failure_label.grid(row=0, column=1, padx=20)
    grade_label = tk.Label(stats_frame, text="Nota actual: 0.00", font=("Arial", 12))
    grade_label.grid(row=0, column=2, padx=20)

    # Mostrar la primera pregunta
    show_question()

    # Ejecutar la interfaz gráfica
    root.mainloop()


def search_answers(blocks: list[dict]) -> list[str]:
    answers = []
    for bloque in blocks:
        if bloque['type'] == 0:  # Bloque de texto
            for linea in bloque['lines']:
                for span in linea['spans']:
                    if span['font'].endswith('-Bold') and span['color'] == 4359668:  # Azul
                        texto = span['text'].strip()
                        if texto.startswith(('A:', 'B:', 'C:', 'D:')):
                            respuesta_correcta = texto[0]  # Extraer la letra
                            answers.append(respuesta_correcta)  # Devolvemos el valor en cuanto lo encontramos
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
            question_body = question_text.replace("Proprietary + Confidential\n", "")
            end_pattern = re.compile(r"\n\s*A:")
            end_match = end_pattern.search(question_body)

            question_body = question_body[:end_match.start()]
            questions.append(question_body)

            options_list = re.findall(r'([A-D]):\s+(.*)', question_text)
            formatted_options = [f"{opt[0]}: {opt[1]}" for opt in options_list]
            options.append(formatted_options)

            answers = answers + [search_answers(answer_blocks)]

    return questions, options, answers


if __name__ == "__main__":
    file_path = "data/Sample Questions of PMLE.pdf"
    questions, options, answers = extract_questions_from_pdf(file_path)
    start_quiz(questions, options, answers)
