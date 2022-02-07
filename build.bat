del /f "Japanese Card Randomizer.ankiaddon"
if not exist "included_fonts" ( 
    mkdir "included_fonts"
)
pwsh -Command "& {Compress-Archive -LiteralPath included_fonts, __init__.py, config.json, config.md, manifest.json, README.md -DestinationPath Japanese-Card-Randomizer.zip -Force}"
rename Japanese-Card-Randomizer.zip "Japanese Card Randomizer.ankiaddon"