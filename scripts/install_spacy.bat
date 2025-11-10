@echo off
echo Installing spaCy for enhanced keyword extraction...
echo.

pip install spacy
python -m spacy download en_core_web_sm

echo.
echo Done! Enhanced keyword extraction with Named Entity Recognition is now available.
echo.
pause
