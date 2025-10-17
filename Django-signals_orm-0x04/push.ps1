# PowerShell script to add, commit, and push changes to Git
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Files
)

if ($Files.Count -eq 0) {
    git add -A .
} else {
    foreach ($file in $Files) {
        git add $file
    }
}

$commitMessage = Read-Host 'Enter the commit message'

git commit -m "$commitMessage"
git push
