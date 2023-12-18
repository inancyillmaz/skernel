import json
import semantic_kernel as sk

from flask import Flask, jsonify, request
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion

app = Flask(__name__)

kernel = None
useOpenAI = True
useChatGPT4 = True


@app.route('/testReviewer', methods=['POST'])
def test_asserter():
    payload = request.get_json()
    code_value = payload['code']
    unitTestSuggestionAssertion = considerGenerateAnAssertion(code_value)
    return jsonify({
        "codeSuggestion": unitTestSuggestionAssertion
    })


@app.route('/gitlabReviewer', methods=['POST'])
def gitlab_reviewer():
    payload = request.get_json()
    startingLineNumber = payload['startingLineNumber']
    code_value = payload['code']
    skill = kernel.import_semantic_skill_from_directory("./samples/skills", "ReviewSkills")
    asserter_skill = skill["GitlabSuggestioner"]
    assertion_result = str(asserter_skill(code_value))
    suggestedLine = json.loads(assertion_result)['lines_will_changed']
    emptyLineCount = count_newlines_until_substring(code_value, suggestedLine)
    lastCount = emptyLineCount + startingLineNumber if emptyLineCount != -1 else 0
    return jsonify({
        "total_lines_up_to_suggestion": lastCount,
        "is_code_suggestion_success": json.loads(assertion_result)['is_code_suggestion_success'],
        "explanation_of_new_code": json.loads(assertion_result)['explanation_of_new_code'],
        "new_code_suggestion": json.loads(assertion_result)['new_code_suggestion']

    })


def suggustMeANewSuggestion(code_value):
    skill = kernel.import_semantic_skill_from_directory("./samples/skills", "ReviewSkills")
    asserter_skill = skill["Asserter"]
    assertion_result = str(asserter_skill(code_value))
    return assertion_result


def generateAnAssertion(code_value):
    skill = kernel.import_semantic_skill_from_directory("./samples/skills", "ReviewSkills")
    assertion_validator_detector = skill["AssertionDetector"]
    isAssertionNeededResult = str(assertion_validator_detector(code_value))
    isAssertionNeeded = json.loads(isAssertionNeededResult)["needAssertion"]
    if isAssertionNeeded:
        return suggustMeANewSuggestion(code_value)
    else:
        return ""


def considerGenerateAnAssertion(code_value):
    isUnitTestResult = considerIsUnitTest(code_value)
    isUnitTest = json.loads(isUnitTestResult)["isUnitTest"]
    if isUnitTest:
        return generateAnAssertion(code_value)
    else:
        return ""


def considerIsUnitTest(content: str):
    skill = kernel.import_semantic_skill_from_directory("./samples/skills", "ReviewSkills")
    joke_function = skill["UnitTestFinder"]
    return str(joke_function(content))


def count_newlines_until_substring(text, stop_string):
    position = text.find(stop_string)

    if position != -1:
        sliced_text = text[:position]
        return sliced_text.count("\n")
    else:
        return -1


def addGPTModels():
    if useChatGPT4:
        kernel.add_chat_service("chat-gpt", OpenAIChatCompletion("gpt-4",
                                                                 "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",
                                                                 ""))
    else:
        kernel.add_chat_service("chat-gpt", OpenAIChatCompletion("gpt-3.5-turbo",
                                                                 "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",
                                                                 ""))


def addChatService():
    if useOpenAI:
        addGPTModels()
    else:
        kernel.add_chat_service("chat_completion", AzureChatCompletion("Deployment", "api_key", "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"))


def setup_kernel():
    global kernel
    kernel = sk.Kernel()
    addChatService()


if __name__ == '__main__':
    setup_kernel()
    app.run(debug=True)
