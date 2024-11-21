import logging
import os
import sys
from attr import attrs, attrib
from sample_questions_pmle.utils import extract_questions_from_pdf, get_params

import random
import gradio as gr


@attrs
class QuizzPMLE:
    questions = attrib(type=list[str], init=True)
    options = attrib(type=list[list[str]], init=True)
    answers = attrib(type=list[list[str]], init=True)

    current_question_index = attrib(type=int, init=False, default=0)
    score = attrib(type=int, init=False, default=0)

    def __call__(self, **kwargs):
        interface = self.create_interface()
        return interface.launch(**kwargs)

    def format_options_group(self, options_group: list) -> gr.CheckboxGroup:
        """
        Formatea la estructura del options_group para que devuelva las opciones
        desmarcadas en la interfaz.

        Parameters
        ----------
        options_group: list
            Lista de opciones

        Returns
        -------
        new_options_group: gr.CheckboxGroup
            Nuevo CheckboxGroup formateado.
        """
        new_options_group = gr.CheckboxGroup(
            choices=[[op, op] for op in options_group],
            label="Opciones", value=[])
        return new_options_group

    def create_interface(self):
        with gr.Blocks() as quiz_interface:
            question = gr.Textbox(label="Pregunta")
            options_group = gr.CheckboxGroup([], label="Opciones", value=[])
            feedback = gr.Textbox(label="Retroalimentación")
            final_score = gr.Textbox(label="Puntuación Final")

            next_question_btn = gr.Button("Enviar Respuesta")
            next_question_btn.click(
                self.submit_answer,
                inputs=options_group,
                outputs=[question, options_group, feedback, final_score],
            ).then(
                self.format_options_group,
                inputs=options_group,
                outputs = [options_group]
            )

            reset_btn = gr.Button("Reiniciar Cuestionario")
            reset_btn.click(
                self.reset_quiz,
                outputs=[question, options_group, feedback, final_score],
            ).then(
                self.format_options_group,
                inputs=options_group,
                outputs = [options_group]
            )

            question_text, options_test, _ = self.get_next_question()  # Inicializa la interfaz
            question.value = question_text
            options_group.choices = [[op, op] for op in options_test]
            options_group.values = []
        return quiz_interface

    def get_total_score(self) -> float:
        """
        Función que devuelve el score total.
        """
        if self.current_question_index > 0:
            return self.score / self.current_question_index
        return 0

    def get_next_question(self) -> tuple[str, list[str], str]:
        """
        Función que devuelve la siguiente pregunta.

        Returns
        -------
        question_text: str
            Texto de la nueva pregunta
        options_test: list[str]
            Lista con las opciones de respuesta.
        scoring: str
            Texto con la puntuación.

        """
        question_indices = list(range(len(self.questions)))
        if self.current_question_index < len(self.questions):
            idx = question_indices[self.current_question_index]
            question_text = (f"Pregunta {self.current_question_index + 1} "
                             f"(page {idx * 2 + 1}):\n{self.questions[idx]}\n")
            option_texts = self.options[idx]
            options_test = []
            for option in option_texts:
                question_text = question_text + f"\n {option}"
                options_test.append(option[0])
            final_score = self.get_total_score()
            return question_text, options_test, f"Puntuación: {final_score}"
        else:
            final_score = self.get_total_score()
            return "El cuestionario ha terminado.", [], f"Puntuación final: {final_score}"

    def submit_answer(self, user_input: list) -> tuple[str, list[str],str, str]:
        """
        Método que comprueba si la respuesta es correcta y devuelve la siguiente pregunta
        actualizando el score.

        Parameters
        ----------
        user_input: list
            Lista de opciones marcadas

        Returns
        -------
        question_text: str
            Texto de la nueva pregunta
        options_test: list[str]
            Lista con las opciones de respuesta.
        feedback: str
            Feedback de la respuesta
        scoring: str
            Texto con la puntuación.
        """
        question_indices = list(range(len(self.questions)))
        if self.current_question_index < len(self.questions):
            idx = question_indices[self.current_question_index]
            user_selection = set(user_input[0::2])
            correct_answers = set(self.answers[idx])

            if user_selection == correct_answers:
                self.score += 1
                feedback = "¡Correcto!"
            else:
                feedback = f"Incorrecto. Respuesta(s) correcta(s): \n {questions[idx]}:\n"
                for option in self.options[idx]:
                    if option[0] in list(correct_answers):
                        feedback = feedback + f"{option}\n"

            self.current_question_index += 1
            next_question, next_options, final_score = self.get_next_question()
            return next_question, next_options, feedback, final_score
        else:
            return "El cuestionario ha terminado.", [], "El cuestionario ya ha terminado.", ""

    def reset_quiz(self) -> tuple[str, list[str],str, str]:
        """
        Función que resetea la encuesta

        Returns
        -------
        question_text: str
            Texto de la nueva pregunta
        options_test: list[str]
            Lista con las opciones de respuesta.
        feedback: str
            Feedback de la respuesta
        scoring: str
            Texto con la puntuación.

        """
        question_indices = list(range(len(self.questions)))
        random.shuffle(question_indices)
        self.current_question_index = 0
        self.score = 0
        next_question, next_options, final_score = self.get_next_question()
        return next_question, next_options, "", final_score


if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] [%(asctime)s] %(message)s")
    params = get_params(sys.argv[1:])
    questions, options, answers = extract_questions_from_pdf(**params)
    quiz_app = QuizzPMLE(questions, options, answers)
    quiz_app(debug=True, inbrowser=True, server_port=7860, share=True)
