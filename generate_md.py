import os
import yaml
from groq import Groq
from datetime import datetime
from zoneinfo import ZoneInfo  # Add this import

def get_topic_from_frontmatter(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        # Parse frontmatter between --- markers
        if content.startswith('---'):
            _, frontmatter, _ = content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)
            return metadata.get('Topic')
    return None

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DESTINATION_FILE = os.environ.get("DESTINATION_FILE")
MODEL = os.environ.get("MODEL", "llama3-8b-8192")

# Get topic from frontmatter instead of environment variable
TOPIC = get_topic_from_frontmatter(DESTINATION_FILE) or os.environ.get("TOPIC")

client = Groq(
    api_key=GROQ_API_KEY,
)

prompt = open('learning_prompt.txt', 'r').read().format(topic=TOPIC)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model=MODEL,
)

response = chat_completion.choices[0].message.content

def format_markdown(response, date):
    data = yaml.load(response, Loader=yaml.FullLoader)
    question, hint = data['question'], data['hint']
    return f"""### {date}
> [!question]- {question}
> {hint}

---
#### Answer:
---

"""

def append_to_markdown_file(formatted_content, filepath):
    with open(filepath, 'a') as f:
        f.write(formatted_content)

today = datetime.now(ZoneInfo('America/Los_Angeles')).strftime('%Y-%m-%d')

formatted_md = format_markdown(response, today)

markdown_filepath = DESTINATION_FILE
append_to_markdown_file(formatted_md, markdown_filepath)
