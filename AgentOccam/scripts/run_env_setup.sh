BASE_URL="<your_base_url>" # <Change this to your base address>

export SHOPPING="http://${BASE_URL}:7770"
export SHOPPING_ADMIN="http://${BASE_URL}:7780/admin"
export REDDIT="http://${BASE_URL}:9999"
export GITLAB="http://${BASE_URL}:8023"
export MAP="http://${BASE_URL}:3000"
export WIKIPEDIA="http://${BASE_URL}:8888/wikipedia_en_all_maxi_2022-05/A/User:The_other_Kiwix_guy/Landing"
export HOMEPAGE="http://${BASE_URL}:4399"

mkdir -p ./.auth/
python browser_env/auto_login.py