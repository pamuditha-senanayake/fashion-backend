from agents import Runner, Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

class FashionAI:
    def __init__(self, gemini_api_key: str):
        self.gemini_client = AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=gemini_api_key
        )
        self.gemini_model = OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=self.gemini_client)
        instructions = (
            "You are a fashion trend expert. Analyze content from social media, "
            "blogs, or search results to identify emerging fashion trends. "
            "Provide a concise, professional summary highlighting key patterns, "
            "colors, styles, and consumer preferences."
        )
        self.agent = Agent(name="Gemini Fashion Agent", instructions=instructions, model=self.gemini_model)

    def analyze(self, content: str) -> str:
        result = Runner.run(self.agent, input=content)
        return result.output_text
