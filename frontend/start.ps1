$ErrorActionPreference = 'Stop'

$npmCommand = Get-Command npm -ErrorAction SilentlyContinue
if ($npmCommand) {
    npm install
    if ($LASTEXITCODE -ne 0) { throw 'npm install failed.' }
    npm run dev
    exit $LASTEXITCODE
}

# Optional fallback for this workspace, where Node is provided through the
# Python nodejs-wheel package because the system Node installer is unavailable.
$nodePackage = python -c "import importlib.util; print(importlib.util.find_spec('nodejs_wheel').submodule_search_locations[0])" 2>$null
if ($LASTEXITCODE -ne 0 -or -not $nodePackage) {
    throw 'Install Node.js 20.19+ (or 22.12+) and npm, then run npm install and npm run dev.'
}
$node = Join-Path $nodePackage 'node.exe'
$npmCli = Join-Path $nodePackage 'lib\node_modules\npm\bin\npm-cli.js'
& $node $npmCli install
if ($LASTEXITCODE -ne 0) { throw 'npm install failed.' }
& $node $npmCli run dev
exit $LASTEXITCODE
