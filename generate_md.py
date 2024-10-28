import os
import yaml
from groq import Groq
from datetime import datetime

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TOPIC = os.environ.get("TOPIC")
MODEL = os.environ.get("MODEL", "llama3-8b-8192")
DESTINATION_FILE = os.environ.get("DESTINATION_FILE")

client = Groq(
    api_key=GROQ_API_KEY,
)

prompt = open('/Users/kaushal/workplace/daily-learning-md/learning_prompt.txt', 'r').read().format(topic=TOPIC)

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

```
```

"""

def append_to_markdown_file(formatted_content, filepath):
    with open(filepath, 'a') as f:
        f.write(formatted_content)

# Get today's date
today = datetime.now().strftime('%Y-%m-%d')

# Format the markdown
formatted_md = format_markdown(response, today)

# Append to existing markdown file
markdown_filepath = DESTINATION_FILE  # Update this path
append_to_markdown_file(formatted_md, markdown_filepath)
