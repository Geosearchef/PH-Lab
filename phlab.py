import gradio as gr
from ciphers import all_ciphers
from dictionary import AnagramLookupTable, dictionary_all, dictionary_popular, find_words_by_regex
from analysis import bruteforce_string_filter_sort, analyze_frequencies, calculate_entropy
import re
import time

#redirect_to_light_js = "window.addEventListener('load', function () {gradioURL = window.location.href; if (!gradioURL.endsWith('?__theme=light')) {window.location.replace(gradioURL + '?__theme=dark');}});"

# Cipher

def run_cipher(input_cipher_index: int, input_key: str, output_cipher_index: int, output_key: str, input_text: str) -> str:
    if len(input_text) > 3000:
        return "Input too long"
    if len(input_text) > 300 and input_key == "all":
        return "Input too long"

    input_cipher = all_ciphers[input_cipher_index]
    output_cipher = all_ciphers[output_cipher_index]

    data = input_cipher.decode(input_text, input_key)
    if isinstance(data, list):
        data = "\n".join([b.decode("utf-8") for b in data]).encode("utf-8")
    output_text = output_cipher.encode(data, output_key)
    if isinstance(output_text, list):
        output_text = "\n".join(output_text)

    return output_text


#available_ciphers = ["Text", "Numbers", "Cesar", "Tap", "Morse"]
cipher_names = [c.name for c in all_ciphers]

# Analysis

def brute_force_input(input: str) -> str:
    timeout_stamp = time.time() + 30.0
    results = bruteforce_string_filter_sort(input, timeout_stamp=timeout_stamp, total_iterations=3)
    result_string = "\n".join([str(r) for r in results]) if len(results) != 0 else "No results found"
    
    if time.time() > timeout_stamp:
        result_string = "Maximum computation time exceeded!\n\n" + result_string

    return result_string


def statistical_text_analysis(input: str) -> tuple[dict[str, float], str]:
    if input == "":
        return {}, ""

    freqs_by_symbol = analyze_frequencies(input)
    
    if len(freqs_by_symbol) == 0:
        return {}, ""

    num_symbols = sum(freqs_by_symbol.values())
    max_freq = max(freqs_by_symbol.values())

    norm_freqs = {s: freqs_by_symbol[s] / num_symbols for s in freqs_by_symbol}
    top_norm_freqs = {s: freqs_by_symbol[s] / max_freq for s in freqs_by_symbol}

    entropy = calculate_entropy(probs=list(norm_freqs.values()))

    return norm_freqs, f"{entropy:.3}"


# Dictionary

anagram_lookup_table_all = AnagramLookupTable(dictionary_all)
anagram_lookup_table_common = AnagramLookupTable(dictionary_popular)

def lookup_anagram(anagram: str, limit_to_common: bool) -> str:
    lookup_table = anagram_lookup_table_all if not limit_to_common else anagram_lookup_table_common
    solutions = lookup_table.lookup(anagram.replace(" ", ""))
    return f"{len(solutions)} results found:\n\n{'\n'.join(solutions)}" if solutions is not None else f"No results found for '{anagram}'"

def find_word(search_string: str, limit_to_common: bool) -> str:
    results = find_words_by_regex(re.compile(search_string, re.IGNORECASE), dictionary_all if not limit_to_common else dictionary_popular)
    return f"{len(results)} words found:\n\n{'\n'.join(results)}" if len(results) != 0 else f"No results found for '{search_string}'"


# Base converter

def int_to_base(n: int, base: int) -> str:
    convertString = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = ""

    while n > 0:
        result = convertString[n % base] + result
        n = n // base

    return result

def convert_base(input: str, in_base: str, out_base: str) -> str:
    try:
        return " ".join([int_to_base(int(num, int(in_base)), int(out_base)) for num in input.split()])
    except ValueError:
        return "Invalid"




css = """
.small-button { max-width: 2.8em; min-width: 2.8em !important; align-self: center; }
.centered-checkbox > label {  }
.label-no-heading > div > h2 { display: none; }
.top-margin { margin-top: 30pt; }
"""

with gr.Blocks(css=css, theme=gr.themes.Default()) as app:
    gr.Markdown("# Puzzle Hunt Laboratory")
    with gr.Tab("Ciphers"):
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    base_selector_left = gr.Radio(cipher_names, value=cipher_names[1], type="index", interactive=True, show_label=False)
                    base_run_button_left = gr.Button("➡️", elem_classes=["small-button"], variant="secondary", scale=0)
                base_text_area_left = gr.TextArea(interactive=True, show_label=False, show_copy_button=True)
                left_key_area = gr.Textbox(label="Key", interactive=True)
            with gr.Column():
                with gr.Row():
                    base_run_button_right = gr.Button("⬅️", elem_classes=["small-button"], scale=0)
                    base_selector_right = gr.Radio(cipher_names, value=cipher_names[0], type="index", interactive=True, show_label=False)
                
                right_text_area = gr.TextArea(interactive=True, show_label=False, show_copy_button=True)
                right_key_area = gr.Textbox(label="Key", interactive=True)
        
        base_selector_left.select(
            fn=lambda cindex, key: "all" if cindex == cipher_names.index("Caesar") and not key.isnumeric() else key,
            inputs=[base_selector_left, left_key_area],
            outputs=[left_key_area]
        )
        base_selector_right.select(
            fn=lambda cindex, key: "all" if cindex == cipher_names.index("Caesar") and not key.isnumeric() else key,
            inputs=[base_selector_right, right_key_area],
            outputs=[right_key_area]
        )
        
        # run the ciphers
        gr.on(
            triggers=[base_run_button_left.click, base_text_area_left.input, left_key_area.input],
            fn=run_cipher,
            inputs=[base_selector_left, left_key_area, base_selector_right, right_key_area, base_text_area_left],
            outputs=[right_text_area]
        )
        gr.on(
            triggers=[base_run_button_right.click, right_text_area.input, right_key_area.input],
            fn=run_cipher,
            inputs=[base_selector_right, right_key_area, base_selector_left, left_key_area, right_text_area],
            outputs=[base_text_area_left]
        )
    
    
    with gr.Tab("Analysis"):
        with gr.Row():
            with gr.Column():
                analysis_input = gr.Textbox(interactive=True, label="Input", placeholder="Input a single word")
                analysis_solve_button = gr.Button("Do Magic", variant="primary")

                entropy_label = gr.Label(container=True, label="Entropy - language = 3.6 - 4.2", elem_classes=["top-margin"])                
                frequency_bins = gr.Label(value={}, label="Frequency Analysis", num_top_classes=10, container=False, elem_classes=["label-no-heading"])
                #gr.Markdown("Entropy of natural language: 3.5 - 4.2")


            with gr.Column():
                analysis_output = gr.TextArea(label="Output", interactive=False)

        gr.on(
            triggers=[analysis_input.submit, analysis_solve_button.click],
            fn=brute_force_input,
            inputs=[analysis_input],
            outputs=[analysis_output]
        )
        analysis_input.change(
            fn=statistical_text_analysis,
            inputs=[analysis_input],
            outputs=[frequency_bins, entropy_label]
        )

    with gr.Tab("Anagram"):
        with gr.Row():
            anagram_input = gr.Textbox(interactive=True, label="Anagram", placeholder="tbr?tu")
            anagram_limit_common = gr.Checkbox(label="Limit to common words", value=False, interactive=True, scale=0, elem_classes=["centered-checkbox"])
        anagram_solve_button = gr.Button("Lookup", variant="primary")
        anagram_output = gr.TextArea(label="Solutions", interactive=False)

        gr.on(
            triggers=[anagram_input.submit, anagram_solve_button.click],
            fn=lookup_anagram,
            inputs=[anagram_input, anagram_limit_common],
            outputs=[anagram_output]
        )

    with gr.Tab("Dictionary"):
        with gr.Row():
            dictionary_input = gr.Textbox(interactive=True, label="Regular Expression", placeholder="wa.+(er|it)")  # alternative: w.ter.rop
            dictionary_limit_common = gr.Checkbox(label="Limit to common words", value=False, interactive=True, scale=0, elem_classes=["centered-checkbox"])
        dictionary_solve_button = gr.Button("Search", variant="primary")
        dictionary_output = gr.TextArea(label="Results", interactive=False)

        gr.on(
            triggers=[dictionary_input.submit, dictionary_solve_button.click],
            fn=find_word,
            inputs=[dictionary_input, dictionary_limit_common],
            outputs=[dictionary_output]
        )

    with gr.Tab("Base Converter"):
        bases = [10, 2, 16, 8]

        with gr.Row():
            with gr.Column():
                with gr.Row():
                    selector_by_base = { base: gr.Button(str(base), elem_classes=["small-button"], variant="secondary", scale=0) for base in bases }
                    base_key_left = gr.Textbox(interactive=True, show_label=False, value="10")
                    base_run_button_left = gr.Button("➡️", elem_classes=["small-button"], variant="secondary", scale=0)

                    for base in bases:
                        selector_by_base[base].click(lambda b=base: str(b), inputs=[], outputs=[base_key_left])
                    
                base_text_area_left = gr.TextArea(interactive=True, show_label=False, show_copy_button=True)
            with gr.Column():
                with gr.Row():
                    base_run_button_right = gr.Button("⬅️", elem_classes=["small-button"], variant="secondary", scale=0)
                    base_key_right = gr.Textbox(interactive=True, show_label=False, value="10")
                    selector_by_base = { base: gr.Button(str(base), elem_classes=["small-button"], variant="secondary", scale=0) for base in bases }

                    for base in bases:
                        selector_by_base[base].click(lambda b=base: str(b), inputs=[], outputs=[base_key_right])

                base_text_area_right = gr.TextArea(interactive=True, show_label=False, show_copy_button=True)

        
        # run the ciphers
        gr.on(
            triggers=[base_run_button_left.click, base_text_area_left.input],
            fn=convert_base,
            inputs=[base_text_area_left, base_key_left, base_key_right],
            outputs=[base_text_area_right]
        )
        gr.on(
            triggers=[base_run_button_right.click, base_text_area_right.input],
            fn=convert_base,
            inputs=[base_text_area_right, base_key_right, base_key_left],
            outputs=[base_text_area_left]
        )
    
    with gr.Tab("Have you googled it?"):
        gr.Markdown("""No? Then maybe it's time to do so.
                    - ISBN
                    - IP address
                    - phone numbers
                    - Coordinates
                    
                    **Take a look at the cheatsheet Brainstorming section.**
                    """)


demo = app

print("Launching webapp")
app.launch()

