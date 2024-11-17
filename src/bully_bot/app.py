import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    # Load the pre-trained model and tokenizer
    model_name = (
        "microsoft/DialoGPT-medium"  # You can choose 'small' or 'large' as well
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Streamlit app configuration
    st.title("Hello, try sending me a message!")

    # Session state to keep the conversation history
    if "history" not in st.session_state:
        st.session_state["history"] = []

    # User input
    user_input = st.text_input("You:", "")

    if st.button("Send") and user_input:
        # Tokenize and generate response
        input_ids = tokenizer.encode(
            user_input + tokenizer.eos_token, return_tensors="pt"
        )

        # Concatenate with history if exists
        bot_input_ids = (
            torch.cat([st.session_state["history"], input_ids], dim=-1)
            if st.session_state["history"]
            else input_ids
        )

        response_ids = model.generate(
            bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id
        )
        response = tokenizer.decode(
            response_ids[:, bot_input_ids.shape[-1] :][0], skip_special_tokens=True
        )

        # Update session state
        st.session_state["history"] = response_ids

        # Display response
        st.text_area("Bot:", value=response, height=100, max_chars=None, key=None)


if __name__ == "__main__":
    main()
