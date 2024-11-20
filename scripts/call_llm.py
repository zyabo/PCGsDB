import json
import pandas as pd
import ollama
import re
import time
import pickle
import os
import pandas as pd
import re
import time
import pickle
import json
import os
import ast
from transformers import AutoTokenizer
import transformers
import torch
from openai import OpenAI

torch.cuda.empty_cache()
# device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cuda"

client_gpt = OpenAI(
    api_key="sk-proj-XrnkiXS7BrOUoBHNwgmtT3BlbkFJ7RaJA26AQuE9pTPmP5aP",
)


def get_response(model_type, model_name, client, pipeline, tokenizer, prompt_str,
                 system_content="", user_content="", template=""):
    total_tokens = 0
    if model_type == "local":
        response_str = get_response_local(prompt_str, pipeline, tokenizer, model_name, template)

    if model_type == "api":
        if model_name == "chain-of-thoughts.q5":
            response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:chain-of-thoughts.q5', messages=[
                {'role': 'user', 'content': prompt_str}
            ])
            response_str = response['message']['content']

        elif model_name == "thinking-fast-n-slow.q5":
            response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:thinking-fast-n-slow.q5', messages=[
                {'role': 'user', 'content': prompt_str}
            ])
            response_str = response['message']['content']

        elif model_name == "critical-thinking.q5":
            response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:critical-thinking.q5', messages=[
                {'role': 'user', 'content': prompt_str}
            ])
            response_str = response['message']['content']

        elif model_name == "iceberg-mental-model.q5":
            response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:iceberg-mental-model.q5', messages=[
                {'role': 'user', 'content': prompt_str}
            ])
            response_str = response['message']['content']

        elif model_name == "second-order-thinking.q5":
            response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:second-order-thinking.q5', messages=[
                {'role': 'user', 'content': prompt_str}
            ])
            response_str = response['message']['content']
        else:
            response_str = get_response_api(prompt_str, model_name)

    if model_type == "qwen":
        response_str, total_tokens = get_response_qwen(client, model_name, system_content, user_content)

    if model_type == "gpt":
        response_str = get_response_gpt(prompt_str, model_name)


    return response_str, total_tokens


def get_response_qwen(client, model_name, system_content, user_content):
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                'role': 'system',
                'content': 'You are a helpful medical assistant.'
            },
            {
                'role': 'system',
                'content': system_content
            },
            {
                'role': 'user',
                'content': user_content
            }
        ],
        # stream=True
    )
    # print(completion.choices[0].message.content)  # Output the text content of the entire response
    response_str = completion.choices[0].message.content
    total_tokens = completion.usage.total_tokens
    return response_str, total_tokens


def get_response_api(prompt_str, model_name):
    if model_name == "medllama2":
        response = ollama.chat(model='medllama2', messages=[
            {'role': 'user', 'content': prompt_str}
        ])

    if model_name == "chain-of-thoughts.q5":
        response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:chain-of-thoughts.q5', messages=[
            {'role': 'user', 'content': prompt_str}
        ])

    if model_name == "thinking-fast-n-slow.q5":
        response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:thinking-fast-n-slow.q5', messages=[
            {'role': 'user', 'content': prompt_str}
        ])

    if model_name == "critical-thinking.q5":
        response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:critical-thinking.q5', messages=[
            {'role': 'user', 'content': prompt_str}
        ])

    if model_name == "iceberg-mental-model.q5":
        response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:iceberg-mental-model.q5', messages=[
            {'role': 'user', 'content': prompt_str}
        ])

    if model_name == "second-order-thinking.q5":
        response = ollama.chat(model='mychen76/llama3.1-intuitive-thinker:second-order-thinking.q5', messages=[
            {'role': 'user', 'content': prompt_str}
        ])

    if model_name == "llama3":
        response = ollama.chat(model='llama3', messages=[
            {'role': 'user', 'content': prompt_str}
        ])
    response_str = response['message']['content']
    return response_str

def get_response_gpt(prompt_str, model_name = "gpt-3.5-turbo"):
    chat_completion = client_gpt.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt_str,
            }
        ],
        model=model_name,
    )
    response_str = chat_completion.choices[0].message.content
    return response_str


def get_response_local(prompt_str, pipeline, tokenizer, model_name, template=""):
    if model_name == "medllama2" or model_name == "llama2":
        sequences = pipeline(
            prompt_str,
            do_sample=False,
            temperature=0.0,
            top_k=10,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            max_length=8000,
        )
        for seq in sequences:
            print(f"Result: {seq['generated_text'][len(prompt_str):]}")
        return sequences[0]['generated_text'][len(prompt_str):]

    if model_name == "llama3":
        messages = [
            {"role": "system",
             "content": "You are an expert and experienced from the healthcare and biomedical domain with extensive medical knowledge and practical experience. Your name is OpenBioLLM, and you were developed by Saama AI Labs. who's willing to help answer the user's query with explanation. In your explanation, leverage your deep medical expertise such as relevant anatomical structures, physiological processes, diagnostic criteria, treatment guidelines, or other pertinent medical concepts. Use precise medical terminology while still aiming to make the explanation clear and accessible to a general audience."},
            {"role": "user", "content": prompt_str},
        ]
        prompt = pipeline.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        terminators = [
            pipeline.tokenizer.eos_token_id,
            pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]
        outputs = pipeline(
            prompt,
            max_new_tokens=8000,
            eos_token_id=terminators,
            do_sample=False,
            temperature=0.0,
        )
        return outputs[0]["generated_text"][len(prompt):]

    # model_name = "Llama-3.1-8B-Instruct"
    # model_name = "Qwen2.5-7B-Instruct"

    if model_name == "Llama-3.1-8B-Instruct":
        messages = [
            {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
            {"role": "user", "content": prompt_str},
        ]
        outputs = pipeline(
            messages,
            max_new_tokens=256,
        )
        # print(outputs[0]["generated_text"][-1])
        return outputs[0]["generated_text"][-1]

    if model_name == "Qwen2.5-7B-Instruct":
        messages = [{"role": "user", "content": prompt_str}]

        outputs = pipeline(messages, max_new_tokens=256, do_sample=False, temperature=0.0, top_k=50, top_p=0.95)
        # print(outputs[0]["generated_text"])
        return outputs[0]["generated_text"]

    if model_name == "numind/NuExtract-1.5":
        # messages = [{"role": "user", "content": prompt_str}]
        #
        # outputs = pipeline(messages, max_new_tokens=256, do_sample=False, temperature=0.0, top_k=50, top_p=0.95)
        # # print(outputs[0]["generated_text"])
        # return outputs[0]["generated_text"]

        template = json.dumps(json.loads(template), indent=4)
        prompts = [f"""<|input|>\n### Template:\n{template}\n### Text:\n{text}\n\n<|output|>""" for text in [prompt_str]]

        outputs = []
        batch_size = 1
        max_length = 10_000
        max_new_tokens = 4_000
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i + batch_size]

            # Using the pipeline directly for generation
            predictions = pipeline(batch_prompts, max_new_tokens=max_new_tokens, truncation=True, padding=True)

            # Flatten nested list of predictions and extract generated text
            for batch in predictions:
                if isinstance(batch, list):
                    for pred in batch:
                        if isinstance(pred, dict) and 'generated_text' in pred:
                            outputs.append(pred['generated_text'])
                elif isinstance(batch, dict) and 'generated_text' in batch:
                    outputs.append(batch['generated_text'])
                else:
                    raise ValueError("Unexpected output format from pipeline")

        # Extracting output text after "<|output|>"
        return [output.split("<|output|>")[1] if "<|output|>" in output else output for output in outputs]




def init_llm(model_type, model_name):
    pipeline = ""
    tokenizer = ""
    client = ""
    if model_type == "local":
        if model_name == "Llama-3.1-8B-Instruct":
            model = r"D:\Datas\LocalModels\Llama-3.1-8B-Instruct"
            tokenizer = AutoTokenizer.from_pretrained(model)
            pipeline = transformers.pipeline(
                "text-generation",
                model=model,
                model_kwargs={"torch_dtype": torch.bfloat16},
                device_map="auto",
            )

        if model_name == "numind/NuExtract-1.5":
            model_path = "D:/Datas/LocalModels/NuExtract1.5"  # New model path
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)  # Load tokenizer
            pipeline = transformers.pipeline(
                "text-generation",
                model=model_path,  # Use model path directly
                model_kwargs={"torch_dtype": torch.bfloat16},  # Set the desired torch dtype
                device_map="auto"  # Automatically map to available devices (like CUDA if available)
            )

        if model_name == "Qwen2.5-7B-Instruct":
            model = r"D:\Datas\LocalModels\Qwen2.5-7B-Instruct"
            tokenizer = AutoTokenizer.from_pretrained(model)
            pipeline = transformers.pipeline(
                "text-generation",
                model=model,
                torch_dtype=torch.float16,
                device_map="auto",
            )

        if model_name == "medllama2":
            model = r"E:\Datas\Models\llSourcell_medllama2_7b"
            tokenizer = AutoTokenizer.from_pretrained(model)
            pipeline = transformers.pipeline(
                "text-generation",
                model=model,
                torch_dtype=torch.float16,
                device_map="auto",
            )
        if model_name == "llama3":
            model_id = r"E:\Datas\Models\meta-llama_Meta-Llama-3-8B-Instruct"
            pipeline = transformers.pipeline(
                "text-generation",
                model=model_id,
                model_kwargs={"torch_dtype": torch.bfloat16},
                device=device,
            )
            tokenizer = ""

    if model_type == "qwen":
        client = OpenAI(
            api_key="sk-7c4f8fb0342f495da02e20c8632e34bb",  # API_KEY
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  #
        )




    return client, pipeline, tokenizer

def get_model_dict(model_name= "llama3"):
    # 本地 api
    if model_name == "llama3":
        model_dict = {"model name": "llama3",
                      "total_tokens_max": 1e100}

    if model_name == "medllama2":
        model_dict = {"model name": "medllama2",
                      "total_tokens_max": 1e100}

    if model_name == "llama3.1":
        model_dict = {"model name": "llama3.1:8b",
                      "total_tokens_max": 1e100}

    if model_name == "chain-of-thoughts.q5":
        model_dict = {"model name": "chain-of-thoughts.q5",
                      "total_tokens_max": 1e100}
    if model_name == "thinking-fast-n-slow.q5":
        model_dict = {"model name": "thinking-fast-n-slow.q5",
                      "total_tokens_max": 1e100}
    if model_name == "critical-thinking.q5":
        model_dict = {"model name": "critical-thinking.q5",
                      "total_tokens_max": 1e100}
    if model_name == "iceberg-mental-model.q5":
        model_dict = {"model name": "iceberg-mental-model.q5",
                      "total_tokens_max": 1e100}
    if model_name == "second-order-thinking.q5":
        model_dict = {"model name": "second-order-thinking.q5",
                      "total_tokens_max": 1e100}


    # 提取基因用
    if model_name == "qwen-plus":
        model_dict = {"model name": "qwen-plus",
                      "total_tokens_max": 232918}

    if model_name == "qwen-max":
        model_dict = {"model name": "qwen-max",
                      "total_tokens_max": 418316}
    if model_name == "qwen-max-0428":
        model_dict = {"model name": "qwen-max-0428",
                      "total_tokens_max": 1000000}

    if model_name == "qwen-max-longcontext":
        model_dict = {"model name": "qwen-max-longcontext",
                      "total_tokens_max": 1000000}

    if model_name == "qwen-max-0403":
        model_dict = {"model name": "qwen-max-0403",
                      "total_tokens_max": 1000000}
    if model_name == "qwen-max-0107":
        model_dict = {"model name": "qwen-max-0107",
                      "total_tokens_max": 1000000}
    if model_name == "qwen-max-1201":
        model_dict = {"model name": "qwen-max-1201",
                      "total_tokens_max": 1000000}
    if model_name == "qwen-long":
        model_dict = {"model name": "qwen-long",
                      "total_tokens_max": 3994357}
    if model_name == "qwen-turbo":
        model_dict = {"model name": "qwen-turbo",
                      "total_tokens_max": 4000000}

    # 开源
    if model_name == "qwen1.5-110b-chat":
        model_dict = {"model name": "qwen1.5-110b-chat",
                      "total_tokens_max": 3989885}
    if model_name == "qwen1.5-72b-chat":
        model_dict = {"model name": "qwen1.5-72b-chat",
                      "total_tokens_max": 4000000}
    if model_name == "qwen-72b-chat":
        model_dict = {"model name": "qwen-72b-chat",
                      "total_tokens_max": 1000000}
    if model_name == "llama3-70b-instruct":
        model_dict = {"model name": "llama3-70b-instruct",
                      "total_tokens_max": 1000000}
    if model_name == "llama3-8b-instruct":
        model_dict = {"model name": "llama3-8b-instruct",
                      "total_tokens_max": 1000000}
    return model_dict