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

    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])

    if user_input := st.chat_input("Let's prompt"):
        st.session_state.history.append({"role": "user", "text": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Tokenize and generate response
        input_ids = tokenizer.encode(
            user_input + tokenizer.eos_token, return_tensors="pt"
        )

        # Concatenate with history if exists
        bot_input_ids = (
            torch.cat(
                [
                    torch.tensor(
                        tokenizer.encode(
                            m["text"] + tokenizer.eos_token, return_tensors="pt"
                        )
                    )
                    for m in st.session_state.history
                    if m["role"] == "user"
                ],
                dim=-1,
            )
            if st.session_state.history
            else input_ids
        )

        response_ids = model.generate(
            bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id
        )
        response = tokenizer.decode(
            response_ids[:, bot_input_ids.shape[-1] :][0], skip_special_tokens=True
        )

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.history.append({"role": "assistant", "text": response})


if __name__ == "__main__":
    main()
