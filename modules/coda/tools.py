
def DirectVerificationTool(exercise_type: str, user_answer: str, correct_answer_data: str) -> dict:
    """
    Evaluates the user's answer based on the exercise type.

    Args:
        exercise_type: The type of exercise ('multiple_choice' or 'fill_in_the_blank').
        user_answer: The answer submitted by the user.
        correct_answer_data: The correct answer.

    Returns:
        A dictionary with 'score' and 'feedback'.
    """
    is_correct = False

    if exercise_type == 'multiple_choice':
        is_correct = user_answer == correct_answer_data

    elif exercise_type == 'fill_in_the_blank':
        is_correct = user_answer.strip().lower() == correct_answer_data.strip().lower()

    else:
        return {"score": 0, "feedback": f"Error: Invalid exercise type '{exercise_type}' for DirectVerificationTool."}

    if is_correct:
        return {"score": 100, "feedback": "Correct!"}
    else:
        return {"score": 0, "feedback": "Incorrect. Please try again."}
