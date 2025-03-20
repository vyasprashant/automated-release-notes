import sys
import subprocess
import yaml

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        from cli import generate_release_notes
        # Load config.yaml
        try:
            with open("/app/config.yaml", "r") as f:
                cfg = yaml.safe_load(f)
            if not cfg:
                raise ValueError("config.yaml is empty")
        except FileNotFoundError:
            print("Error: config.yaml not found. Please add it and rebuild the image.")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML in config.yaml: {str(e)}. Please fix and rebuild the image.")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {str(e)}. Please fix config.yaml and rebuild the image.")
            sys.exit(1)

        generate_release_notes(cfg)
    else:
        print("Starting Streamlit UI...")
        subprocess.run(["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"])

if __name__ == "__main__":
    main()