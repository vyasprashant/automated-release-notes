def export_to_file(content, file_path):
    try:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"✅ Release Notes Saved to {file_path}")
    except Exception as e:
        print(f"❌ Error saving release notes: {str(e)}")
        fallback_path = "release_notes.md"
        with open(fallback_path, "w") as f:
            f.write(content)
        print(f"✅ Saved to fallback: {fallback_path}")