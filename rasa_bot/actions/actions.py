from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Restarted
import requests
import random


class ActionFetchQuestion(Action):
    def name(self) -> Text:
        return "action_fetch_question"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            exam_id = tracker.get_slot("exam_id")
            question_num = tracker.get_slot("question_number") or 0
            score = tracker.get_slot("score") or 0

            total_response = requests.get("http://localhost:8000/api/count/1/count/")
            total_response.raise_for_status()
            total_questions = total_response.json()["count"]

            if question_num >= total_questions:
                return self._handle_exam_completion(dispatcher, exam_id, tracker)

            question_response = requests.get(f"http://localhost:8000/api/questions/1/{question_num}/")
            question_response.raise_for_status()
            response = question_response.json()

            options = {
                'A': response["option1"],
                'B': response["option2"],
                'C': response["option3"],
                'D': response["option4"]
            }

            question_text = (
                f"Question {question_num + 1}/{total_questions}: {response['text']}\n\n"
                + "\n".join([f"{key}. {value}" for key, value in options.items()])
                + "\n\nPlease answer with A, B, C, or D"
            )

            dispatcher.utter_message(text=question_text)

        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="❌ Error connecting to the exam server. Please try again later.")
            print(f"API Connection Error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text="❌ An unexpected error occurred.")
            print(f"Error: {str(e)}")

        return []

    def _handle_exam_completion(self, dispatcher: CollectingDispatcher, exam_id: int, tracker: Tracker):
        try:
            score = tracker.get_slot("score") or 0
            total_response = requests.get("http://localhost:8000/api/count/1/count/")
            total_response.raise_for_status()
            total_questions = total_response.json()["count"]

            percentage = (score / total_questions) * 100 if total_questions > 0 else 0

            feedback = (
                f"🎉 Exam Completed!\n\n"
                f"Your score: {int(score)}/{total_questions}\n"
                f"Percentage: {percentage:.1f}%\n\n"
            )

            if percentage >= 75:
                feedback += "Excellent work! 🏆"
            elif percentage >= 50:
                feedback += "Good job! 👍"
            else:
                feedback += "Keep practicing! 📚"

            dispatcher.utter_message(text=feedback)
            return [
                SlotSet("question_number", 0),
                SlotSet("score", 0),
                Restarted()
            ]

        except Exception as e:
            dispatcher.utter_message(text="❌ Couldn't calculate final score.")
            print(f"Scoring Error: {str(e)}")
            return []


class ActionCheckAnswer(Action):
    def name(self) -> Text:
        return "action_check_answer"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            user_answer = tracker.latest_message.get("text").strip().upper()
            exam_id = tracker.get_slot("exam_id")
            question_num = tracker.get_slot("question_number") or 0
            current_score = tracker.get_slot("score") or 0

            if user_answer not in ['A', 'B', 'C', 'D']:
                dispatcher.utter_message(text="⚠️ Please respond with only A, B, C, or D")
                return []

            answer_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
            response = requests.post(
                f"http://localhost:8000/api/check_answer/1/{question_num}/",
                json={"answer": answer_map[user_answer]},
            )
            response.raise_for_status()
            result = response.json()

            correct_option = chr(64 + result["correct_answer"])
            new_score = current_score + 1 if result["is_correct"] else current_score

            if result["is_correct"]:
                feedback = "✅ Correct! (+1 point)"
            else:
                encouragements = [
                    "Don't worry, you'll get the next one! 💪",
                    "Keep going, you're learning! 📘",
                    "Incorrect, but you’re doing great. Try again! 🎯",
                    "Not quite, but don’t give up! 🚀"
                ]
                feedback = f"❌ Incorrect (Correct: {correct_option})\n{random.choice(encouragements)}"

            dispatcher.utter_message(text=f"{feedback}\nCurrent score: {int(new_score)}")

            return [
                SlotSet("question_number", question_num + 1),
                SlotSet("score", new_score)
            ]

        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="⚠️ Error connecting to the exam server.")
            print(f"API Connection Error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text="⚠️ An unexpected error occurred.")
            print(f"Error: {str(e)}")

        return []


class ActionGreetAndPrompt(Action):
    def name(self) -> Text:
        return "action_greet_and_prompt"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        dispatcher.utter_message(text="👋 Hello! Welcome to the DOU Exam Bot.")
        dispatcher.utter_message(text="When you're ready, type 'start exam' to begin.")
        return []
