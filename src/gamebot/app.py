import random
import math
from itertools import permutations
import streamlit as st

class BullsAndCows:
    """
    A class to implement the Bulls and Cows game.
    Includes functionality for entropy and next guess suggestions.
    """

    def __init__(self):
        self.digits = list(range(10))
        self.secret = random.sample(self.digits, 4)  # Secret number (4 unique digits)
        self.attempts = 0
        self.possible_combinations = list(permutations(range(10), 4))  # All possible guesses
        self.first_attempt = True
        
    def calculate_entropy(self):
        n = len(self.possible_combinations)
        if n == 0:
            return 0  # No combinations left (edge case)
        probabilities = [1 / n] * n  # Equal probability for all possibilities
        entropy = sum(
            p * math.log2(1 / p) for p in probabilities
        )  # entropy calculation
        return entropy

    def entropy_reduction(self, prev_entropy, current_entropy):
        return prev_entropy - current_entropy

    def get_feedback(self, guess, code=None):
        if code is None:
            code = self.secret
        bulls = sum(g == s for g, s in zip(guess, code))
        cows = sum(g == s for g in guess for s in code) - bulls
        return bulls, cows

    def update_possibilities(self, guess, bulls, cows):
        new_possibilities = []
        for combo in self.possible_combinations:
            test_bulls, test_cows = self.get_feedback(guess, combo)
            if (test_bulls, test_cows) == (bulls, cows):
                new_possibilities.append(combo)
        self.possible_combinations = new_possibilities

    def suggest_next_guesses(self):
        """
        Suggest up to 10 guesses from the remaining possibilities.
        Returns:
            list: A list of up to 10 suggested guesses or an empty list.
        """
        sample_size = min(10, len(self.possible_combinations))  # Ensure up to 10 guesses
        return random.sample(self.possible_combinations, sample_size) if self.possible_combinations else []  


def main():
    # Streamlit App
    st.set_page_config(
        page_icon="https://cdn-icons-png.flaticon.com/512/6100/6100585.png",
        page_title="Ramya's game bot"
    )
    st.title("Bulls and Cows")
    st.text(
        "In this game, you need to guess a 4-digit number with all unique digits. "
        "I'll give you hints in the form of Bulls and Cows. "
        "A Bull means a correct digit in the correct place, and a Cow means a correct digit in the wrong place. "
        "Let's get started!"
    )

    # Ensure the game state persists across reruns
    if "game" not in st.session_state:
        st.session_state.game = BullsAndCows()
    if "messages" not in st.session_state:
        st.session_state.messages = []  # Store chat messages
    if "entropy_history" not in st.session_state:
        st.session_state.entropy_history = [st.session_state.game.calculate_entropy()]  # Track entropy values
    if "entropy_reduction_history" not in st.session_state:
        st.session_state.entropy_reduction_history = [0]
    if "game_over" not in st.session_state:
        st.session_state.game_over = False

    game = st.session_state.game

    # Chat input for user's guesses
    if not st.session_state.game_over:
        user_input = st.chat_input("Enter your 4-digit guess:")

        if user_input:
            # Append user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Validate user input
            if (
                len(user_input) != 4
                or not user_input.isdigit()
                or len(set(user_input)) != 4
            ):
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": "Invalid guess! Please enter 4 different digits.",
                    }
                )
            else:
                # Valid input: Process guess
                guess = [int(x) for x in user_input]
                prev_entropy = st.session_state.entropy_history[-1] 
                game.attempts += 1
                bulls, cows = game.get_feedback(guess)
                game.update_possibilities(guess, bulls, cows)

                # Calculate entropy and update history
                entropy = game.calculate_entropy()
                entropy_reduction = game.entropy_reduction(prev_entropy, entropy)

                # Append entropy and mutual information to session state
                st.session_state.entropy_history.append(entropy)
                st.session_state.entropy_reduction_history.append(entropy_reduction)
                
                # Check win condition
                if bulls == 4:
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": f"🎉 Congratulations! You guessed the secret number in {game.attempts} attempts!",
                        }
                    )
                    st.session_state.game_over = True
                else:
                    # Display feedback and suggestions with entropy and mutual information in a table
                    suggestions = game.suggest_next_guesses()
                    feedback = f"""
                    Bulls: {bulls}, Cows: {cows} <br><br>
                    **Game Metrics:**<br>
                    <table>
                        <tr><th>Metric</th><th>Value</th></tr>
                        <tr><td>Entropy</td><td>{entropy:.2f} bits</td></tr>
                        <tr><td>Entropy Reduction</td><td>{entropy_reduction:.2f} bits</td></tr>
                    </table>
                    """

                    # Add suggestions if available
                    if suggestions:
                        feedback += "Suggested next guesses:<br>"
                        feedback += ", ".join(
                            f"{''.join(map(str, s))}" for s in suggestions
                        )
                    else:
                        feedback += "<br>No suggestions available."

                    st.session_state.messages.append(
                        {"role": "assistant", "content": feedback}
                    )

    # Display chat history AFTER processing user input
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # Plot the entropy graph on the sidebar
    if st.session_state.entropy_history:
        st.sidebar.subheader("Entropy Progress")
        st.sidebar.line_chart(
            {"Entropy (bits)": st.session_state.entropy_history},
            x_label="Number of Guesses",
            y_label="Entropy (bits)",
        )
        current_entropy = st.session_state.entropy_history[-1]
        st.sidebar.write(f"**Current Entropy:** {current_entropy:.2f} bits")
    
    if st.session_state.entropy_reduction_history:
        st.sidebar.subheader("Entropy Reduction Progress")
        st.sidebar.line_chart(
            {"Entropy Reduction": st.session_state.entropy_reduction_history},
            x_label="Number of Guesses",
            y_label="Entropy Reduction",
        )
        current_entropy_reduce = st.session_state.entropy_reduction_history[-1]
        st.sidebar.write(f"**Current Entropy Reduction:** {current_entropy_reduce:.2f}")

    # Restart button
    if st.button("Restart Game"):
        st.session_state.game = BullsAndCows()
        st.session_state.messages = []
        st.session_state.entropy_history = [st.session_state.game.calculate_entropy()]
        st.session_state.entropy_reduction_history = [0]
        st.session_state.game_over = False


if __name__ == "__main__":
    main()
