mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = true\n\
\n\
" > ~/.streamlit/config.toml