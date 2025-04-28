
from langchain.output_parsers import StructuredOutputParser,ResponseSchema
from typing import List


class JQLQueryParser:


    @staticmethod
    def create_output_parser()->StructuredOutputParser:
         # Initialize the response schemas
        jql = ResponseSchema(name="JQL", description="This is the executable JQL that can execute in JIRA")
        reasoning = ResponseSchema(name="Reason", description="This is the reason the JQL has been created")
        
        # Store response schemas in a list
        response_schema = [jql, reasoning,reasoning]

        # Create and return the StructuredOutputParser using the response schemas
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas=response_schema)
        return output_parser
    
    @staticmethod
    def get_format_instructions() -> str:   
        # Return format instructions from the output parser
        output_parser = JQLQueryParser.create_output_parser()
        format_instructions = output_parser.get_format_instructions()
        return format_instructions

if __name__ == "__main__":
    print(JQLQueryParser.get_format_instructions())


