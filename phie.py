import gradio as gr
from ciphers import all_ciphers
from dictionary import AnagramLookupTable, dictionary_all, dictionary_popular, find_words_by_regex
import re

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


# Dictionary

anagram_lookup_table_all = AnagramLookupTable(dictionary_all)
anagram_lookup_table_common = AnagramLookupTable(dictionary_popular)

def lookup_anagram(anagram: str, limit_to_common: bool) -> str:
    lookup_table = anagram_lookup_table_all if not limit_to_common else anagram_lookup_table_common
    solutions = lookup_table.lookup(anagram.replace(" ", ""))
    return f"{len(solutions)} results found:\n\n{'\n'.join(solutions)}" if solutions is not None else f"No results found for '{anagram}'"

def find_word(search_string: str, limit_to_common: bool) -> str:
    results = find_words_by_regex(re.compile(search_string), dictionary_all if not limit_to_common else dictionary_popular)
    return f"{len(results)} words found:\n\n{'\n'.join(results)}" if len(results) != 0 else f"No results found for '{search_string}'"



css = """
.small-button { max-width: 2.8em; min-width: 2.8em !important; align-self: center; }
.centered-checkbox > label {  }
"""

with gr.Blocks(css=css, theme=gr.themes.Default()) as app:
    gr.Markdown("# Puzzle Hunt Intelligence Laboratory")
    with gr.Tab("Ciphers"):
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    left_cipher_selector = gr.Radio(cipher_names, value=cipher_names[1], type="index", interactive=True, show_label=False)
                    left_run_button = gr.Button("➡️", elem_classes=["small-button"], variant="secondary", scale=0)
                left_text_area = gr.TextArea(interactive=True, show_label=False, show_copy_button=True)
                left_key_area = gr.Textbox(label="Key", interactive=True)
            with gr.Column():
                with gr.Row():
                    right_run_button = gr.Button("⬅️", elem_classes=["small-button"], scale=0)
                    right_cipher_selector = gr.Radio(cipher_names, value=cipher_names[0], type="index", interactive=True, show_label=False)
                
                right_text_area = gr.TextArea(interactive=True, show_label=False, show_copy_button=True)
                right_key_area = gr.Textbox(label="Key", interactive=True)
        
        left_cipher_selector.select(
            fn=lambda cindex, key: "all" if cindex == cipher_names.index("Caesar") and not key.isnumeric() else key,
            inputs=[left_cipher_selector, left_key_area],
            outputs=[left_key_area]
        )
        right_cipher_selector.select(
            fn=lambda cindex, key: "all" if cindex == cipher_names.index("Caesar") and not key.isnumeric() else key,
            inputs=[right_cipher_selector, right_key_area],
            outputs=[right_key_area]
        )
        
        # run the ciphers
        gr.on(
            triggers=[left_run_button.click, left_text_area.input, left_key_area.input],
            fn=run_cipher,
            inputs=[left_cipher_selector, left_key_area, right_cipher_selector, right_key_area, left_text_area],
            outputs=[right_text_area]
        )
        gr.on(
            triggers=[right_run_button.click, right_text_area.input, right_key_area.input],
            fn=run_cipher,
            inputs=[right_cipher_selector, right_key_area, left_cipher_selector, left_key_area, right_text_area],
            outputs=[left_text_area]
        )
    
    
    with gr.Tab("Bruteforce"):
        gr.Markdown("brute force cesar, other keys, ...")
        gr.Button("Google it", variant="primary")

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
        gr.Markdown("not yet implemented")
    
    with gr.Tab("Have you googled it?"):
        gr.Markdown("""No? Then maybe it's time to do so.
                    - ISBN
                    - IP address
                    - phone numbers
                    - Coordinates
                    
                    **Take a look at the cheatsheet Brainstorming section.**
                    """)


demo = app

app.launch()

