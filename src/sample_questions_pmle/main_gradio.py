import logging
import sys
import os

from sample_questions_pmle.utils import extract_questions_from_pdf, get_params

import random
import gradio as gr
def start_quiz(questions, options, answers):
    question_indices = list(range(len(questions)))
    random.shuffle(question_indices)
    current_question_index = 0
    score = 0

    def get_next_question():
        if current_question_index < len(questions):
            idx = question_indices[current_question_index]
            question_text = f"Pregunta {current_question_index + 1} (page {idx*2+1}):\n{questions[idx]}\n"
            option_texts = options[idx]
            options_test = []
            for option in option_texts:
                question_text = question_text + f"\n {option}"
                options_test.append(option[0])
            final_score = ""
            if current_question_index > 0:
                final_score = f"{score/current_question_index}"
            return question_text, options_test, f"Puntuación: {final_score}"
        else:
            return "El cuestionario ha terminado.", [], f"Puntuación final: {score}/{len(questions)}"

    def submit_answer(user_input):
        nonlocal current_question_index, score  # ¡Importante!
        if current_question_index < len(questions):
            idx = question_indices[current_question_index]
            user_selection = set(user_input[0::2])
            correct_answers = set(answers[idx])

            if user_selection == correct_answers:
                score += 1
                feedback = "¡Correcto!"
            else:
                feedback = f"Incorrecto. Respuesta(s) correcta(s): \n {questions[idx]}:\n"
                for option in options[idx]:
                    if option[0] in list(correct_answers):
                        feedback = feedback + f"{option}\n"

            current_question_index += 1
            next_question, next_options, final_score = get_next_question()
            return next_question, next_options, feedback, final_score
        else:
            return "El cuestionario ha terminado.", [], "El cuestionario ya ha terminado."


    def reset_quiz():
        nonlocal current_question_index, score # ¡Importante!
        random.shuffle(question_indices)
        current_question_index = 0
        score = 0
        return get_next_question() + ("",)

    with gr.Blocks() as quiz_interface:
        question = gr.Textbox(label="Pregunta")
        options_group = gr.CheckboxGroup([], label="Opciones")
        feedback = gr.Textbox(label="Retroalimentación")
        final_score = gr.Textbox(label="Puntuación Final")

        next_question_btn = gr.Button("Enviar Respuesta")
        next_question_btn.click(
            submit_answer,
            inputs=options_group,
            outputs=[question, options_group, feedback, final_score],
        )

        reset_btn = gr.Button("Reiniciar Cuestionario")
        reset_btn.click(
            reset_quiz,
            outputs=[question, options_group, feedback, final_score],
        )

        question_text, options_test,_ = get_next_question()  # Inicializa la interfaz
        question.value = question_text
        options_group.choices = [[op, op] for op in options_test]

    return quiz_interface


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] [%(asctime)s] %(message)s")
    params = get_params(sys.argv[1:])
    questions, options, answers = extract_questions_from_pdf(**params)
    quiz_app = start_quiz(questions, options, answers)
    quiz_app.launch(debug=True, inbrowser=True, server_port=7860, share=True)
