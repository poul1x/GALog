autoflake -r ./galog --remove-all-unused-imports -i
isort -q ./galog
black -q ./galog
