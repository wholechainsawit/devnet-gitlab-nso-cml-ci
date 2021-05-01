echo "Make NSO docker images..."
pushd nso-docker
make
popd

# Make customed docker images based on cisco-nso-dev
sh build_ci_image.sh

echo "Set up Gitlab..."
pushd nso_cicd_setup/gitlab/
make
popd
