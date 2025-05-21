def fix_code(code, client):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Aşağıdaki Python kodundaki hatayı düzelt:"},
            {"role": "user", "content": code}
        ],
        max_tokens=500,
        timeout=20
    )
    return response.choices[0].message.content
