NSO_BASE_IMG=$(docker images --filter=reference='cisco-nso-dev' --format "{{.Repository}}:{{.Tag}}" | awk '/cisco-nso-dev/ {print $1; exit}')

echo "Base NSO image: $NSO_BASE_IMG"

docker build -t nso:gitlabci --build-arg BASE_IMG=$NSO_BASE_IMG .
