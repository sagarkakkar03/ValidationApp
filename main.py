import streamlit as st
from simpleeval import simple_eval
import sigfig

# Define function to count decimal places
def count_decimal_places(num):
    num_str = str(num)
    if '.' in num_str:
        return len(num_str.split('.')[1])
    return 0


# Define function to check decimals between two values
def check_for_decimals(initial_value, final_value):
    if initial_value == final_value:
        return True
    else:
        if count_decimal_places(initial_value) > 2:
            if initial_value < 0.01:
                return sigfig(initial_value, 2) == sigfig.round(final_value, 2)
            return abs(initial_value - final_value) < 0.01
        else:
            return False

# Validate step-by-step calculations
def validate_steps_with_highlight(steps):
    results = []
    for row in steps:
        flag = True
        calculations = list(row.split("="))
        checks = []
        for calc in calculations:
            calc = calc.strip()
            new_calc = ""
            for text in calc:
                if text == "{" or text == "[":
                    new_calc += "("
                elif text == "}" or text == "]":
                    new_calc += ")"
                else:
                    new_calc += text
            calc = new_calc
            try:
                checks.append(float(simple_eval(calc)))
            except:
                try:
                    checks.append(float(calc))
                except Exception as e:
                    pass

        initial = None
        if len(checks) > 1:
            last = checks[-1]
            for current_val in checks:
                if initial is None:
                    initial = current_val
                elif current_val == last:
                    # check for decimals
                    flag = flag&check_for_decimals(initial, current_val)
                else:
                    if initial != current_val:
                        flag = False

        if flag:
            results.append((row, "Correct"))
        else:
            results.append((row, "Incorrect"))
    return results

# Streamlit Interface
st.title("Step-by-Step Calculation Validator with Highlighting")

st.write("Enter each step of your calculation in the format `expression = result` (e.g., `a + b = 47`). Separate steps with a newline.")
steps_input = st.text_area("Enter your calculations:", height=200)

if st.button("Validate"):
    if steps_input.strip():
        steps = steps_input.strip().split("\n")
        results = validate_steps_with_highlight(steps)
        st.subheader("Validation Results:")
        for step, status in results:
            if status == "Correct":
                st.markdown(f"<p style='color:green;'>{step} ✔</p>", unsafe_allow_html=True)
            elif status == "Incorrect":
                st.markdown(f"<p style='color:red;'>{step} ✖</p>", unsafe_allow_html=True)
            else:  # Invalid Format
                st.markdown(f"<p style='color:orange;'>{step} ⚠ Invalid Format</p>", unsafe_allow_html=True)
    else:
        st.warning("Please enter some calculations to validate.")
