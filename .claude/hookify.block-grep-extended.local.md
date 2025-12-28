---
name: block-grep-extended
enabled: true
event: bash
pattern: grep\s+-E\b
action: block
---

⚠️ **grep -E blocked!**

The `-E` flag doesn't work correctly on macOS systems.

**Use `-e` instead:**
- `grep -e "pattern"` instead of `grep -E "pattern"`

Note: `-e` specifies the pattern to match, while `-E` enables extended regex which has compatibility issues on macOS.
