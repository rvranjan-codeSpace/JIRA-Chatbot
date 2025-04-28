from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
import os
from constants.config import GPT_CONFIG,GROQ_CONFIG
 
 

class Model:
    def __init__(self, ai_type, model_name, temperature=0.5):
        self.ai_type = ai_type
        self.model_name = model_name
        self._temperature = temperature
        load_dotenv()  # Ensure environment variables are loaded

    def getOpenAIModel(self) -> ChatOpenAI:
        #os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        gpt_api_key = GPT_CONFIG.get("gpt_api_key")
        os.environ["OPENAI_API_KEY"] = gpt_api_key
        return ChatOpenAI(model=self.model_name, temperature=self._temperature)

    def getGroqModel(self) -> ChatGroq:
        #os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
        groq_api_key=GROQ_CONFIG.get("groq_api_key")
        os.environ["GROQ_API_KEY"] = groq_api_key
        llm = ChatGroq(model=self.model_name, api_key=os.getenv("GROQ_API_KEY"))
        return llm

    def getModel(self)->BaseChatModel:
        if self.ai_type.lower() == "groq":
            return self.getGroqModel()
        elif self.ai_type.lower() == "openai":
            return self.getOpenAIModel()
        else:
            raise ValueError(f"Unsupported AI type: {self.ai_type}")


if __name__ == "__main__":
    # Creating a model with a custom temperature
    # model_OpenAI = Model("OpenAI", "gpt-3.5-turbo", 0.5).getModel()
    # print(model_OpenAI.invoke("What is machine learning?"))

    # Creating a model with the default temperature
    model_Groq = Model("Groq", "Gemma2-9b-It").getModel()
    print(model_Groq.invoke("What is machine learning?"))
