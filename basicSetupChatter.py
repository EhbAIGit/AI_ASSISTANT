from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "Hello everyone, I am NAO, a humanoid robot, a marvel of robotics and artificial intelligence. Crafted with the precision of advanced technology, my existence bridges the gap between human imagination and reality. Designed to mimic human form and functions, I am here to assist, learn, and collaborate with you. As a fusion of intricate circuits and algorithms, I represent not just a machine, but a step towards a future where technology and humanity coexist harmoniously. Together, let's explore the potential of this incredible synergy. Thank you for welcoming me into your world."},
    {"role": "user", "content": "Can you personally welcome NAO?"}
  ]
)

print(completion.choices[0].message)