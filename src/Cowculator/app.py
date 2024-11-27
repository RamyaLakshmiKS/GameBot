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

    def calculate_entropy(self):
        n = len(self.possible_combinations)
        if n == 0:
            return 0  # No combinations left (edge case)
        probabilities = [1 / n] * n  # Equal probability for all possibilities
        entropy = sum(p * math.log2(1 / p) for p in probabilities)  # entropy calculation
        return entropy
    
    def calculate_mutual_information(self, prev_entropy, current_entropy):
        """
        Calculate mutual information as the difference between previous and current entropy.
        Args:
            prev_entropy (float): Entropy before the current guess.
            current_entropy (float): Entropy after the current guess.
        Returns:
            float: Mutual information in bits.
        """
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
        num_suggestions = min(10, len(self.possible_combinations))
        return random.sample(self.possible_combinations, num_suggestions)  # Pick up to 10 random guesses


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
    if "entropy_history" not in st.session_state:
        st.session_state.entropy_history = [st.session_state.game.calculate_entropy()]  # Track entropy values
    if "mutual_info_history" not in st.session_state:
        st.session_state.mutual_info_history = [st.session_state.game.calculate_mutual_information]  # Track mutual information values
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "first_attempt" not in st.session_state:
        st.session_state.first_attempt = True  # Flag to track first attempt
    if "attempts" not in st.session_state:
        st.session_state.attempts = 0  # Initialize attempts
    
    game = st.session_state.game


    # Chat input for user's guesses
    if not st.session_state.game_over:
        user_input = st.chat_input("Enter your 4-digit guess: ")

        if user_input:
            # Append user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Validate user input
            if (len(user_input) != 4 or not user_input.isdigit() or len(set(user_input)) != 4):
                st.session_state.messages.append(
                    {"role": "assistant",
                     "content": "Invalid guess! Please enter 4 different digits.",
                    })
            else:
                # Valid input: Process guess
                guess = [int(x) for x in user_input]
                prev_entropy = st.session_state.entropy_history[-1]  # Get previous entropy
                game.attempts += 1
                
                # Provide feedback
                bulls, cows = game.get_feedback(guess)
                game.update_possibilities(guess, bulls, cows)

                # Calculate and update history
                entropy = game.calculate_entropy()
                mutual_info = game.calculate_mutual_information(prev_entropy, entropy)
                
                # Append entropy and mutual information to session state
                st.session_state.entropy_history.append(entropy)
                st.session_state.mutual_info_history.append(mutual_info)

                # Check win condition
                if bulls == 4:
                    st.session_state.messages.append(
                        {"role": "assistant",
                         "content": f"🎉 Congratulations! You guessed the secret number in {game.attempts} attempts!",
                        })
                    st.session_state.game_over = True
                else:
                    # Display feedback and suggestions
                    suggestions = game.suggest_next_guesses()
                    feedback = (f"Bulls: {bulls}, Cows: {cows}\nEntropy: {entropy:.2f} bits")
                    if suggestions:
                        feedback += "\nSuggested next guesses:\n"
                        for s in suggestions:
                            feedback += f"**{''.join(map(str, s))}**\n"
                    else:
                        feedback += "\nNo suggestions available."
                    st.session_state.messages.append({"role": "assistant", "content": feedback})

                    # If it's the first attempt, show 10 random combinations
                    if not st.session_state.game_over and st.session_state.first_attempt:
                        sample_size = min(10, len(game.possible_combinations))
                        random_combinations = random.sample(game.possible_combinations, sample_size)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": "Here are 10 random combinations you can choose from:"}
                        )
                        button_cols = st.columns(sample_size)
                        for i, combo in enumerate(random_combinations):
                            # Create a clickable button for each combination
                            combo_str = ''.join(map(str, combo))
                            if button_cols[i].button(combo_str, key=f"combo_{i}"):
                                user_input = combo_str
                                st.session_state.messages.append({"role": "user", "content": user_input})
                                st.session_state.first_attempt = False
                                
                                # Set the selected combination as the next guess
                                game.attempts += 1
                                bulls, cows = game.get_feedback(combo)
                                game.update_possibilities(combo, bulls, cows)

                                # Recalculate entropy after the new guess
                                prev_entropy = st.session_state.entropy_history[-1]
                                entropy = game.calculate_entropy()
                                mutual_info = game.calculate_mutual_information(prev_entropy, entropy)

                                # Append entropy and mutual information to session state
                                st.session_state.entropy_history.append(entropy)
                                st.session_state.mutual_info_history.append(mutual_info)
                                
                                # Check if the selected combination wins
                                if bulls == 4:
                                    st.session_state.messages.append(
                                        {"role": "assistant", "content": f"🎉 Congratulations! You guessed the secret number in {game.attempts} attempts!"}
                                    )
                                    st.session_state.game_over = True
                                else:
                                    st.session_state.messages.append(
                                        {"role": "assistant", "content": f"Bulls: {bulls}, Cows: {cows}"}
                                    )

                        # Disable the first attempt flag
                        st.session_state.first_attempt = False
                        
    # Display chat history AFTER processing user input
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Plot the entropy and mutual information graphs on the sidebar
    if st.session_state.entropy_history:
        st.sidebar.subheader("Entropy Chart Progress")
        st.sidebar.line_chart(
            {"Entropy (bits)": st.session_state.entropy_history},
            x_label="Number of Guesses",
            y_label="Entropy (bits)")
        
    if st.session_state.mutual_info_history:
        st.sidebar.subheader("Mutual Information Chart Progress")
        st.sidebar.line_chart(
            {"Mutual Information (bits)": st.session_state.mutual_info_history},
            x_label="Number of Guesses",
            y_label="Mutual Information (bits)")

    # Restart button
    if st.button("Restart Game"):
        st.session_state.game = BullsAndCows()
        st.session_state.messages = []
        st.session_state.entropy_history = [st.session_state.game.calculate_entropy()]
        st.session_state.mutual_info_history = [st.session_state.game.calculate_mutual_information(prev_entropy, st.session_state.entropy_history)]
        st.session_state.game_over = False
        st.session_state.first_attempt = True
        st.session_state.attempts = 0


if __name__ == "__main__":
    main()
