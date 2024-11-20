import logging
import sys
import os

from sample_questions_pmle.utils import extract_questions_from_pdf, get_params


import random
import gradio as gr

def start_quiz(questions, options, answers):
    # Variables globales
    question_indices = list(range(len(questions)))
    random.shuffle(question_indices)
    current_question_index = [0]
    score = [0]

    def get_next_question():
        if current_question_index[0] < len(questions):
            idx = question_indices[current_question_index[0]]
            question_text = f"Pregunta {current_question_index[0] + 1}:\n{questions[idx]}"
            option_texts = options[idx]
            return question_text, option_texts, ""
        else:
            return "El cuestionario ha terminado.", [], f"Puntuación final: {score[0]}/{len(questions)}"

    def submit_answer(user_input):
        if current_question_index[0] < len(questions):
            idx = question_indices[current_question_index[0]]
            user_selection = set(user_input)
            correct_answers = set(answers[idx])

            if user_selection == correct_answers:
                score[0] += 1
                feedback = "¡Correcto!"
            else:
                feedback = f"Incorrecto. Respuesta(s) correcta(s): {', '.join(correct_answers)}"

            current_question_index[0] += 1
            next_question, next_options, final_score = get_next_question()

            return next_question, next_options, feedback, final_score
        else:
            return "El cuestionario ha terminado.", [], "El cuestionario ya ha terminado."

    def reset_quiz():
        random.shuffle(question_indices)
        current_question_index[0] = 0
        score[0] = 0
        return get_next_question() + ("",)

    with gr.Blocks() as quiz_interface:
        question = gr.Textbox(label="Pregunta", interactive=False)
        options_group = gr.CheckboxGroup(choices=[], label="Opciones", interactive=True)
        feedback = gr.Textbox(label="Retroalimentación", interactive=False)
        final_score = gr.Textbox(label="Puntuación Final", interactive=False)

        next_question_btn = gr.Button("Enviar Respuesta")
        next_question_btn.click(submit_answer, inputs=[options_group], outputs=[question, options_group, feedback, final_score])

        reset_btn = gr.Button("Reiniciar Cuestionario")
        reset_btn.click(reset_quiz, outputs=[question, options_group, feedback, final_score])

        # Inicializa la primera pregunta
        question_text, option_texts, _ = get_next_question()
        question.value = question_text
        options_group.choices = option_texts

    return quiz_interface

if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] [%(asctime)s] %(message)s")
    params = get_params(sys.argv[1:])
    questions, options, answers = extract_questions_from_pdf(**params)
    start_quiz(questions, options, answers)
