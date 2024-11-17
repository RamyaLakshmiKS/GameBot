import subprocess

def main():
    subprocess.run(["streamlit", "run", "src/bully_bot/app.py"])

if __name__ == "__main__":
    main()