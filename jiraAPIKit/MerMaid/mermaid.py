from dash_extensions import Mermaid
from langchain.prompts import ChatPromptTemplate
from llmmodel.modelFactory import Model
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'MACROS')))
 
model = Model(ai_type="openai", model_name="gpt-4o-mini", temperature=0.5)
llm = model.getModel()
 


# Mermaid diagram generation function
def generate_mermaid_diagram(steps):
    ts = None

    ts_link = """
    Your job is to write the code to generate a colorful mermaid diagram
    describing the below
    {steps} information only, don't use any other information.
    Only generate the code as output, nothing extra.
    Each line in the code must be terminated by a semicolon.
    Include specific relationship labels such as 'blocks', 'duplicates','tests','relates to' or 'clones' where applicable.
    Code:
    """

    ts_status = """
    Your job is to write the code to generate a colorful mermaid diagram
    describing the below
    {steps} information only, don't use any other information.
    Only generate the code as output, nothing extra.
    Each line in the code must be terminated by a semicolon.
    Include specific relationship labels such as 'Status', 'Due Dates' where applicable.
    Code:
    """
    if "Status" in steps or "Due Date" in steps:
        ts = ts_status
    else:
        ts = ts_link

    pt = ChatPromptTemplate.from_template(ts)
    qa_chain = pt | llm
    response = qa_chain.invoke({"steps": steps})
    data = response.content
    data = data.replace("`", "").replace("mermaid", "")
    #print(data)
    return data
