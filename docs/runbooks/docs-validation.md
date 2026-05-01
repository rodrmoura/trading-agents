# Documentation Validation Runbook

Use this runbook before committing documentation or scaffold changes.

## Checks

```powershell
git diff --check
rg -n '[^\x00-\x7F]' .github docs apps packages prompts examples PROJECT-GUIDE.md TODO.md DOCS-GOVERNANCE.md CODING-STANDARDS.md SECURITY.md DEPLOY.md CONTRIBUTING.md PROJECT-CHANGELOG.md
```

If a touched file intentionally needs non-ASCII text, document why in the change summary.

## Status Check

```powershell
git status --short
```

Confirm staged or committed files match the intended documentation scope.
