import json

from server.utils.helpers import get_location

json_path = get_location('../prompts/data/prompt_templates.json')

templates = json.load(open(json_path, 'r'))

def assemble_template(template_id, rag = True, rag_derive = True, llama_intruction = False) -> str:
    template = _get_template_by_id(template_id, True)

    if rag:
        template = _add_rag(template)
        template = _derive_outside_context(template, rag_derive)
        template = _add_prompt_partial(template, 'formatting')
        template = _add_prompt_partial(template, 'context')
        template = _add_prompt_partial(template, 'history')
        template = _add_prompt_partial(template, 'question')
        template = _add_prompt_partial(template, 'answer')
    else :
        template = _add_prompt_partial(template, 'formatting')
        template = _add_prompt_partial(template, 'history')
        template = _add_prompt_partial(template, 'question')
        template = _add_prompt_partial(template, 'answer')

    if llama_intruction:
        template = _add_llama_instruction(template)

    return template
    
def _get_template_by_id(template_id, system = False):
    global templates

    try:
        prompt_template =[t for t in templates if t.get('name') == template_id][0]
    except:
        raise Exception('Invalid template id')

    if system and prompt_template.get('type') != 'system':
        raise Exception('Invalid template type')

    prompt_template = prompt_template.get('value')

    return prompt_template

def _add_prompt_partial(prompt, template_id):
    prompt_template = _get_template_by_id(template_id)

    prompt = prompt + " " + prompt_template

    return prompt

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

def _add_llama_instruction(prompt):
    llama_prompt = _get_template_by_id('llama_instruction')

    llama_prompt = llama_prompt.replace('TEMPLATE', prompt)

    return llama_prompt