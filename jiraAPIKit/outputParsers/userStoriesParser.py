
from langchain.output_parsers import StructuredOutputParser,ResponseSchema
from typing import List

class UserStoryParser:


    @staticmethod
    def create_output_parser()->StructuredOutputParser:
         # Initialize the response schemas
        ac = ResponseSchema(name="AC", description="This is acceptance criteria for a particular user story")
        tc_sumary = ResponseSchema(name="testcase_summary", description="This is the test case summary")
        tc_description = ResponseSchema(name="testcase_steps", description="This is test case steps")
        
        # Store response schemas in a list
        response_schema = [ac, tc_sumary,tc_description]

        # Create and return the StructuredOutputParser using the response schemas
        output_parser = StructuredOutputParser.from_response_schemas(response_schemas=response_schema)
        return output_parser
    
    @staticmethod
    def get_format_instructions() -> str:   
        # Return format instructions from the output parser
        output_parser = UserStoryParser.create_output_parser()
        format_instructions = output_parser.get_format_instructions()
        return format_instructions

if __name__ == "__main__":
    print(UserStoryParser.get_format_instructions())


