import openai
import os  # Added missing os module
def interpret_lab_results(pdf_text):
    """
    Interprets laboratory test results from a given PDF text.
    :param pdf_text: Text extracted from the PDF
    :return: Clinical evaluation
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")  # Get OpenAI API key
    prompt = f"""
    The following are laboratory test results for a patient. Analyze these results and provide a clinical evaluation:
    {pdf_text}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a medical expert (psychiatrist) analyzing lab test results."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Lab analysis encountered an error: {str(e)}"