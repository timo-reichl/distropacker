
from pathlib import Path

from distropackager import package_root_dir
from distropackager.docker import DockerImage
from distropackager.process import ProcessContext


class Package(object):
    base_name = None
    build_command = None

    def __init__(self, build_dir):
        self.build_dir = Path(build_dir)

    def build(self):
        docker_image = DockerImage(self)
        docker_image.build(docker_image.tag)

        image_name = docker_image.with_tag(docker_image.tag)
        image_volume = f"{self.build_dir}:/{package_root_dir.name}"

        with ProcessContext(
            f"docker run --rm -w /{package_root_dir.name} -v {image_volume} {image_name} {self.build_command}",
            run_dir=self.build_dir,
            print_stdout=True
        ):
            pass


class ArchPackage(Package):
    base_name = "arch"
    build_command = "makepkg -s"


class ManjaroPackage(ArchPackage):
    pass  # need manjaro repos?


class DebianPackage(Package):
    base_name = "debian"
    build_command = "dpkg-buildpackage -us -uc"


class UbuntuPackage(DebianPackage):
    base_name = "ubuntu"


class FedoraPackage(Package):
    base_name = "fedora"


class GentooPackage(Package):
    base_name = "gentoo"


# quick test
test_package = ArchPackage(package_root_dir.parent.joinpath("docker", "sample_package", "arch"))
test_package.build()
