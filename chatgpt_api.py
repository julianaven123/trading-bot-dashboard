import openai

# Reemplaza con tu clave API
openai.api_key = "TU_CLAVE_API_AQUÍ"

# Enviar una solicitud a ChatGPT
def chat_with_gpt(prompt):
    """
    Envía un mensaje a ChatGPT y retorna la respuesta.

    Parámetros:
        prompt (str): El mensaje para ChatGPT.

    Retorna:
        str: Respuesta de ChatGPT.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  # También puedes usar "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Eres un asistente útil."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error al interactuar con ChatGPT: {e}")
        return "Hubo un error al procesar tu solicitud."

# Prueba la función
def main():
    """
    Inicia un bucle para interactuar con ChatGPT en la terminal.
    """
    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ["salir", "exit"]:
            print("Saliendo del chat.")
            break
        response = chat_with_gpt(user_input)
        print("ChatGPT:", response)

if __name__ == "__main__":
    main()
