import streamlit as st
import sigfig
from decimal import Decimal, ROUND_HALF_UP
import re
from st_copy_to_clipboard import st_copy_to_clipboard

# Define function to count decimal places
def count_decimal_places(num):
    num_str = str(num)
    if '.' in num_str:
        return len(num_str.split('.')[1])
    return 0


def format_calculations():
    formatted_text = re.sub(r'\*', '×', st.session_state.steps_input)  # Replace * with × for multiplication
    formatted_text = re.sub(r'(\d),(\d)', r'\1\2', formatted_text)  # Remove commas within numbers
    formatted_text = re.sub(r'\s*=\s*', ' = ', formatted_text)  # Ensure spacing around "="
    formatted_text = re.sub(r'\s*([+\-×/^/])\s*', r'\1', formatted_text)  # Remove spaces around operators
    formatted_text = re.sub(r'= ?(-?\d)', r'= \1', formatted_text)  # Ensure space after "="
    st.session_state.steps_input = formatted_text

    return formatted_text

def replace_square_root(expression):
    """
    Replaces square root symbols (√) in the expression with Python's '**0.5'.
    Handles square roots with and without parentheses, and supports nested parentheses.
    """
    # Iterate through the expression to replace occurrences of √
    while '√' in expression:
        # Find the index of the square root symbol
        index = expression.find('√')

        # Check if the square root has parentheses
        if index + 1 < len(expression) and expression[index + 1] == '(':
            # Use a stack to find the corresponding closing parenthesis
            open_paren = index + 1
            stack = []
            close_paren = -1

            # Traverse the expression after the '(' to find the matching ')'
            for i in range(open_paren, len(expression)):
                if expression[i] == '(':
                    stack.append(i)  # Push the index of '(' onto the stack
                elif expression[i] == ')':
                    stack.pop()  # Pop the stack when encountering ')'
                    if not stack:
                        close_paren = i
                        break

            # If a valid closing parenthesis is found
            if close_paren != -1:
                inner_expression = expression[open_paren + 1: close_paren]
                # Replace √(inner_expression) with (inner_expression)**0.5
                expression = expression[:index] + f"({inner_expression})**0.5" + expression[close_paren + 1:]
        else:
            # Handle the case where there are no parentheses after √
            start = index + 1
            end = start

            # Find where the number ends (assume no space in between)
            while end < len(expression) and (expression[end].isdigit() or expression[end] == '.'):
                end += 1

            # Replace √N with (N)**0.5
            number = expression[start:end]
            expression = expression[:index] + f"({number})**0.5" + expression[end:]

    return expression


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

    find_abs(expr, 0, 0)
    for i in allpossibilities:
        try:
            eval(i)
            return i
        except:
            pass
    return

def custom_round(number, decimals=0):
    multiplier = Decimal('1.' + '0' * decimals)  # Create a decimal
    rounded_number = Decimal(str(number)).quantize(multiplier, rounding=ROUND_HALF_UP)
    return float(rounded_number)


def to_new_string(text):
    """
    Converts a given text to its superscript representation.
    Only digits and a few characters are supported.
    """
    # Unicode superscript mapping
    script_map = {
        '⁰': '**0', '¹': '**1', '²': '**2', '³': '**3', '⁴': '**4',
        '⁵': '**5', '⁶': '**6', '⁷': '**7', '⁸': '**8', '⁹': '**9', '{': '(', '[': '(', ']': ')', '}': ')', '^': '**', '×': '*', ':': '/', '$': '', '%': '', '−': '-', '°': ''
    }

    # Convert the input text using the mapping
    return ''.join(script_map[char] if char in script_map else char for char in text)


# Replacing stings
def adjusted_string(calc):
    calc = calc.strip()
    calc = to_new_string(calc)
    calc.replace('sqrt', '√')
    calc.replace('Sqrt', '√')
    calc.replace('SQRT', '√')
    calc = replace_square_root(calc)
    calc = preprocess_absolute(calc)
    return calc






# Function to check parentheses
def balanced_parenthesis(myStr):
    open_list = ["[", "{", "("]
    close_list = ["]", "}", ")"]
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

#later
def handle_root(string):
    for i in range(string):
        stack = []
        if string[i] =='√':
            stack.append(1)
    return

# Define function to check decimals between two values
def check_for_final_decimal(initial_value, final_value):
    if initial_value == final_value:
        return True
    else:
        if count_decimal_places(initial_value) > 2:
            if abs(initial_value) < 0.01:
                return sigfig.round(initial_value, 2) == sigfig.round(final_value, 2)

            return custom_round(initial_value, 2) == custom_round(final_value, 2)
        else:
            return False
def check_for_decimals(initial_value, final_value):
    if initial_value == final_value:
        return True
    else:
        if count_decimal_places(initial_value) > 2:
            if abs(initial_value) < 0.01:
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

if "steps_input" not in st.session_state:
    st.session_state.steps_input = ""

st.write("Enter each step of your calculation in the format `expression = result` (e.g., `a + b = 47`). Separate steps with a newline.")

# Use key to bind text_area to session_state
 # Create layout for text area + copy button

st.text_area("Enter your calculations:", value=st.session_state.steps_input, height=200, key="steps_input")


steps_input = st.session_state.steps_input
# Button triggers the format function
col1, col2 = st.columns([0.9, 0.1])
with col1:
    x = st.button("Validate", on_click=format_calculations, key="validate_button")
with col2:
    st_copy_to_clipboard(st.session_state.steps_input)


if x:
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


from math import gcd


def simplify_ratio(a, b):
    # Convert inputs to Decimal for higher precision
    # Scale both numbers to avoid floating point precision issues
    scale = 10**6
    a_scaled = int(a * scale)
    b_scaled = int(b * scale)

    # Find the greatest common divisor (GCD)
    common_divisor = gcd(a_scaled, b_scaled)

    # Simplify the ratio
    simplified_a = a_scaled // common_divisor
    simplified_b = b_scaled // common_divisor

    return simplified_a, simplified_b


# Streamlit UI
st.title("Ratio Simplifier")

# User input for floats as text and convert to float
float1 = st.text_input("Numerator")
float2 = st.text_input("Denominator")

# Process inputs when both are entered
if st.button("Calculate Simplified Ratio"):
    if float1 and float2:
        try:
            # Convert the inputs to float
            float1 = float(float1)
            float2 = float(float2)

            # Calculate simplified ratio
            simplified_a, simplified_b = simplify_ratio(float1, float2)

            # Display the simplified ratio
            st.write(f"The simplified ratio of {float1} and {float2} is: {simplified_a}:{simplified_b}")
            # st.write(gcd(int(float1 * 10**20), int(float2 * 10**20)))
        except ValueError:
            st.error("Please enter valid numbers.")
    else:
        st.warning("Please enter both float values to calculate the ratio.")
st.write("Note: Valid up to 8 decimal places.")

st.title("Text to Markdown Converter")

# User input for text
user_text = st.text_area("Enter text to convert to Markdown:")

if st.button("Convert to Markdown"):
    if user_text:
        # Display converted text as Markdown
        st.markdown(user_text)
    else:
        st.warning("Please enter some text to convert.")
