from RestrictedPython import compile_restricted, safe_globals
import traceback
def evaluate_code(user_code: str, test_cases_data: dict):
    """
    Evaluates user's Python code against a set of test cases using a sandbox.

    Args:
        user_code: The Python code submitted by the user as a string.
        test_cases_data: A dictionary containing the function name and test cases.
                         Example: {"function_name": "add", "test_cases": [{"input": [1, 2], "output": 3}]}

    Returns:
        A dictionary containing the final 'score' and detailed 'feedback'.
    """
    # --- SECURITY NOTE ---
    # This implementation now uses RestrictedPython to create a safer execution
    # environment. It prevents access to most dangerous built-ins. However, for a
    # true production system, running code in a fully isolated container (e.g., Docker)
    # is the recommended best practice for maximum security.

    passed_tests = 0
    feedback_details = []

    try:
        # Validate the input data structure
        if "test_cases" not in test_cases_data or "function_name" not in test_cases_data:
            return {"score": 0, "feedback": "Evaluation error: The 'test_cases_data' must include 'function_name' and 'test_cases'."}

        test_cases = test_cases_data["test_cases"]
        function_name = test_cases_data["function_name"]
        total_tests = len(test_cases)

        if total_tests == 0:
            return {"score": 100, "feedback": "No test cases were provided, so the submission is considered trivially correct."}

        # Compile the user's code in a restricted environment
        byte_code = compile_restricted(user_code, '<string>', 'exec')

        # Prepare a safe scope for the execution
        execution_scope = {}
        exec(byte_code, safe_globals, execution_scope)

        # Check if the required function exists in the scope
        if function_name not in execution_scope:
            return {"score": 5, "feedback": f"Error: The required function '{function_name}' was not found in your code. Please check the spelling."}

        user_function = execution_scope[function_name]

        # Loop through each test case and execute the function
        for i, test in enumerate(test_cases):
            test_input = test["input"]
            expected_output = test["output"]

            try:
                # Use argument unpacking (*) to pass inputs to the function
                actual_output = user_function(*test_input)

                if actual_output == expected_output:
                    passed_tests += 1
                    feedback_details.append(f"✅ Test {i+1}: Input {test_input} -> Passed!")
                else:
                    feedback_details.append(f"❌ Test {i+1}: Input {test_input} -> Failed. Expected '{expected_output}', but got '{actual_output}'.")
            except Exception as e:
                feedback_details.append(f"💥 Test {i+1}: Input {test_input} -> Error during execution: {e}")

    except Exception as e:
        return {"score": 0, "feedback": f"A critical error occurred during code compilation or setup: {e}"}

    # Calculate final score and compile feedback
    score = (passed_tests / total_tests) * 100
    summary = f"Passed {passed_tests} out of {total_tests} test cases."
    final_feedback = summary + "\n\n" + "\n".join(feedback_details)

    return {"score": round(score), "feedback": final_feedback}
