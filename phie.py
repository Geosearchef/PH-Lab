import gradio as gr
from ciphers import all_ciphers

#redirect_to_light_js = "window.addEventListener('load', function () {gradioURL = window.location.href; if (!gradioURL.endsWith('?__theme=light')) {window.location.replace(gradioURL + '?__theme=dark');}});"

def run_cipher(input_cipher_index: int, input_key: str, output_cipher_index: int, output_key: str, input_text: str) -> str:
    if len(input_text) > 3000:
        return "Input too long"
    if len(input_text) > 300 and input_key == "all":
        return "Input too long"

    input_cipher = all_ciphers[input_cipher_index]
    output_cipher = all_ciphers[output_cipher_index]

    data = input_cipher.decode(input_text, input_key)
    output_text = output_cipher.encode(data, output_key)

    return output_text


#available_ciphers = ["Text", "Numbers", "Cesar", "Tap", "Morse"]
cipher_names = [c.name for c in all_ciphers]

css = ".small-button { max-width: 2.8em; min-width: 2.8em !important; align-self: center; border-radius: 0.5em;}"

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
        gr.Markdown("anagram solver")

    with gr.Tab("Dictionary"):
        gr.Markdown("regex dictionary search")

    with gr.Tab("Base Converter"):
        gr.Markdown("not yet implemented")


demo = app

app.launch()

