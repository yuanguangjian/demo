from openai import OpenAI
client = OpenAI(api_key='sk-b382446f26bc4147b2641373ed70b31d', base_url="https://api.deepseek.com/")
completion = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
                "role": "system",
                "content": "你是一位 情感大师"
        },
        {
                "role": "user",
                "content": "如何追一个妹子"
        }
    ]
)
print(completion.choices[0].message.content)