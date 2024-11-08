import gradio as gr
from setuptools.command.rotate import rotate

from ciphers import all_ciphers
from dictionary import AnagramLookupTable, dictionary_all, dictionary_popular, find_words_by_regex, T9LookupTree
from analysis import bruteforce_string_filter_sort, analyze_frequencies, calculate_entropy, is_isbn
from evaluation import eval_expression
from oeis import oeis_database
from grid_search import find_rotated_grid_words
import re
import time
from config import config

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

# T9


# Calculator

def run_calculation(expr: str, password: str) -> str:
    if not "calculator_password" in config or config["calculator_password"] not in password.lower():
        return "Wrong passcode"
    return eval_expression(expr)


# Indexing

def index_words(words: str, indices: str, include_spaces: bool) -> str:
    if not include_spaces:
        words = words.replace(" ", "")

    words_list, indices_list = words.split("\n"), indices.split("\n")
    if len(indices_list) == 1 and len(words_list) > 1:
        indices_list *= len(words_list)
    elif len(words_list) == 1 and len(indices_list) > 1:
        words_list *= len(indices_list)

    if len(words_list) != len(indices_list):
        return "Error: Number of words and indices must be the same"
    
    try:
        return "\n".join([f"{words_list[i][int(indices_list[i]) - 1]}   -   {words_list[i]}[{int(indices_list[i])}]" for i in range(len(words_list)) if int(indices_list[i]) - 1 < len(words_list[i])])
    except ValueError as e:
        return "Error: Indices must be integers"


# Word grid

def solve_word_grid(input_grid: str, all_rots: bool, reverse: bool) -> tuple[str, str]:
    input_grid = input_grid.strip()
    input_grid = input_grid.replace(" ", "").lower()

    if len(input_grid) == 0:
        return "", ""

    results = find_rotated_grid_words(input_grid, rotate=all_rots, reverse=reverse)

    output_grid = input_grid
    if len(results) != 0 and results[0].x != -1: # catch invalid
        matched_locations = [(x, res.y) for res in results for x in range(res.x, res.x + len(res.word)) if res.orientation == "horizontal"] + [(res.x, y) for res in results for y in range(res.y, res.y + len(res.word)) if res.orientation == "vertical"]
    else:
        matched_locations = []

    output_grid = "\n".join("   ".join([c.upper() if (col_index, row_index) in matched_locations else "_" for col_index, c in enumerate(row)]) for row_index, row in enumerate(output_grid.split("\n")))


    return output_grid, "\n".join([f"{res.word} - ({res.x+1},{res.y+1}) - {res.orientation} - rot {res.rot}{f" - reversed" if res.reversed else ""}" for res in results])

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
        if int(in_base) < 2 or int(out_base) < 2 or int(in_base) > 36 or int(out_base) > 36:
            return "Invalid base"
    
        return " ".join([int_to_base(int(num, int(in_base)), int(out_base)) for num in input.split()])
    except ValueError:
        return "Invalid"

# ISBN

def verify_isbns(isbns: str) -> str:
    isbns = [s.strip().replace("-", "").replace(" ", "") for s in isbns.split("\n")]

    return "\n".join([f"Yes ({candidate})" if is_isbn(candidate, dictionary_popular) else "No" for candidate in isbns])


# OEIS

def lookup_oeis_seq(sequence: str) -> str:
    if len(sequence) < 9:
        return "Sequence too short"
    results = [f"{id}:   {s}" for id, s in oeis_database.lookup_by_sequence(sequence.strip())]
    return "\n".join(results) if len(results) > 0 else "No results found"

def lookup_oeis_id(id: str) -> str:
    res = oeis_database.lookup_by_index(id)
    return res if res is not None else "ID not found"


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
                    cipher_selector_left = gr.Radio(cipher_names, value=cipher_names[0], type="index", interactive=True, show_label=False)
                    cipher_run_button_left = gr.Button("➡️", elem_classes=["small-button"], variant="secondary", scale=0)
                cipher_text_area_left = gr.TextArea(interactive=True, show_label=False, show_copy_button=True)
                cipher_key_area_left = gr.Textbox(label="Key", interactive=True)
            with gr.Column():
                with gr.Row():
                    cipher_swap_input_button_right = gr.Button("🔄", elem_classes=["small-button"], scale=0)
                    cipher_selector_right = gr.Radio(cipher_names, value=cipher_names[0], type="index", interactive=True, show_label=False)
                
                cipher_text_area_right = gr.TextArea(interactive=False, show_label=False, show_copy_button=True)
                cipher_key_area_right = gr.Textbox(label="Key", interactive=True)
        
        def get_key(cindex, key):
            if cindex == cipher_names.index("Caesar") and not key.isnumeric():
                return "all"
            if cindex == cipher_names.index("T9") and not key == "common" and not key == "all" and not key == "uncommon":
                return "common"
            return key

        cipher_selector_left.select(
            fn=get_key,
            inputs=[cipher_selector_left, cipher_key_area_left],
            outputs=[cipher_key_area_left]
        )
        cipher_selector_right.select(
            fn=get_key,
            inputs=[cipher_selector_right, cipher_key_area_right],
            outputs=[cipher_key_area_right]
        )
        
        # run the ciphers
        gr.on(
            triggers=[cipher_run_button_left.click, cipher_text_area_left.change, cipher_key_area_left.input, cipher_selector_left.select, cipher_selector_right.select, cipher_key_area_right.input],
            fn=run_cipher,
            inputs=[cipher_selector_left, cipher_key_area_left, cipher_selector_right, cipher_key_area_right, cipher_text_area_left],
            outputs=[cipher_text_area_right]
        )
        # gr.on(
        #     triggers=[base_run_button_right.click, right_text_area.input, right_key_area.input],
        #     fn=run_cipher,
        #     inputs=[base_selector_right, right_key_area, base_selector_left, left_key_area, right_text_area],
        #     outputs=[base_text_area_left]
        # )

        # swap inputs
        cipher_swap_input_button_right.click(
            fn=lambda t, r, l, kr, kl: (t, cipher_names[r], cipher_names[l], kr, kl),
            inputs=[cipher_text_area_right, cipher_selector_right, cipher_selector_left, cipher_key_area_right, cipher_key_area_left],
            outputs=[cipher_text_area_left, cipher_selector_left, cipher_selector_right, cipher_key_area_left, cipher_key_area_right]
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
    
    with gr.Tab("Calculator"):
        with gr.Row():
            with gr.Column():
                calculator_input = gr.Textbox(label="Input", placeholder="Enter a mathematical expression")
                calculator_solve_button = gr.Button("Compute", variant="primary")
                calculator_passcode = gr.Textbox(label="Passcode", placeholder="Enter team")
            calculator_output = gr.Textbox(label="Results", interactive=False)

        gr.on(
            triggers=[calculator_input.submit, calculator_solve_button.click],
            fn=run_calculation,
            inputs=[calculator_input, calculator_passcode],
            outputs=[calculator_output]
        )

    with gr.Tab("Indexing"):
        with gr.Column():
            with gr.Row():
                indexing_words_input = gr.TextArea(label="Words", placeholder="Words separated by newline")
                indexing_indices_input = gr.TextArea(label="Indices", placeholder="Indices separated by newline")
                indexing_output = gr.TextArea(label="Results", interactive=False)
            
            indexing_include_spaces_checkbox = gr.Checkbox(label="Include spaces", value=False)
            gr.Markdown("Note: Indices are 1-based")
        
        gr.on(
            triggers=[indexing_words_input.change, indexing_indices_input.change, indexing_include_spaces_checkbox.change],
            fn=index_words,
            inputs=[indexing_words_input, indexing_indices_input, indexing_include_spaces_checkbox],
            outputs=[indexing_output]
        )

    with gr.Tab("Word Grid"):
        with gr.Column():
            with gr.Row():
                grid_input = gr.TextArea(label="Grid", placeholder="Grid of letters")
                grid_output = gr.TextArea(label="Output", interactive=False)
                grid_result_output = gr.TextArea(label="Results", interactive=False)

            grid_search_all_rots = gr.Checkbox(label="Search all rotations")
            grid_include_reverse = gr.Checkbox(label="Include reverse")

            gr.on(
                triggers=[grid_input.change, grid_search_all_rots.change, grid_include_reverse.change],
                fn=solve_word_grid,
                inputs=[grid_input, grid_search_all_rots, grid_include_reverse],
                outputs=[grid_output, grid_result_output]
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
                    base_swap_inputs_right = gr.Button("🔄", elem_classes=["small-button"], variant="secondary", scale=0)
                    base_key_right = gr.Textbox(interactive=True, show_label=False, value="10")
                    selector_by_base = { base: gr.Button(str(base), elem_classes=["small-button"], variant="secondary", scale=0) for base in bases }

                    for base in bases:
                        selector_by_base[base].click(lambda b=base: str(b), inputs=[], outputs=[base_key_right])

                base_text_area_right = gr.TextArea(interactive=False, show_label=False, show_copy_button=True)

        
        # run the ciphers
        gr.on(
            triggers=[base_run_button_left.click, base_text_area_left.change, base_key_left.change, base_key_right.change],
            fn=convert_base,
            inputs=[base_text_area_left, base_key_left, base_key_right],
            outputs=[base_text_area_right]
        )
        # gr.on(
        #     triggers=[base_swap_inputs_right.click, base_text_area_right.input],
        #     fn=convert_base,
        #     inputs=[base_text_area_right, base_key_right, base_key_left],
        #     outputs=[base_text_area_left]
        # )

        base_swap_inputs_right.click(
            fn=lambda t, r, l: (t, r, l),
            inputs=[base_text_area_right, base_key_right, base_key_left],
            outputs=[base_text_area_left, base_key_left, base_key_right]
        )

    with gr.Tab("ISBN"):
        with gr.Row():
            with gr.Column():
                isbn_input = gr.TextArea(interactive=True, show_label=False, show_copy_button=False)
                isbn_submit = gr.Button("Verify checksums", variant="primary")

                gr.Markdown("""
                ### ISBNs
                An ISBN has **13 characters**. Before 2007, it had **10 characters**.
                
                The last digit is the checksum, which is between 0 - 10, 10 is indicated as `X`.
                
                #### Conversion
                Convert from 10 to 13 by prepending `978`.
                
                #### Checksum
                a + 3b + c + 3d + e + 3f + g + 3h + i + 3j + k + 3l + m ≡ 0   mod 10
                
                Here, m is the last digit and therefore checksum.
                
                #### Misc
                *ISBNs can be Barcodes!*
                
                [https://en.wikipedia.org/wiki/ISBN](https://en.wikipedia.org/wiki/ISBN)""")

            isbn_output = gr.TextArea(interactive=False, show_label=False, show_copy_button=False)


        gr.on(
            triggers=[isbn_submit.click, isbn_input.change],
            fn=verify_isbns,
            inputs=[isbn_input],
            outputs=[isbn_output]
        )


    with gr.Tab("Integer Series"):
        with gr.Row():
            with gr.Column():
                oeis_sequence_input = gr.Textbox(label="Sequence", placeholder="Enter comma separated sequence here...")
                oeis_identifier_input = gr.Textbox(label="Identifier", placeholder="Enter A000000 identifier here...")
                gr.Markdown("Based on [The Online Encyclopedia of Integer Sequences](https://oeis.org/)")
            oeis_output = gr.TextArea(label="Output")
        
        
        oeis_sequence_input.change(
            fn=lookup_oeis_seq,
            inputs=[oeis_sequence_input],
            outputs=[oeis_output]
        )
        oeis_identifier_input.change(
            fn=lookup_oeis_id,
            inputs=[oeis_identifier_input],
            outputs=[oeis_output]
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

