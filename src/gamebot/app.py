import random
import math
from itertools import permutations
import streamlit as st

class BullsAndCows:
    """
    A class to implement the Bulls and Cows game.
    Includes functionality for entropy, entropy reduction and next guess suggestions.
    """

    def __init__(self):
        # Initialize the game with digits 0-9 and randomly generate a 4-digit secret number with unique digits.
        self.digits = list(range(10))  # Contains digits from 0-9
        self.secret = random.sample(self.digits, 4)  # Secret number (4 unique digits)
        self.attempts = 0  # Tracks the no of attempts made by the player
        self.possible_combinations = list(permutations(range(10), 4))  # All possible guesses
        self.first_attempt = True  # Flag for the first attempt
    
    # Entropy calculation    
    def calculate_entropy(self):
        """
        Calculate the entropy based on the number of remaining possible combinations.
        
        Entropy formula: H(X) = sum(P(x_i) * log2/(P(x_i)))
        Since all possibilities are equally likely, P(x_i) = 1 / n for all i.
        """
        n = len(self.possible_combinations)  # No. of remaining combinations
        if n == 0:
            return 0  # No combinations left (edge case)
        probabilities = [1 / n] * n  # Uniform probability distribution
        entropy = sum(p * math.log2(1 / p) for p in probabilities)  # Formula
        return entropy

    def entropy_reduction(self, prev_entropy, current_entropy):
        """
        Calculate the reduction in entropy after a guess.
        Args:
            prev_entropy (float): Entropy before the current guess.
            current_entropy (float): Entropy after the current guess.
        Returns:
            float: The difference between previous and current entropy.
        """
        return prev_entropy - current_entropy  

    def get_feedback(self, guess, code=None):
        """
        Provide feedback on the number of bulls and cows for a given guess.
        Args:
            guess (list): The player's guessed number as a list of digits.
            code (list): The actual secret code. Defaults to the generated secret.
        Returns:
            tuple: Number of bulls (correct digit and position) and cows (correct digit, wrong position).
        """
        if code is None:
            code = self.secret  # Use the secret number if no code is provided
        bulls = sum(g == s for g, s in zip(guess, code))  # Correct digit in the correct position
        cows = sum(g == s for g in guess for s in code) - bulls  # Correct digit but in wrong position
        return bulls, cows

    def update_possibilities(self, guess, bulls, cows):
        """
        Update the list of possible combinations based on the feedback from the current guess.
        Args:
            guess (list): The player's guessed number.
            bulls (int): Number of bulls in the guess.
            cows (int): Number of cows in the guess.
        """
        new_possibilities = []
        for combo in self.possible_combinations:
            test_bulls, test_cows = self.get_feedback(guess, combo)
            # Keep combinations that produce the same feedback as the player's guess
            if (test_bulls, test_cows) == (bulls, cows):
                new_possibilities.append(combo)
        self.possible_combinations = new_possibilities  # Update the possibilities

    def suggest_next_guesses(self):
        """
        Suggest up to 10 possible guesses from the remaining combinations.
        Returns:
            list: A list of up to 10 suggested guesses or an empty list if no combinations remain.
        """
        sample_size = min(10, len(self.possible_combinations))  # Limit to 10 suggestions
        return random.sample(self.possible_combinations, sample_size) if self.possible_combinations else []  


def main():
    # Streamlit App setup with page title and icon
    st.set_page_config(
        page_icon="https://cdn-icons-png.flaticon.com/512/6100/6100585.png",
        page_title="Ramya's game bot")
    st.title("Bulls and Cows")
    st.text("In this game, you need to guess a 4-digit number with all unique digits. "
            "I'll give you hints in the form of Bulls and Cows. "
            "A Bull means a correct digit in the correct place, and a Cow means a correct digit in the wrong place. "
            "Let's get started!")

    # Ensure the game state persists across reruns
    if "game" not in st.session_state:
        st.session_state.game = BullsAndCows()  # initialize the game object
    if "messages" not in st.session_state:
        st.session_state.messages = []  # Store chat messages
    if "entropy_history" not in st.session_state:
        st.session_state.entropy_history = [st.session_state.game.calculate_entropy()]  # Track entropy values
    if "entropy_reduction_history" not in st.session_state:
        st.session_state.entropy_reduction_history = [0]  # Track entropy reduction values 
    if "game_over" not in st.session_state:
        st.session_state.game_over = False  # Flag for game over

    game = st.session_state.game

    # Chat input for user's guesses
    if not st.session_state.game_over:
        user_input = st.chat_input("Enter your 4-digit guess")  # Store user input

        if user_input:
            # Append user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})

            # Validate user input ( must be 4 unique digits)
            if (len(user_input) != 4
                or not user_input.isdigit()
                or len(set(user_input)) != 4):
                st.session_state.messages.append(
                    {"role": "assistant",
                     "content": "Invalid guess! Please enter 4 different digits."})
            else:
                # convert input to a list of integers
                guess = [int(x) for x in user_input]
                prev_entropy = st.session_state.entropy_history[-1]  # Previous entropy
                game.attempts += 1  # Increment in attempts
                bulls, cows = game.get_feedback(guess)  # Get feedback on the guess
                game.update_possibilities(guess, bulls, cows)  # Update remaining possibilities

                # Calculate current entropy and entropy reduction
                entropy = game.calculate_entropy()
                entropy_reduction = game.entropy_reduction(prev_entropy, entropy)

                # Append new entropy and entropy reduction to session state
                st.session_state.entropy_history.append(entropy)
                st.session_state.entropy_reduction_history.append(entropy_reduction)
                
                # Check win 
                if bulls == 4:
                    st.session_state.messages.append(
                        {"role": "assistant",
                         "content": f"🎉 Congratulations! You guessed the secret number in {game.attempts} attempts!",})
                    st.session_state.game_over = True
                else:
                    # Display feedback and suggestions with entropy and entropy reduction in a table
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
                            f"{''.join(map(str, s))}" for s in suggestions)
                    else:
                        feedback += "<br>No suggestions available."

                    # Append feedback to chat history
                    st.session_state.messages.append({"role": "assistant", "content": feedback})

    # Display chat history 
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    # Plot entropy graph on the sidebar
    if st.session_state.entropy_history:
        st.sidebar.subheader("Entropy Progress")
        st.sidebar.line_chart(
            {"Entropy (bits)": st.session_state.entropy_history},
            x_label="Number of Guesses",
            y_label="Entropy (bits)")
        current_entropy = st.session_state.entropy_history[-1]
        st.sidebar.write(f"**Current Entropy:** {current_entropy:.2f} bits")
    
    # Plot entropy reduction graph on the sidebar
    if st.session_state.entropy_reduction_history:
        st.sidebar.subheader("Entropy Reduction Progress")
        st.sidebar.line_chart(
            {"Entropy Reduction": st.session_state.entropy_reduction_history},
            x_label="Number of Guesses",
            y_label="Entropy Reduction")
        current_entropy_reduce = st.session_state.entropy_reduction_history[-1]
        st.sidebar.write(f"**Current Entropy Reduction:** {current_entropy_reduce:.2f}")

    # Restart button
    if st.button("Restart Game"):
        st.session_state.game = BullsAndCows()  # Reset the game class
        st.session_state.messages = []  # clear chat history
        st.session_state.entropy_history = [st.session_state.game.calculate_entropy()]  # Reset entropy history
        st.session_state.entropy_reduction_history = [0]  # Reset entropy reduction history
        st.session_state.game_over = False  # Reset game over flag
        st.experimental_rerun()  # Refresh the app


if __name__ == "__main__":
    main()
