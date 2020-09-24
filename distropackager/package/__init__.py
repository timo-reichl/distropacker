
from configobj import ConfigObj
from pathlib import Path

from distropackager import root_dir
from distropackager.docker import DockerImage
from distropackager.process import ProcessContext


class Package(object):
    def __init__(self, info, build_dir):
        self.info = info
        self.build_dir = build_dir

    def __getattr__(self, item):
        if item in self.info:
            return self.info[item]

        return self.__getattribute__(item)

    def build(self, dependencies, tag=None, force=False):
        docker_image = DockerImage(self)
        docker_image.build(dependencies, tag, force)

        image_name = docker_image.with_tag(docker_image.latest)
        image_volume = f"{self.build_dir}:/{root_dir.name}"

        ProcessContext.execute(
            f"docker run --rm -w /{root_dir.name} -v {image_volume} {image_name} {self.build_command}",
            run_dir=self.build_dir,
            print_stdout=True
        )


class PackageManager(object):
    def __init__(self, ini_path):
        self.ini = ConfigObj(ini_path)

    def get(self, name, build_dir):
        info = dict(self.ini[name])
        base = info.get("base", None)

        if base is not None:
            base_info = dict(self.ini[base])
            base_info.update(info)
            del base_info["base"]

            info = base_info

        return Package(info, build_dir)


package_manager = PackageManager(str(Path(__file__).parent.joinpath("data.ini")))
