# actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, Restarted, FollowupAction
import requests
import random

API_BASE = "http://localhost:8000/api"

def get_auth_headers(tracker: Tracker) -> Dict[str, str]:
    # Try slot first, then message metadata
    token = (tracker.get_slot("jwt_token")
             or tracker.latest_message.get("metadata", {}).get("access_token"))
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

class ActionFetchQuestion(Action):
    def name(self) -> Text:
        return "action_fetch_question"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            exam_id = tracker.get_slot("exam_id") or "1"
            headers = get_auth_headers(tracker)

            r = requests.get(f"{API_BASE}/adaptive/next/{exam_id}/", headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()

            if data.get("done"):
                # Do NOT call a removed method; just inform & reset.
                msg = data.get("message") or "Exam complete."
                dispatcher.utter_message(text=f"🎉 {msg}")
                return [
                    SlotSet("question_id", None),
                    SlotSet("asked_count", 0.0),
                    SlotSet("total_questions", float(data.get("total_questions", 0)) if data.get("total_questions") is not None else 0.0),
                    SlotSet("difficulty", 2.0),
                    SlotSet("question_number", 0.0),
                    # do not reset score here; ActionCheckAnswer handles final saving/summary
                ]

            q = data["question"]
            options = {'A': q["option1"], 'B': q["option2"], 'C': q["option3"], 'D': q["option4"]}
            diff_map = {1: "Easy", 2: "Medium", 3: "Hard"}
            question_text = (
                f"({diff_map.get(int(data['current_difficulty']), 'Medium')}) "
                f"Question {int(data['asked_count'])}/{int(data['total_questions'])}:\n"
                f"{q['text']}\n\n" + "\n".join([f"{k}. {v}" for k, v in options.items()])
            )
            dispatcher.utter_message(text=question_text)

            return [
                SlotSet("question_id", str(q["id"])),
                SlotSet("asked_count", float(data["asked_count"])),
                SlotSet("total_questions", float(data["total_questions"])),
                SlotSet("difficulty", float(data["current_difficulty"]))
            ]

        except requests.exceptions.RequestException as e:
            dispatcher.utter_message(text="❌ Error connecting to the exam server. Please try again later.")
            print(f"API Connection Error: {str(e)}")
        except Exception as e:
            dispatcher.utter_message(text="❌ An unexpected error occurred.")
            print(f"Error: {str(e)}")

        return []

class ActionCheckAnswer(Action):
    def name(self) -> Text:
        return "action_check_answer"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            user_answer = (tracker.latest_message.get("text") or "").strip().upper()
            if user_answer not in ['A', 'B', 'C', 'D']:
                dispatcher.utter_message(text="⚠️ Please respond with only A, B, C, or D")
                return []

            exam_id = tracker.get_slot("exam_id") or "1"
            question_id = tracker.get_slot("question_id")
            if not question_id:
                dispatcher.utter_message(text="⚠️ I couldn't find the current question. Say 'start exam' to begin.")
                return []

            answer_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
            headers = get_auth_headers(tracker)
            response = requests.post(
                f"{API_BASE}/adaptive/check_answer/",
                headers=headers,
                json={
                    "exam_id": int(exam_id),
                    "question_id": int(question_id),
                    "answer": answer_map[user_answer],
                },
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            correct_option = chr(64 + int(result["correct_answer"]))
            current_score = float(tracker.get_slot("score") or 0.0)
            new_score = current_score + (1.0 if result["is_correct"] else 0.0)

            if result["is_correct"]:
                feedback = "✅ Correct! (+1 point)"
            else:
                encouragements = [
                    "Don't worry, you'll get the next one! 💪",
                    "Keep going, you're learning! 📘",
                    "Incorrect, but you're doing great. Try again! 🎯",
                    "Not quite, but don't give up! 🚀"
                ]
                feedback = f"❌ Incorrect. The correct answer was {correct_option}.\n{random.choice(encouragements)}"

            dispatcher.utter_message(
                text=f"{feedback}\nCurrent score: {int(new_score)} | Next difficulty: {int(result.get('current_difficulty', 2))}"
            )

            # If done, finalize & reset here using the *local* new_score (prevents off-by-one errors)
            if result.get("done"):
                final_score = int(new_score)
                total_q = int(result.get("total_questions", 0))

                try:
                    save_response = requests.post(
                        f"{API_BASE}/save_result/{exam_id}/",
                        headers=headers,
                        json={"score": final_score, "total_questions": total_q},
                        timeout=10
                    )
                    save_response.raise_for_status()
                except Exception as e:
                    dispatcher.utter_message(text="❌ Couldn't save your exam results. Please contact support.")
                    print(f"API Error: {str(e)}")

                percentage = (final_score / total_q) * 100 if total_q else 0.0
                end_msg = (
                    f"🎉 Exam Completed!\n\n"
                    f"Your score: {final_score}/{total_q}\n"
                    f"Percentage: {percentage:.1f}%\n\n"
                    f"Your result has been saved to your account."
                )
                if percentage >= 75:
                    end_msg += " Excellent work! 🏆"
                elif percentage >= 50:
                    end_msg += " Good job! 👍"
                else:
                    end_msg += " Keep practicing! 📚"
                dispatcher.utter_message(text=end_msg)

                return [
                    # clear exam state
                    SlotSet("score", 0.0),
                    SlotSet("question_id", None),
                    SlotSet("difficulty", 2.0),
                    SlotSet("asked_count", 0.0),
                    SlotSet("total_questions", 0.0),
                    SlotSet("question_number", 0.0),
                    Restarted(),
                ]

            # Not done yet → persist new state and immediately fetch the next question
            return [
                SlotSet("score", new_score),
                SlotSet("question_id", None),  # we're about to fetch a new one
                SlotSet("difficulty", float(result.get("current_difficulty", 2))),
                SlotSet("asked_count", float(result.get("asked_count", 0.0))),
                SlotSet("total_questions", float(result.get("total_questions", 0.0))),
                FollowupAction("action_fetch_question"),
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
