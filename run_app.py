import subprocess

def main():
    subprocess.run(["streamlit", "run", "src/Cowculator/app.py"])

if __name__ == "__main__":
    main()