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
        self.possible_combinations = list(
            permutations(range(10), 4)
        )  # All possible guesses

    def calculate_entropy(self):
        n = len(self.possible_combinations)
        if n == 0:
            return 0  # No combinations left (edge case)
        probabilities = [1 / n] * n  # Equal probability for all possibilities
        entropy = sum(
            p * math.log2(1 / p) for p in probabilities
        )  # entropy calculation
        return entropy

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
        Suggest up to 3 guesses from the remaining possibilities.
        Returns:
            list: A list of up to 3 suggested guesses or an empty list.
        """
        if len(self.possible_combinations) >= 3:
            return random.sample(self.possible_combinations, 3)  # Pick 3 random guesses
        return []  # No suggestions if fewer than 2 possibilities


def main():
    # Streamlit App
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
                game.attempts += 1
                bulls, cows = game.get_feedback(guess)
                game.update_possibilities(guess, bulls, cows)

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
                    # Display feedback and suggestions
                    entropy = game.calculate_entropy()
                    suggestions = game.suggest_next_guesses()
                    feedback = (
                        f"Bulls: {bulls}, Cows: {cows}\nEntropy: {entropy:.2f} bits"
                    )
                    if suggestions:
                        feedback += "\nSuggested next guesses:\n"
                        feedback += "\n".join(
                            f"**{''.join(map(str, s))}**" for s in suggestions
                        )
                    else:
                        feedback += "\nNo suggestions available."
                    st.session_state.messages.append(
                        {"role": "assistant", "content": feedback}
                    )

    # Display chat history AFTER processing user input
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Restart button
    if st.button("Restart Game"):
        st.session_state.game = BullsAndCows()
        st.session_state.messages = []
        st.session_state.game_over = False


if __name__ == "__main__":
    main()
