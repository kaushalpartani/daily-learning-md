import os
import yaml
import re
from groq import Groq
from datetime import datetime
from zoneinfo import ZoneInfo
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
logger = logging.getLogger(__name__)

# Constants
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DESTINATION_FILE = os.environ.get("DESTINATION_FILE")
MODEL = os.environ.get("MODEL", "llama3-8b-8192")
DISABLED_KEYS = ['disabled', 'Disabled', 'DISABLED']

def is_disabled(filepath):
    """Check if the file is explicitly disabled by checking for the 'disabled' property in the frontmatter."""
    with open(filepath, 'r') as f:
        content = f.read()
        if content.startswith('---'):
            _, frontmatter, _ = content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)
            logger.info(f"Metadata: {metadata}")
            return not any([key in metadata for key in DISABLED_KEYS])
    return False

def get_topic_from_frontmatter(filepath):
    """Extract Topic field from markdown frontmatter."""
    with open(filepath, 'r') as f:
        content = f.read()
        if content.startswith('---'):
            _, frontmatter, _ = content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)
            return metadata.get('Topic')
    return None

def get_previous_questions(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        pattern = r'> \[!question\]- (.*)\n'
        matches = re.finditer(pattern, content)
        questions = [match.group(1).strip() for match in matches]
        if not questions:
            return "There have been no previous questions"
        return "\n".join(questions[-5:]) if len(questions) > 5 else "\n".join(questions)

def format_markdown(response, date):
    """Format the AI response into markdown with question and hint."""
    data = yaml.load(response, Loader=yaml.FullLoader)
    question, hint = data['question'], data['hint']
    return f"""
### {date}
> [!question]- {question}
> {hint}

---
#### Answer:
---

"""

def append_to_markdown_file(formatted_content, filepath):
    """Append formatted content to the markdown file."""
    with open(filepath, 'a') as f:
        f.write(formatted_content)

def generate_question():
    """Main function to generate and append a new question."""
    if is_disabled(DESTINATION_FILE):
        logger.info(f"{DESTINATION_FILE} has disabled flag set. Skipping generation.")
        return
    # Get topic from frontmatter or environment
    topic = get_topic_from_frontmatter(DESTINATION_FILE) or os.environ.get("TOPIC")
    
    # Initialize Groq client
    client = Groq(api_key=GROQ_API_KEY)
    
    # Prepare prompt
    prompt = open('learning_prompt.txt', 'r').read().format(
        topic=topic, 
        previous_questions=get_previous_questions(DESTINATION_FILE)
    )
    
    # Get AI response
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
    )
    response = chat_completion.choices[0].message.content
    logger.info(f"Generated response: {response}")

    # Format and append response
    today = datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y-%m-%d')
    formatted_md = format_markdown(response, today)
    append_to_markdown_file(formatted_md, DESTINATION_FILE)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((Exception)),
    reraise=True
)
def generate_question_with_retry():
    """Generate question with retry logic, since we might not get the exact formatting we want on firsty try."""
    generate_question()

if __name__ == "__main__":
    generate_question_with_retry()
