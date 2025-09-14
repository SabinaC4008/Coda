import sys
from io import StringIO

def evaluate_code(user_code: str, test_cases_data: dict):
    results = []

    execution_scope = {}

    try:
        exec(user_code, {}, execution_scope)
    except Exception as e:
        error_message = f"Syntax Error or problem in code definition: {e}"
        for name in test_cases_data:
            results.append({"name": name, "status": "💥 Error", "details": error_message})
        return results

    # Now, loop through the test cases and call the function.
    for name, data in test_cases_data.items():
        result_details = {"name": name, "status": ""}

        original_stdout = sys.stdout
        captured_output_stream = StringIO()
        sys.stdout = captured_output_stream

        try:
            function_name = data["function_name"]
            func_to_call = execution_scope.get(function_name)

            # Check if the function was actually defined in the user's code
            if not func_to_call or not callable(func_to_call):
                raise NameError(f"Function '{function_name}' not found in the provided code.")

            # Call the function with the provided arguments
            actual_return = func_to_call(*data["args"])

            # Compare the return value
            if actual_return == data["expected_return"]:
                result_details["status"] = "✅ Passed"
            else:
                result_details["status"] = "❌ Failed"
                result_details["details"] = (
                    f"Expected return: {data['expected_return']} ({type(data['expected_return']).__name__}), "
                    f"Actual return: {actual_return} ({type(actual_return).__name__})"
                )

        except Exception as e:
            # This catches runtime errors when the function is called
            result_details["status"] = "💥 Error"
            result_details["details"] = f"An error occurred during execution: {e}"
        finally:
            # Always restore stdout and add any printed output to the details
            printed_output = captured_output_stream.getvalue()
            if printed_output:
                details = result_details.get("details", "")
                result_details["details"] = (details + f"\nPrinted output:\n{printed_output}").strip()
            sys.stdout = original_stdout

        results.append(result_details)

    # Calculate score and feedback
    passed = sum(1 for r in results if r["status"] == "✅ Passed")
    total = len(results)
    score = int((passed / total) * 100) if total > 0 else 0

    if score == 100:
        feedback = "Excellent! All test cases passed successfully."
    elif score >= 60:
        feedback = "Good job, but some test cases did not pass. Please review the details."
    else:
        feedback = "Several test cases failed or there were errors. Please review your code carefully."

    results_details = {"score": score, "feedback": feedback}

    return results_details



"""if __name__ == "__main__":
    results = evaluate_code(example_user_code, example_test_cases)
    for res in results:
        print(res)"""