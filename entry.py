import sys
import subprocess

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        from cli import run_cli
        run_cli()
    else:
        print("Starting Streamlit UI...")
        subprocess.run(["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"])

if __name__ == "__main__":
    main()