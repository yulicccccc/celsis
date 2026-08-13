# Ready-to-push instructions

Assuming your new repo is already cloned locally:

```powershell
cd C:\path\to\celsis

# Copy the contents of this package into the repo root, then:
git status
git add README.md PRD.md PROJECT_STATE.md AGENTS.md CHANGELOG.md .gitignore MANIFEST.json docs templates
git commit -m "docs: capture Celsis Data Entry V1 product and implementation"
git push
```

If the repo is empty and not yet cloned:

```powershell
git clone https://github.com/yulicccccc/celsis.git
cd celsis
# Copy package contents here
git add .
git commit -m "docs: capture Celsis Data Entry V1 product and implementation"
git push -u origin main
```

Before push, confirm:

```powershell
git status
git ls-files
```

Do not commit production PDFs/WKL files, browser sessions, credentials, or live screenshots.
