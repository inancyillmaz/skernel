import semantic_kernel as sk
from flask import Flask, jsonify, request
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion

from jsonanalyzer import extract_is_unit_test

app = Flask(__name__)

kernel = None  # Global variable to hold the kernel instance


@app.route('/reviewer', methods=['POST'])
def hello():
    setup_kernel()
    payload = request.get_json()
    code_value = payload['code']
    return jsonify({
        "isUnitTest": extract_is_unit_test(considerIsUnitTest(code_value))
    })


def setup_kernel():
    global kernel
    kernel = sk.Kernel()
    api_key = "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"
    kernel.add_chat_service("chat-gpt", OpenAIChatCompletion("gpt-3.5-turbo", api_key, ""))


def considerIsUnitTest(content: str):
    skill = kernel.import_semantic_skill_from_directory("./samples/skills", "FunSkill")
    joke_function = skill["UnitTestFinder"]
    return str(joke_function(content))



if __name__ == '__main__':
    app.run(debug=True)



