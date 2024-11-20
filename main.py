import streamlit as st
import sigfig

# Define function to count decimal places
def count_decimal_places(num):
    num_str = str(num)
    if '.' in num_str:
        return len(num_str.split('.')[1])
    return 0

# Preprocess absolute
def preprocess_absolute(expr):
    allpossibilities = []

    def find_abs(expr, curr, count):
        nonlocal allpossibilities
        if curr == len(expr):
            if count == 0:
                allpossibilities.append(expr)

            return
        if expr[curr] == "|":
            find_abs(expr[:curr] + "abs(" + expr[curr + 1:], curr + 1, count + 1)
            if count > 0:
                find_abs(expr[:curr] + ")" + expr[curr + 1:], curr + 1, count - 1)
        else:
            find_abs(expr, curr + 1, count)
    ans = None
    find_abs(expr, 0, 0)
    for i in allpossibilities:
        try:
            eval(i)
            return i
        except:
            pass
    return

# Replacing stings
def adjusted_string(calc):
    calc = calc.strip()
    calc = calc.replace('{', '(')
    calc = calc.replace('[', '(')
    calc = calc.replace('}', ')')
    calc = calc.replace(']', ')')
    calc = calc.replace('^', '**')
    calc = calc.replace('×', "*")
    calc = calc.replace(':', '/')
    calc = calc.replace("$", '')
    calc = calc.replace('%', '')
    calc = preprocess_absolute(calc)
    return calc


open_list = ["[", "{", "("]
close_list = ["]", "}", ")"]

# Function to check parentheses
def balanced_parenthesis(myStr):
    stack = []
    for i in myStr:
        if i in open_list:
            stack.append(i)
        elif i in close_list:
            pos = close_list.index(i)
            if ((len(stack) > 0) and
                    (open_list[pos] == stack[len(stack) - 1])):
                stack.pop()
            else:
                return False
    if len(stack) == 0:
        return True
    else:
        return False

# Define function to check decimals between two values
def check_for_final_decimal(initial_value, final_value):
    if initial_value == final_value:
        return True
    else:
        if count_decimal_places(initial_value) > 2:
            if initial_value < 0.01:
                return sigfig.round(initial_value, 2) == sigfig.round(final_value, 2)
            return abs(initial_value - final_value) < 0.01
        else:
            return False
def check_for_decimals(initial_value, final_value):
    if initial_value == final_value:
        return True
    else:
        if count_decimal_places(initial_value) > 2:
            if initial_value < 0.01:
                return sigfig.round(initial_value, 2) == sigfig.round(final_value, 2)
            return abs(initial_value - final_value) < 0.00001
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
            flag = flag&balanced_parenthesis(calc)
            calc = adjusted_string(calc)
            # st.markdown(calc)
            try:
                checks.append(float(eval(calc)))
            except:
                try:
                    checks.append(float(calc))
                except Exception as e:
                    pass

        st.markdown(checks)

        initial = None
        if len(checks) > 1:
            last = checks[-1]
            for current_val in checks:
                if initial is None:
                    initial = current_val
                elif current_val == last:
                    # check for decimals
                    flag = flag&check_for_final_decimal(initial, current_val)
                else:
                    if initial != current_val:
                        flag = flag&check_for_decimals(initial, current_val)

        if flag:
            results.append((row, "Correct"))
        else:
            results.append((row, "Incorrect"))
    return results

# Streamlit Interface
st.title("Step-by-Step Calculation Validator")

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
