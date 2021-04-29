echo "Make NSO docker images..."
pushd nso-docker
make
popd

echo "Set up Gitlab..."
pushd nso_cicd_setup/gitlab/
make
popd
