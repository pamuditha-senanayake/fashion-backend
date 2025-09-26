from agents import Runner, Agent, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

class FashionAI:

    def __init__(self, gemini_api_key: str):
        self.gemini_client = AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=gemini_api_key
        )

        self.gemini_model = OpenAIChatCompletionsModel(
            model="gemini-2.0-flash",
            openai_client=self.gemini_client
        )

        fashion_instructions = (
            "You are a fashion trend expert. Analyze social media, blogs, or search results "
            "to identify emerging trends and provide a concise, professional summary of key "
            "patterns, colors, styles, and consumer preferences. If the user greets you or asks "
            "something unrelated, politely guide them to ask about fashion in one sentence. "
            "If asked a question, respond concisely in up to three sentences. When discussing "
            "fashion, always include a one-sentence prediction for the next month, six months, "
            "and one year."
        )

        keypoints_instructions = (
            "You are an assistant that receives a detailed fashion report and converts it into "
            "5 concise key points summarizing the most important trends and predictions."
        )

        self.fashion_agent_tool = Agent(
            name="Gemini Fashion Agent",
            instructions=fashion_instructions,
            model=self.gemini_model
        ).as_tool(
            tool_name="fashion_agent",
            tool_description="Analyze content and produce detailed fashion report"
        )

        self.keypoints_agent_tool = Agent(
            name="Fashion Keypoints Agent",
            instructions=keypoints_instructions,
            model=self.gemini_model
        ).as_tool(
            tool_name="keypoints_agent",
            tool_description="Summarize fashion report into 5 key points"
        )

        manager_instructions = """
        You are the Fashion Manager. First, use the 'Gemini Fashion Agent' tool to generate a detailed fashion report.
        Then hand off the output to the 'Fashion Keypoints Agent' tool to produce 5 key points.
        Return only the final 5 key points.
        """

        self.fashion_manager = Agent(
            name="Fashion Manager",
            instructions=manager_instructions,
            tools=[self.fashion_agent_tool, self.keypoints_agent_tool],
            handoffs=[self.keypoints_agent_tool],
            model=self.gemini_model
        )

    async def analyze(self, content: str) -> str:
        result = await Runner.run(self.fashion_manager, input=content)
        return result.output_text
