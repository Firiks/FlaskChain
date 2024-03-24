import json

from server.utils.helpers import get_location

json_path = get_location('../prompts/data/prompt_templates.json')

templates = json.load(open(json_path, 'r'))

def assemble_template(template_id = 'base', rag = True, rag_derive = True, llama_intruction = False) -> str:
    template = _get_template_by_id(template_id)

    if rag:
        template = _add_rag(template)
        template = _derive_outside_context(template, rag_derive)
        template = _add_formatting(template)
        template = _add_context(template)
        template = _add_history(template)
        template = _add_question(template)
        template = _add_answer(template)
    else :
        template = _add_formatting(template)
        template = _add_history(template)
        template = _add_question(template)
        template = _add_answer(template)

    if llama_intruction:
        template = _add_llama_instruction(template)

    return template
    
def _get_template_by_id(template_id):
    global templates

    prompt_template =[t.get('value') for t in templates if t.get('name') == template_id][0]

    return prompt_template

def _add_rag(prompt):
    rag_prompt = _get_template_by_id('base_rag')
    prompt = prompt + " " + rag_prompt

    return prompt

def _derive_outside_context(prompt, can_derive = False):
    derive = 'can'

    if not can_derive:
        derive = 'dont'
    
    prompt = prompt.replace('CONTENT_DERIVE', derive)

    return prompt

def _add_formatting(prompt):
    format_prompt = _get_template_by_id('formatting')

    prompt = prompt + " " + format_prompt

    return prompt

def _add_context(prompt):
    context_prompt = _get_template_by_id('context')

    prompt = prompt + " " + context_prompt

    return prompt

def _add_history(prompt):
    history_prompt = _get_template_by_id('history')

    prompt = prompt + " " + history_prompt

    return prompt

def _add_question(prompt):
    question_prompt = _get_template_by_id('question')

    prompt = prompt + " " + question_prompt

    return prompt

def _add_answer(prompt):
    answer_prompt = _get_template_by_id('answer')

    prompt = prompt + " " + answer_prompt

    return prompt

def _add_llama_instruction(prompt):
    llama_prompt = _get_template_by_id('llama_instruction')

    llama_prompt = llama_prompt.replace('TEMPLATE', prompt)

    return llama_prompt

if __name__ == "__main__":
    template = assemble_template()

    print(template)